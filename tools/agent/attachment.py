"""附件侦察：只读、结构化的文件分析。

安全边界：
  - 只解析字节，**不执行**附件里的任何脚本或可执行文件；
  - 不调用 binwalk/exiftool/strings 等外部命令，只用标准库与 `agent.carve`；
  - 上传副本写入独立随机目录，文件名只保留最后一段，防止路径穿越。

输出给前端的是结构化结果：类型、内嵌雕刻、自动解码、字符串、结构异常。
`analyze_probe()` 仍返回旧的文本格式，供 hint/CLI 继续复用。
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import re
import tempfile
import uuid
import zipfile
from pathlib import Path
from urllib.parse import unquote

try:                                    # 允许作为包导入，也允许脚本方式运行
    from . import carve as _carve
    from . import recon as _recon
except ImportError:                     # pragma: no cover
    from agent import carve as _carve    # type: ignore
    from agent import recon as _recon    # type: ignore

MAX_CARVE = 20
MAX_DECODED = 10
MAX_ZIP_ENTRIES = 30
MAX_CHUNKS = 40
MAX_DECODED_CHARS = 800

# 扩展名与真实类型不一致时给出提示（只做提示，不改变文件）
EXT_KIND = {
    ".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".gif": "GIF",
    ".bmp": "BMP", ".webp": "RIFF", ".avi": "RIFF", ".wav": "RIFF",
    ".zip": "ZIP", ".docx": "ZIP", ".xlsx": "ZIP", ".apk": "ZIP",
    ".jar": "ZIP", ".whl": "ZIP", ".rar": "RAR", ".7z": "7Z",
    ".gz": "GZIP", ".tgz": "GZIP", ".bz2": "BZIP2", ".xz": "XZ",
    ".pdf": "PDF", ".elf": "ELF", ".exe": "PE", ".dll": "PE",
    ".mp3": "MP3", ".mp4": "MP4", ".ogg": "OGG", ".flac": "FLAC",
}

EXECUTABLE_EXT = {
    ".exe", ".dll", ".scr", ".com", ".bat", ".cmd", ".ps1", ".vbs",
    ".js", ".jse", ".wsf", ".msi", ".sh", ".bash", ".py", ".pl", ".rb",
    ".jar", ".elf", ".bin",
}

_PAD_WORDS = re.compile(r"(JUNK|PAD|AAAA|0000|XXXX)+", re.I)
_B64 = re.compile(r"^[A-Za-z0-9+/]{8,}={0,2}$")
_HEX = re.compile(r"^[0-9a-fA-F]{16,}$")


# ---------------------------------------------------------------- 文本/类型
def _text_info(data: bytes) -> tuple[bool, str]:
    """返回 (是否像文本, 预览)。二进制文件不应被误判为文本。"""
    sample = data[:4000]
    if not sample:
        return False, ""
    try:
        text = sample.decode("utf-8")
    except UnicodeDecodeError:
        text = sample.decode("utf-8", "replace")
    bad = text.count("\ufffd")
    if bad > max(3, len(text) * 0.01):
        return False, ""
    printable = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
    if not text or printable / len(text) < 0.95:
        return False, ""
    preview = text[:300].replace("\n", " ⏎ ")
    return True, preview


def _magic_kind(data: bytes) -> str | None:
    head = data[:32]
    for magic, desc in _recon.MAGIC:
        if len(magic) <= len(head) and head.startswith(magic):
            return desc
    return None


def _mismatch(ext: str, kind: str | None) -> str:
    if not ext or not kind:
        return ""
    want = EXT_KIND.get(ext)
    if not want:
        return ""
    if want.lower() in kind.lower():
        return ""
    return f"扩展名 {ext} 与真实内容「{kind}」不符 —— 可能被改过"


def _is_executable_name(name: str) -> bool:
    return Path(str(name)).suffix.lower() in EXECUTABLE_EXT


# ---------------------------------------------------------------- 解码
def _readable(t: str) -> bool:
    if not t or len(t) < 4 or "\ufffd" in t:
        return False
    for ch in t:
        if ord(ch) < 32 and ch not in "\t\n\r":
            return False
        if ord(ch) == 127:
            return False
    allowed = " \t\n\r_-.:/{}[]()@#$%^&*+=,;'\"<>|\\!?~`"
    ratio = sum(
        1 for ch in t
        if ch.isalnum() or "\u4e00" <= ch <= "\u9fff" or ch in allowed
    ) / len(t)
    if ratio < 0.9:
        return False
    if len(t) >= 12:
        head = t[:8]
        reps = t.count(head)
        if reps >= 2 and reps * len(head) >= len(t) * 0.6:
            return False
    return True


def _meaningful(t: str) -> bool:
    return sum(1 for ch in t if ch.isalpha() or "\u4e00" <= ch <= "\u9fff") >= 3


def _try_decode(core: str):
    """按 base64 / hex / URL 尝试解码；返回 (method, decoded) 或 None。"""
    if _B64.fullmatch(core):
        try:
            pad = core + "=" * (-len(core) % 4)
            dec = base64.b64decode(pad, validate=False).decode("utf-8")
            if dec != core:
                return "base64", dec
        except Exception:  # noqa: BLE001
            pass
    if len(core) % 2 == 0 and _HEX.fullmatch(core):
        try:
            dec = binascii.unhexlify(core).decode("utf-8")
            if dec != core:
                return "hex", dec
        except Exception:  # noqa: BLE001
            pass
    if "%" in core:
        try:
            dec = unquote(core)
            if dec != core:
                return "url", dec
        except Exception:  # noqa: BLE001
            pass
    return None


def decode_candidates(strings: list[str]) -> list[dict]:
    """从字符串里挑 base64/hex/url 并解码，返回结构化结果。

    假线索比没线索更糟，所以沿用 recon 的严格判定：控制字符、
    U+FFFD、低可读占比、大段重复填充一律丢弃。
    """
    out: list[dict] = []
    seen: set[str] = set()
    for raw in strings:
        s = str(raw).strip()
        if not s:
            continue
        core = s.split(":", 1)[1].strip() if s.count(":") == 1 else s
        if not core or _PAD_WORDS.fullmatch(core):
            continue
        got = _try_decode(core)
        if not got:
            continue
        method, dec = got
        if not _readable(dec) or not _meaningful(dec) or dec in seen:
            continue
        seen.add(dec)
        trunc = len(dec) > MAX_DECODED_CHARS
        out.append({
            "method": method,
            "encoded": core[:MAX_DECODED_CHARS],
            "decoded": dec[:MAX_DECODED_CHARS],
            "truncated": trunc,
        })
        if len(out) >= MAX_DECODED:
            break
    return out


# ---------------------------------------------------------------- 结构
def _zip_structure(path: Path) -> tuple[dict | None, list[str]]:
    anomalies: list[str] = []
    try:
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            entries = [{
                "name": i.filename,
                "size": i.file_size,
                "compressed": i.compress_size,
                "encrypted": bool(i.flag_bits & 0x1),
            } for i in infos[:MAX_ZIP_ENTRIES]]
            encrypted = any(i.flag_bits & 0x1 for i in infos)
            if encrypted:
                anomalies.append("ZIP 含加密条目，需要密码才能解压")
            return {
                "count": len(infos),
                "entries": entries,
                "truncated": len(infos) > MAX_ZIP_ENTRIES,
                "encrypted": encrypted,
            }, anomalies
    except zipfile.BadZipFile:
        anomalies.append("ZIP 结构损坏或不是有效 ZIP")
    except Exception as e:  # noqa: BLE001
        anomalies.append(f"ZIP 解析失败: {type(e).__name__}")
    return None, anomalies


def _structures(path: Path, data: bytes, kind: str | None) -> tuple[dict, list[str]]:
    out: dict = {}
    anomalies: list[str] = []

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        pi = _carve.png_info(path)
        out["png"] = {
            "width": pi.get("width"),
            "height": pi.get("height"),
            "chunks": [
                {k: c.get(k) for k in ("type", "len", "offset", "crc_ok")}
                for c in pi.get("chunks", [])[:MAX_CHUNKS]
            ],
            "truncated": len(pi.get("chunks", [])) > MAX_CHUNKS,
        }
        anomalies.extend(pi.get("anomalies", []))

    if data.startswith(b"RIFF"):
        wi = _carve.wav_info(path)
        if wi.get("sample_rate") or wi.get("chunks"):
            out["wav"] = {
                "format": wi.get("format"),
                "channels": wi.get("channels"),
                "sample_rate": wi.get("sample_rate"),
                "chunks": wi.get("chunks", [])[:MAX_CHUNKS],
                "tail_text": wi.get("tail_text", ""),
            }
        anomalies.extend(wi.get("anomalies", []))

    if kind and "ZIP" in kind:
        zs, za = _zip_structure(path)
        if zs:
            out["zip"] = zs
        anomalies.extend(za)

    return out, anomalies


# ---------------------------------------------------------------- 落盘
def safe_filename(raw: str) -> str:
    """只保留最后一段文件名，去掉控制字符与 Windows 非法字符。"""
    s = str(raw or "").strip().replace("\\", "/").split("/")[-1]
    s = unquote(s)
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    s = re.sub(r'[<>:"|?*]', "_", s).strip(" .")
    if not s or s in (".", ".."):
        return "attachment.bin"
    p = Path(s)
    stem = (p.stem or "attachment")[:80]
    ext = p.suffix[:16]
    return f"{stem}{ext}"


def save_attachment(data: bytes, name: str, root: Path) -> dict:
    """把上传内容复制到独立随机目录，返回保存位置与哈希。"""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    folder = root / uuid.uuid4().hex
    folder.mkdir(parents=False, exist_ok=False)
    safe = safe_filename(name)
    target = (folder / f"upload_{safe}").resolve()
    try:
        target.relative_to(folder.resolve())
    except ValueError as e:  # pragma: no cover  # safe_filename 已剥离目录
        raise ValueError("附件路径越界") from e
    target.write_bytes(data)
    return {
        "name": safe,
        "original_name": str(name or ""),
        "saved": str(target),
        "dir": str(folder),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


# ---------------------------------------------------------------- 主入口
def analyze_path(path: Path, name: str | None = None) -> dict:
    """分析一个已存在的文件；不写文件、不执行程序、不调用外部命令。"""
    path = Path(path)
    data = path.read_bytes()
    display = str(name or path.name)
    sha = hashlib.sha256(data).hexdigest()

    kind = _magic_kind(data)
    is_text, preview = _text_info(data)
    if not kind and is_text:
        kind = "UTF-8 文本"

    ext = Path(display).suffix.lower()
    mismatch = _mismatch(ext, kind)

    carved = _carve.carve_files(data)["items"]
    embedded = [
        {
            "type": i.get("type"),
            "offset": i.get("offset"),
            "offset_hex": i.get("offset_hex"),
            "size": i.get("size"),
        }
        for i in carved if (i.get("offset") or 0) > 0
    ][:MAX_CARVE]

    structures, struct_anomalies = _structures(path, data, kind)
    anomalies: list[str] = []
    for msg in [mismatch, *struct_anomalies]:
        if msg and msg not in anomalies:
            anomalies.append(msg)

    strings = _recon._grab_strings(data)
    decoded = decode_candidates(strings)

    warnings: list[str] = []
    if _is_executable_name(display):
        warnings.append("该扩展名属于可执行/脚本类型；本工具只读取字节，不会运行它。")

    return {
        "schema_version": 1,
        "file": {
            "name": display,
            "size": len(data),
            "sha256": sha,
            "ext": ext,
        },
        "type": {
            "kind": kind or "未知（可能是纯文本或未知格式）",
            "detected": bool(kind),
            "is_text": is_text,
            "preview": preview,
            "extension": ext,
            "extension_mismatch": bool(mismatch),
        },
        "carve": embedded,
        "structures": structures,
        "anomalies": anomalies,
        "decoded": decoded,
        "strings": strings,
        "warnings": warnings,
        "executed": False,
        "execution_note": "只读分析：未执行附件中的任何脚本或可执行文件。",
    }


def analyze_bytes(data: bytes, name: str = "attachment.bin") -> dict:
    """分析内存中的字节；内部临时文件只用于解析结构。"""
    with tempfile.TemporaryDirectory(prefix="kb-attach-") as td:
        p = Path(td) / "upload.bin"
        p.write_bytes(data)
        return analyze_path(p, name=name)


def analyze_upload(data: bytes, name: str, root: Path) -> dict:
    """复制到隔离目录后分析，结果里带保存位置。"""
    saved = save_attachment(data, name, root)
    report = analyze_bytes(data, name=saved["name"])
    report["file"].update({
        "original_name": saved["original_name"],
        "saved": saved["saved"],
        "dir": saved["dir"],
        "sha256": saved["sha256"],
    })
    report["storage"] = {
        "isolated": True,
        "dir": saved["dir"],
        "saved": saved["saved"],
    }
    return report


# ---------------------------------------------------------------- 文本兼容
def analyze_probe(path: str, data: bytes | None = None) -> tuple[bool, str]:
    """给 hint/CLI 的兼容层：把结构化结果渲染成原来的可读文本。"""
    p = Path(path)
    report = analyze_path(p) if data is None else analyze_bytes(data, p.name)
    lines = [
        f"文件: {report['file']['name']}",
        f"大小: {report['file']['size']} 字节 "
        f"({report['file']['size'] / 1024:.1f} KB)",
        f"SHA256: {report['file']['sha256']}",
        f"类型判定: {report['type']['kind']}",
    ]
    if report["type"]["is_text"]:
        lines.append(f"看起来是 UTF-8 文本，开头: {report['type']['preview']}")
    for a in report["anomalies"]:
        lines.append(f"  ⚠ {a}")
    if report["carve"]:
        lines.append("内嵌文件（雕刻结果）:")
        for i in report["carve"]:
            sz = f"{i['size']} 字节" if i["size"] else "大小未知"
            lines.append(f"  {i['offset_hex']} 偏移: {i['type']} ({sz})")
    if report["decoded"]:
        lines.append("自动解码结果（工具已解好，直接使用，不要再自己猜）:")
        for d in report["decoded"]:
            lines.append(f"  {d['encoded']}  --{d['method']}-->  {d['decoded']}")
    if report["strings"]:
        lines.append(f"可读字符串（前 {len(report['strings'])} 条，含关键词优先）:")
        lines.extend(f"  {s}" for s in report["strings"])
    return True, "\n".join(lines)[:_recon.MAX_OUT]

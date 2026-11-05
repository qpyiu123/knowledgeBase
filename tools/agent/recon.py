"""文件侦察工具：让 agent 在题面没信息时能从附件里找线索。

这是针对「题面全是废话」这类真实题型的核心能力。
设计原则：
  1. 单次调用只做一类事，返回**可解读的线索**而不是原始 dump
  2. 输出必须做长度预算，避免一次把上下文撑爆
  3. 全部只读，绝不执行附件里的任何东西
  4. 子进程调用有超时，防止卡死

工具清单：
  list_files(dir)        列出目录里的文件（含大小/类型判断）
  probe_file(path)       自动侦察：file → 魔数 → strings 摘要 → 内嵌文件
  run_tool(tool, path,args)  白名单工具调用（binwalk/exiftool/steghide/...）
"""
from __future__ import annotations

import os
import shutil
import zipfile
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 允许 agent 侦察的目录（只读）
SCAN_ROOTS = [ROOT / "work", ROOT / "attachments", ROOT / "kb"]

MAX_LIST = 200
MAX_STRINGS = 60
MAX_OUT = 4000
TIMEOUT = 30

# 白名单工具：名称 -> [候选命令前缀...]，按顺序找第一个存在的
#
# 便携工具集的位置**不写死**：按优先级依次探测，哪个存在用哪个。
#   1. 环境变量 KB_TOOLS_DIR（想放到别处时设这个）
#   2. <项目根>/tools/_bin          （项目自带）
#   3. <项目根的上一级>/tools        （可选同级工具集）
def _find_bin_dir() -> Path:
    """找一个**确实含有便携工具**的目录。

    注意不能只看目录存在：项目里有个空的 tools/_bin（早期预留），
    如果它被优先选中，exiftool/foremost 就找不到，可用工具会变少。
    """
    probe = ("exiftool-13.27_64", "foremost", "WinRAR")

    cands = []
    env = os.environ.get("KB_TOOLS_DIR")
    if env:
        cands.append(Path(env))
    cands.append(ROOT / "tools" / "_bin")
    cands.append(ROOT.parent / "tools")

    for c in cands:
        if c.is_dir() and any((c / p).exists() for p in probe):
            return c
    for c in cands:
        if c.is_dir():
            return c
    return ROOT / "tools" / "_bin"


BIN = _find_bin_dir()
TOOL_CMDS: dict[str, list[list[str]]] = {
    "file": [["file"]],
    "binwalk": [[sys.executable, str(BIN / "binwalk-2.3.1" / "src" / "scripts" / "binwalk")]],
    "strings": [["strings"]],
    "exiftool": [[str(BIN / "exiftool-13.27_64" / "exiftool.exe")],
                 [str(BIN / "exiftool-13.27_64" / "exiftool(-k).exe"), "-k"]],
    "foremost": [[str(BIN / "foremost" / "foremost.exe")]],
    "pngcheck": [["pngcheck"]],
    "zsteg": [["zsteg"]],
    "steghide": [["steghide"]],
    # 注意：WinRAR.exe 是 GUI 程序，命令行调用会挂起，不能用。
    # ZIP 统一走 extract_zip（纯 Python，见 carve.py）。
    "unzip": [["unzip"]],
    "tar": [["tar"]],
}

# 参数模板（{path} {outdir} 会被替换）
TOOL_ARGS: dict[str, list[list[str]]] = {
    "file": [["{path}"]],
    "binwalk": [["{path}"], ["-e", "--run-as=root", "--directory={outdir}", "{path}"],
                ["-A", "{path}"], ["-E", "{path}"]],
    "strings": [["-n", "6", "{path}"], ["{path}"]],
    "exiftool": [["-S", "-a", "-G1", "{path}"], ["-S", "{path}"]],
    "foremost": [["-q", "-i", "{path}", "-o", "{outdir}"], ["-i", "{path}"]],
    "pngcheck": [["-vt", "{path}"]],
    "zsteg": [["-a", "{path}"]],
    "steghide": [["info", "{path}"]],
    "7z": [["{path}"]],
    "unzip": [["-l", "{path}"], ["-o", "{path}", "-d", "{outdir}"]],
    "tar": [["-tf", "{path}"]],
}

TOOL_DESC = {
    "file": "识别文件真实类型",
    "binwalk": "分析内嵌文件/固件结构（argset=1 额外尝试解包）",
    "strings": "提取可打印字符串",
    "exiftool": "读取全部元数据（EXIF/XMP/文档属性）",
    "foremost": "文件雕刻恢复（argset=1 输出到 _probe）",
    "pngcheck": "PNG 结构校验",
    "zsteg": "PNG/BMP LSB 隐写检测",
    "steghide": "JPEG/WAV/BMP steghide 隐写信息",
    "7z": "列出压缩包内容（含 rar/7z）",
    "unzip": "列出/解压 ZIP（argset=1 解压到 _probe）",
    "tar": "列出 tar 内容",
}

# 常用别名，方便模型直接说
_ALIAS = {"exif": "exiftool", "magic": "file", "identify": "file",
          "rar": "7z", "zip": "unzip", "unrar": "7z"}


# 本机没装这些命令时给 agent 的替代建议（对应纯 Python 实现，见 carve.py）
PYTHON_FALLBACK = {
    "file": "用 probe_file 的「类型判定」即可",
    "binwalk": "用 probe_file 的「内嵌文件（雕刻结果）」，再 extract_embedded 导出",
    "zsteg": "用 probe_file 的「可疑字符串」+ PNG chunk 异常",
    "exiftool": "用 probe_file 的头部字节与文本块",
    "unzip": "用 extract_zip",
    "7z": "用 extract_zip（只支持 ZIP）",
    "foremost": "用 probe_file 的雕刻结果 + extract_embedded",
    "pngcheck": "probe_file 已做 PNG chunk 与 CRC 校验",
}

# 常见文件头的魔数（自己判，不依赖 file 命令）
MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "PNG 图片"),
    (b"\xff\xd8\xff", "JPEG 图片"),
    (b"GIF8", "GIF 图片"),
    (b"BM", "BMP 图片"),
    (b"RIFF", "RIFF 容器（WAV/AVI/WebP）"),
    (b"PK\x03\x04", "ZIP 压缩包（或 docx/xlsx/apk/jar）"),
    (b"Rar!\x1a\x07", "RAR 压缩包"),
    (b"7z\xbc\xaf\x27\x1c", "7z 压缩包"),
    (b"\x1f\x8b", "gzip"),
    (b"BZh", "bzip2"),
    (b"\xfd7zXZ", "xz"),
    (b"%PDF", "PDF 文档"),
    (b"\x7fELF", "ELF 可执行（Linux）"),
    (b"MZ", "PE 可执行（Windows）"),
    (b"\xca\xfe\xba\xbe", "Java class / Mach-O fat"),
    (b"dex\n", "Android DEX"),
    (b"OggS", "Ogg 音频"),
    (b"fLaC", "FLAC 音频"),
    (b"ID3", "MP3 音频"),
    (b"RIFF....WAVE", "WAV 音频"),
    (b"\x1aE\xdf\xa3", "Matroska/WebM 视频"),
    (b"\x00\x00\x00\x18ftyp", "MP4 视频"),
    (b"SQLite format 3", "SQLite 数据库"),
    (b"-----BEGIN", "PEM 密钥/证书"),
]


def _hx(b: bytes, n: int = 16) -> str:
    return " ".join(f"{c:02x}" for c in b[:n])


def _within(p: Path, roots: list[Path]) -> bool:
    rp = p.resolve()
    for r in roots:
        try:
            rp.relative_to(r.resolve())
            return True
        except ValueError:
            continue
    return False


def _resolve(path: str) -> Path | None:
    if not path:
        return None
    raw = Path(str(path).strip().strip('"').strip("'"))
    parts = raw.parts
    if len(parts) > 1 and parts[0].lower() == "work":
        raw = Path(*parts[1:])
    for base in (ROOT, ROOT / "work"):
        cand = (raw if raw.is_absolute() else base / raw).resolve()
        if cand.exists() and _within(cand, SCAN_ROOTS):
            return cand
    cand = (ROOT / raw).resolve()
    return cand if _within(cand, SCAN_ROOTS) else None


# ---------------------------------------------------------------- 工具 1
def list_files(directory: str = "work") -> tuple[bool, str]:
    d = _resolve(directory)
    if d is None:
        return False, f"路径越界或不存在: {directory}"
    if not d.is_dir():
        return False, f"不是目录: {directory}"

    entries = sorted(d.iterdir(), key=lambda p: (p.is_dir(), p.name))[:MAX_LIST]
    if not entries:
        return True, f"{d} 是空的。"

    lines = [f"目录 {d}（{len(entries)} 项）："]
    for p in entries:
        if p.is_dir():
            n = sum(1 for _ in p.rglob("*"))
            lines.append(f"  [DIR ] {p.name}/  ({n} 个文件)")
        else:
            size = p.stat().st_size
            hint = ""
            try:
                head = p.read_bytes()[:16]
                for magic, desc in MAGIC:
                    if len(magic) <= len(head) and head.startswith(magic):
                        hint = f"  <- {desc}"
                        break
                if not hint and p.suffix:
                    hint = f"  ({p.suffix})"
            except Exception:
                pass
            lines.append(f"  [FILE] {p.name}  {size} 字节{hint}")
    return True, "\n".join(lines)


# ---------------------------------------------------------------- 工具 2
def probe_file(path: str) -> tuple[bool, str]:
    """自动侦察一个文件：类型 → 魔数 → 大小 → 字符串摘要 → 内嵌文件线索。"""
    f = _resolve(path)
    if f is None:
        return False, f"路径越界或不存在: {path}"
    if not f.is_file():
        return False, f"不是文件: {path}"

    size = f.stat().st_size
    data = f.read_bytes()
    head = data[:32]
    tail = data[-32:] if len(data) > 32 else b""

    out = [f"文件: {f.name}", f"大小: {size} 字节 ({size/1024:.1f} KB)"]
    out.append(f"头部 16 字节: {_hx(head)}")
    out.append(f"尾部 16 字节: {_hx(tail[-16:])}")

    # 魔数判定
    kind = None
    for magic, desc in MAGIC:
        if len(magic) <= len(head) and head.startswith(magic):
            kind = desc
            break
    # 扩展名与魔数是否一致
    ext = f.suffix.lower()
    ext_map = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".gif": "GIF",
               ".zip": "ZIP", ".rar": "RAR", ".7z": "7z", ".pdf": "PDF",
               ".elf": "ELF", ".exe": "PE", ".wav": "WAV", ".mp3": "MP3"}
    out.append(f"类型判定: {kind or '未知（可能是纯文本或未知格式）'}")
    if kind and ext in ext_map and ext_map[ext].lower() not in kind.lower():
        out.append(f"  ⚠ 扩展名是 {ext} 但内容是 {kind} —— 扩展名可能被改过")

    # 是否纯文本
    try:
        text = data.decode("utf-8")
        printable = sum(1 for c in text[:2000] if c.isprintable() or c in "\r\n\t")
        if printable / max(1, len(text[:2000])) > 0.95:
            preview = text[:300].replace("\n", " ⏎ ")
            out.append(f"看起来是 UTF-8 文本，开头: {preview}")
    except UnicodeDecodeError:
        pass

    # 内嵌文件线索：用雕刻器精确扫描（比简单 find 可靠）
    try:
        from agent import carve as _carve
    except Exception:  # noqa: BLE001
        _carve = None
    if _carve is not None:
        cr = _carve.carve_files(data)
        items = [i for i in cr["items"] if i["offset"] > 0]
        if items:
            out.append("内嵌文件（雕刻结果）:")
            for i in items[:8]:
                sz = f"{i['size']} 字节" if i["size"] else "大小未知"
                out.append(f"  {i['offset_hex']} 偏移: {i['type']} ({sz})")
            out.append("  → 可用 extract_embedded 导出后继续分析")

    # 按格式做深度解析
    if _carve is not None:
        name_l = f.name.lower()
        if kind and "PNG" in kind:
            pi = _carve.png_info(f)
            out.append(f"PNG 结构: {pi.get('width')}x{pi.get('height')}, "
                       f"{len(pi.get('chunks', []))} 个 chunk")
            for a in pi.get("anomalies", [])[:6]:
                out.append(f"  ⚠ {a}")
        elif kind and "RIFF" in kind:
            wi = _carve.wav_info(f)
            if wi.get("sample_rate"):
                out.append(f"WAV: {wi['sample_rate']}Hz, {wi.get('channels')} 声道")
            for a in wi.get("anomalies", [])[:6]:
                out.append(f"  ⚠ {a}")
            if wi.get("tail_text"):
                out.append(f"  尾部可读文本: {wi['tail_text'][:200]}")
        elif kind and "ZIP" in kind:
            try:
                with zipfile.ZipFile(f) as z:
                    ents = z.infolist()[:15]
                    out.append(f"ZIP 内容（{len(z.infolist())} 项）:")
                    for e in ents:
                        enc = " [加密]" if e.flag_bits & 0x1 else ""
                        out.append(f"  {e.filename}  {e.file_size} 字节{enc}")
                    out.append("  → 可用 extract_zip 解压")
            except Exception as e:  # noqa: BLE001
                out.append(f"  ZIP 解析失败: {e}")

    # 可读字符串：除英文外，把疑似 base64/hex 的串**自动解码后**一起给出。
    # 这一步很关键：小模型看到 base64 常常直接"猜"解码结果，
    # 实测它把 flag{mult1_st4g3_st3g0} 编成了 flag{mult1_s4g3_s3g0}。
    # 与其指望模型自己算对，不如由工具算好摆在那里。
    strs = _grab_strings(data)
    decoded = _auto_decode_interesting(strs)
    if decoded:
        out.append("自动解码结果（工具已解好，直接使用，不要再自己猜）:")
        out.extend(f"  {d}" for d in decoded)
    if strs:
        out.append(f"可读字符串（前 {len(strs)} 条，含关键词优先）:")
        out.extend(f"  {s}" for s in strs[:MAX_STRINGS])

    txt = "\n".join(out)
    return True, txt[:MAX_OUT]


def _auto_decode_interesting(strs: list[str]) -> list[str]:
    """从字符串里挑出 base64 / hex 并尝试解码，返回可读结果。

    只保留"解码后明显是文本"的（U+FFFD 少、可打印比例高），
    并且要求解码结果与原始串不同，避免噪声。
    """
    import base64
    import binascii
    import re

    out: list[str] = []
    seen: set[str] = set()
    val = re.compile(r"^[A-Za-z0-9+/]{8,}={0,2}$")
    hexv = re.compile(r"^[0-9a-fA-F]{16,}$")

    def good(t: str) -> bool:
        """判断解码结果"像不像有意义的内容"。

        踩过的坑：JUNKJUNKJUNK... 全是合法 base64 字母表字符，
        解出来是 %CJ%CJ... 这种控制字符乱码，但旧逻辑只检查
        "是否可打印"就放行了，结果模型信了这个假线索、
        完全忽略了旁边真正的 ZIP/GZIP。

        假线索比没线索更糟，所以这里要严格：
        - 不能有控制字符
        - 可读字符（字母/数字/中文/常见标点）占比要高
        - 不能是大段重复模式
        """
        if not t or len(t) < 4:
            return False
        if "\ufffd" in t:
            return False
        # 控制字符一律拒绝（除了 \t \n \r）
        for ch in t:
            if ord(ch) < 32 and ch not in "\t\n\r":
                return False
            if ord(ch) == 127:
                return False

        # 可读占比
        def readable(ch: str) -> bool:
            return (ch.isalnum() or "\u4e00" <= ch <= "\u9fff"
                    or ch in " \t\n\r_-.:/{}[]()@#$%^&*+=,;'\"<>|\\!?~`")

        ratio = sum(1 for ch in t if readable(ch)) / len(t)
        if ratio < 0.9:
            return False

        # 大段重复（如 JUNKJUNKJUNK）说明是填充数据，不是有效编码。
        # 注意必须重复至少两次：否则 12~13 字符的正常结果会被误杀。
        if len(t) >= 12:
            head = t[:8]
            reps = t.count(head)
            if reps >= 2 and reps * len(head) >= len(t) * 0.6:
                return False
        return True

    # base64 解码后应当"看得懂"——至少含字母或中文
    def meaningful(t: str) -> bool:
        letters = sum(1 for ch in t if ch.isalpha() or "\u4e00" <= ch <= "\u9fff")
        return letters >= 3

    for s in strs:
        s = s.strip()
        cand = None
        # 形如 TAIL2:xxxx / FLAG_B64:xxxx —— 取冒号后面的部分
        core = s.split(":", 1)[1] if ":" in s and s.count(":") == 1 else s
        core = core.strip()
        # 明确是填充词的串不要尝试（JUNK/PAD/AAAA 一类）
        if re.fullmatch(r"(JUNK|PAD|AAAA|0000|XXXX)+", core, re.I):
            continue
        if val.match(core):
            try:
                pad = core + "=" * (-len(core) % 4)
                dec = base64.b64decode(pad, validate=False).decode("utf-8")
                if good(dec) and meaningful(dec) and dec not in seen:
                    seen.add(dec)
                    cand = f"{core}  --base64-->  {dec}"
            except Exception:  # noqa: BLE001
                pass
        if cand is None and hexv.match(core):
            try:
                dec = binascii.unhexlify(core).decode("utf-8")
                if good(dec) and meaningful(dec) and dec not in seen:
                    seen.add(dec)
                    cand = f"{core}  --hex-->  {dec}"
            except Exception:  # noqa: BLE001
                pass
        if cand:
            out.append(cand)
        if len(out) >= 10:
            break
    return out


def _grab_strings(data: bytes, minlen: int = 6) -> list[str]:
    """从二进制里捞可打印字符串，关键词优先排序。"""
    import re
    pat = re.compile(rb"[\x20-\x7e]{%d,}" % minlen)
    raw = [m.group().decode("ascii", "ignore") for m in pat.finditer(data[:2_000_000])]
    seen, uniq = set(), []
    for s in raw:
        if s in seen:
            continue
        seen.add(s)
        uniq.append(s)
    KEY = ("flag", "ctf", "pass", "key", "secret", "admin", "token",
           "http", "user", "zip", "png", "jpg", ".txt", ".py", ".php")
    hot = [s for s in uniq if any(k in s.lower() for k in KEY)]
    cold = [s for s in uniq if s not in set(hot)]
    return (hot + cold)[:MAX_STRINGS]


# ---------------------------------------------------------------- 工具 3
def _resolve_cmd(name: str) -> list[str] | None:
    """在候选列表里找出实际可用的命令前缀。"""
    for cand in TOOL_CMDS.get(name, []):
        head = cand[0]
        if os.path.isabs(head):
            if Path(head).exists():
                return cand
        elif shutil.which(head):
            return cand
    return None


def available_tools() -> dict[str, bool]:
    return {k: _resolve_cmd(k) is not None for k in TOOL_CMDS}


def run_tool(tool: str, path: str, argset: int = 0) -> tuple[bool, str]:
    """调用白名单里的侦察工具（只读，带超时）。"""
    name = (tool or "").strip().lower()
    name = _ALIAS.get(name, name)
    if name not in TOOL_CMDS:
        return False, (f"不支持的侦察工具 {tool!r}。"
                       f"可用：{', '.join(sorted(TOOL_CMDS))}")

    prefix = _resolve_cmd(name)
    if prefix is None:
        hint = PYTHON_FALLBACK.get(name, "请用 probe_file 替代")
        return False, f"本机没有安装 {name}。请改用：{hint}"

    f = _resolve(path)
    if f is None:
        return False, f"路径越界或不存在: {path}"
    if not f.is_file():
        return False, f"不是文件: {path}"

    templates = TOOL_ARGS.get(name, [["{path}"]])
    idx = int(argset or 0)
    if idx < 0 or idx >= len(templates):
        idx = 0
    tmpl = templates[idx]
    outdir = str((ROOT / "work" / "_probe").resolve())
    (ROOT / "work" / "_probe").mkdir(parents=True, exist_ok=True)
    argv = [t.format(path=str(f), outdir=outdir) for t in tmpl]

    try:
        r = subprocess.run([*prefix, *argv], capture_output=True, text=True,
                           timeout=TIMEOUT, cwd=str(f.parent),
                           errors="replace")
    except subprocess.TimeoutExpired:
        return False, f"{name} 超时（>{TIMEOUT}s）"
    except Exception as e:  # noqa: BLE001
        return False, f"{name} 执行失败: {type(e).__name__}: {e}"

    body = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
    body = body.strip() or "（无输出）"
    if len(body) > MAX_OUT:
        body = body[:MAX_OUT] + "\n...(已截断)"
    cmd = " ".join(Path(x).name for x in prefix)
    return True, f"$ {cmd} {' '.join(argv)}\n(exit={r.returncode})\n{body}"


# ---------------------------------------------------------------- 规格
TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "列出目录里的文件及其大小和类型判断。"
                "题面没给有效信息时，**第一步就应该用它看看 work/ 目录里有什么附件**。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string",
                                  "description": "目录，默认 work"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "probe_file",
            "description": (
                "自动侦察一个文件：判断真实类型（不看扩展名，看魔数）、大小、"
                "开头/结尾字节、内嵌的其它文件、以及里面所有可读字符串（关键词优先）。"
                "**这是从附件里找线索的主力工具**，拿到附件路径后立刻调用它。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string",
                             "description": "文件相对路径，如 work/attachment.png"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tool",
            "description": (
                "调用白名单里的取证工具做进一步分析。"
                "可用：file / binwalk / strings / exiftool / zsteg / pngcheck / "
                "steghide / foremost / 7z / unzip / tar / identify。"
                "例如 binwalk 看内嵌文件、zsteg 看 PNG 隐写、exiftool 看元数据。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tool": {"type": "string", "description": "工具名"},
                    "path": {"type": "string", "description": "目标文件路径"},
                    "argset": {"type": "integer",
                               "description": "参数组合编号，一般用 0"},
                },
                "required": ["tool", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_embedded",
            "description": (
                "把 probe_file 发现的某个内嵌文件（按偏移）导出到 work/_probe/ 下。"
                "例如 probe_file 报告「0x45 偏移: ZIP」，就用 offset=69 导出。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "源文件路径"},
                    "offset": {"type": "integer", "description": "内嵌数据起始偏移（十进制）"},
                    "size": {"type": "integer", "description": "可选，导出长度"},
                },
                "required": ["path", "offset"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_zip",
            "description": (
                "解压 ZIP（含改过扩展名的，比如 fake.png 其实是 zip）。"
                "会自动检测加密并拒绝目录穿越。解压后继续用 probe_file 分析。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "zip 文件路径"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_gzip",
            "description": (
                "解 GZIP（.gz 或藏在别的文件里的 gzip 片段）。"
                "probe_file 报告某偏移是 GZIP 时，先 extract_embedded 导出再调这个。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "gz 文件路径"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_directions",
            "description": (
                "选手完全没思路时用这个。它会先对附件做完整侦察，"
                "再让本地模型给出 3 个最值得先试的方向（含依据与具体做法）。"
                "只有 probe_file 之后仍然不知道该干什么，才调它。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "附件路径"},
                    "question": {"type": "string", "description": "题面描述（可空）"},
                },
                "required": ["path"],
            },
        },
    },
]


# ---------------------------------------------------------------- 工具 4
def extract_embedded(path: str, offset: int, size: int | None = None) -> tuple[bool, str]:
    """把文件里某一偏移处的内嵌数据导出到 work/_probe/ 下。"""
    try:
        from agent import carve as _carve
    except Exception as e:  # noqa: BLE001
        return False, f"雕刻模块不可用: {e}"

    f = _resolve(path)
    if f is None:
        return False, f"路径越界或不存在: {path}"
    data = f.read_bytes()
    off = int(offset or 0)
    if off < 0 or off >= len(data):
        return False, f"偏移 {off} 超出文件范围（0~{len(data)}）"

    # 用雕刻器推断真实大小
    if not size:
        cr = _carve.carve_files(data[off:])
        cand = [i for i in cr["items"] if i["offset"] == 0]
        if cand:
            size = cand[0]["size"]
    size = int(size) if size else len(data) - off

    blob = data[off: off + size]
    outdir = ROOT / "work" / "_probe"
    outdir.mkdir(parents=True, exist_ok=True)
    # 猜扩展名
    from agent.recon import MAGIC
    ext = ".bin"
    for magic, desc in MAGIC:
        if len(magic) <= len(blob) and blob.startswith(magic):
            key = desc.split("(")[0].strip()
            ext = {"PNG": ".png", "JPEG": ".jpg", "GIF": ".gif", "PDF": ".pdf",
                   "ELF": ".elf", "OGG": ".ogg", "FLAC": ".flac", "BMP": ".bmp",
                   "gzip": ".gz", "bzip2": ".bz2", "xz": ".xz",
                   "ZIP": ".zip", "RAR": ".rar", "7z": ".7z",
                   "PE": ".exe", "WAV": ".wav", "MP3": ".mp3"}.get(key, ".bin")
            break
    out = outdir / f"extract_{off:x}{ext}"
    out.write_bytes(blob)
    return True, (f"已导出 {len(blob)} 字节 -> {out}\n"
                  f"可以继续用 probe_file 或 extract_zip 分析它")


# ---------------------------------------------------------------- 工具 5
def extract_zip(path: str) -> tuple[bool, str]:
    """解压 ZIP（含改扩展名的 zip），输出到 work/_probe/<name>_unzip/。"""
    try:
        from agent import carve as _carve
    except Exception as e:  # noqa: BLE001
        return False, f"解压模块不可用: {e}"

    f = _resolve(path)
    if f is None:
        return False, f"路径越界或不存在: {path}"
    outdir = ROOT / "work" / "_probe" / (f.stem + "_unzip")
    r = _carve.extract_zip(f, outdir)
    if not r["ok"]:
        return False, f"解压失败: {r.get('error')}\n条目: {r.get('entries')}"
    lines = [f"已解压到 {r['outdir']}"]
    for e in r["entries"][:20]:
        lines.append(f"  {e['name']}  {e['size']} 字节")
    lines.append("可以对解出来的文件继续用 probe_file 分析")
    return True, "\n".join(lines)




# ---------------------------------------------------------------- 工具 6
def extract_gzip(path: str) -> tuple[bool, str]:
    """解 GZIP（含藏在别的文件里的 gzip 片段）。"""
    try:
        from agent import carve as _carve
    except Exception as e:  # noqa: BLE001
        return False, f"解压模块不可用: {e}"
    f = _resolve(path)
    if f is None:
        return False, f"路径越界或不存在: {path}"
    r = _carve.extract_gzip(f, ROOT / "work" / "_probe")
    if not r["ok"]:
        return False, f"GZIP 解压失败: {r['error']}"
    lines = [f"解压成功，得到 {r['size']} 字节"]
    if r.get("text"):
        lines.append("解出的文本内容（原样，直接用）:")
        lines.append("  " + r["text"][:600])
    if r.get("outfile"):
        lines.append(f"已写出: {r['outfile']}")
    return True, "\n".join(lines)

# ---------------------------------------------------------------- 工具 7
def suggest_directions(path: str, question: str = "") -> tuple[bool, str]:
    """没思路时给方向建议：侦察附件 + 小模型推方向。"""
    try:
        from agent.hint import hint_for
    except Exception as e:  # noqa: BLE001
        return False, f"建议模块不可用: {e}"
    r = hint_for(path, question=question)
    if not r.hints and not r.raw:
        return False, r.note or "没有生成建议"
    return True, r.render()


def dispatch(name: str, args: dict) -> tuple[bool, str]:
    if not isinstance(args, dict):
        return False, "参数必须是对象"
    if name == "list_files":
        return list_files(**{"directory": args.get("directory", "work")})
    if name == "probe_file":
        return probe_file(**{"path": args.get("path", "")})
    if name == "run_tool":
        return run_tool(**{"tool": args.get("tool", ""),
                           "path": args.get("path", ""),
                           "argset": args.get("argset", 0)})
    if name == "extract_embedded":
        return extract_embedded(**{"path": args.get("path", ""),
                                   "offset": args.get("offset", 0),
                                   "size": args.get("size")})
    if name == "extract_gzip":
        return extract_gzip(**{"path": args.get("path", "")})
    if name == "extract_zip":
        return extract_zip(**{"path": args.get("path", "")})
    if name == "suggest_directions":
        return suggest_directions(path=args.get("path", ""),
                                   question=args.get("question", ""))
    return False, f"未知工具: {name}"

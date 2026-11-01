"""DB-Q1 只读语料质量审计与近似去重候选。

设计约束（与 docs/DB_QUALITY.md 一致）：

* **只读**：本脚本不写 kb、不写 index、不写 config.toml。所有输出只落在
  ``--out-dir``（默认 ``work/db_quality1``）。工具不会修改任何被审计文件。
* **收录规则同源**：枚举 Markdown 复用 ``kb.parser.iter_md_paths``，与
  manifest / 索引完全同一套规则，不另造一套文件扫描口径。
* **元数据缺失 != 违规**：license 字段只记录"写了什么"，从不推断"已获许可"。
* **启发式标注为疑似**：所有启发式规则输出都带 ``confidence``，报告里统称
  "疑似"，不当作事实。

用法::

    .\\.venv\\Scripts\\python.exe tools\\audit_corpus.py
    .\\.venv\\Scripts\\python.exe tools\\audit_corpus.py --help

输出（默认 ``work/db_quality1/``）：

``inventory.jsonl``          每篇一行记录
``duplicate_candidates.json`` 精确副本 + 近似候选 + 簇 + 同 URL 线索
``import_check.json``        277 篇导入批专项核查
``eval_protocol.json``       下一批冻结检索评测的采集/标注协议（只设计）
``run_meta.json``            规模、耗时、错误数、参数（便于复跑比对）
``report.md``                人读报告
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
import traceback
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import yaml

from kb.config import Config  # noqa: E402
from kb.parser import (  # noqa: E402
    VALID_CATEGORIES,
    iter_md_paths,
    split_front_matter,
)

SCHEMA_VERSION = 1
DEFAULT_OUT_DIR = "work/db_quality1"
SHINGLE_K = 5           # 字符级 shingle 宽度（CJK 友好，不依赖分词）
MIN_SHINGLES = 12       # 少于该数量的 shingle 不参与近似比对（短卡片由包含关系兜底）
# 包含度判据是最容易被"一篇短卡片整段出现在长文里"判中的，短卡片侧的集合越小
# 越容易被放大成高分，所以参与包含度比对的最小集合规模单独设（远大于噪声水平，
# 又远小于实测最短正文约 55 个 shingle，避免把整个语料排除在外）。
MIN_CONTAINMENT_SHINGLES = 50
GENERIC_URL_PATHS = {"", "/", "/index.html", "/index.php", "/home", "/en", "/zh"}

# ---------------------------------------------------------------------------
# 通用小工具
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_text_strict(path: Path) -> tuple[str, str | None]:
    """按 UTF-8 严格读取；返回 (文本, 错误描述)。解码失败时退化为 replace 以便继续审计。"""
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError as e:
        return raw.decode("utf-8", errors="replace"), (
            f"非 UTF-8 字节（offset {e.start}）: {e.reason}"
        )


def norm_url(url: str) -> str:
    """URL 归一化：小写 scheme/host、去末尾斜杠与常见追踪参数。

    仅用于"同 URL 线索"归并；**通用首页 URL 不参与归并**（见 ``url_group_key``）。
    """
    u = (url or "").strip()
    if not u:
        return ""
    u = u.split("#", 1)[0]
    scheme, _, rest = u.partition("://")
    if not rest:
        return u.lower()
    host, _, path = rest.partition("/")
    host = host.lower()
    path = "/" + path if path else ""
    path = path.split("?", 1)[0]
    while path.endswith("/") and len(path) > 1:
        path = path[:-1]
    return f"{scheme.lower()}://{host}{path}".rstrip("/")


def url_group_key(url: str) -> str:
    """返回可归并的 URL 键；通用首页 / 空 URL 返回空串（不可归并）。"""
    n = norm_url(url)
    if not n:
        return ""
    scheme, _, rest = n.partition("://")
    host, _, path = rest.partition("/")
    if "/" + path in GENERIC_URL_PATHS or not path:
        return ""
    return n


def url_host(url: str) -> str:
    u = norm_url(url)
    if not u:
        return ""
    rest = u.partition("://")[2] or u
    return rest.split("/", 1)[0]


# ---------------------------------------------------------------------------
# front-matter / 代码围栏 / 图片
# ---------------------------------------------------------------------------

# 至少 3 个反引号或波浪线，闭合同字符且长度 >= 开启长度（CommonMark 规则）。
# 引用块里也能开围栏（"> ```asm"），所以先剥掉最多 3 层引用前缀再匹配。
FENCE_OPEN_RE = re.compile(r"^(?P<indent>[ ]{0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
BLOCKQUOTE_RE = re.compile(r"^[ ]{0,3}>[ ]?")
# 行内代码：`...` 或 ``...``（反引号串定界，贪婪到同长度定界符）
INLINE_CODE_RE = re.compile(r"(?P<tick>`+)(?:(?!`).)+?(?P=tick)")


def strip_blockquote(line: str, max_depth: int = 3) -> str:
    """剥掉行首引用前缀 `> `，返回引用内的内容行。"""
    for _ in range(max_depth):
        m = BLOCKQUOTE_RE.match(line)
        if not m:
            break
        line = line[m.end():]
    return line

IMG_INLINE_RE = re.compile(r"!\[[^\]]*\]\(\s*(?P<target><[^>]*>|[^)\s]+)")
IMG_REFDEF_RE = re.compile(r"^\s{0,3}\[(?P<label>[^\]]+)\]:\s*(?P<target>\S+)", re.M)
IMG_HTML_RE = re.compile(r"""<img\b[^>]*?\bsrc\s*=\s*["'](?P<target>[^"']+)["']""", re.I)
IMG_REFUSE_RE = re.compile(r"!\[[^\]]*\]\s*\[(?P<label>[^\]]*)\]")
IMG_PLACEHOLDER_RE = re.compile(r"!\[[^\]]*\]\(\s*\)")

# "疑似依图"：正文里紧跟图片段落/链接的指代性表述
IMAGE_DEPENDENT_RE = re.compile(
    r"(如图|下图|上图|见图|图\s*\d|图中|图示|图中所示|截图|附图|"
    r"(?<![\w])see\s+(?:the\s+)?figure)",
    re.I,
)

CONTENT_TYPE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("summary_card", re.compile(r"一句话总结|攻击链|关键 payload|经验教训", re.I)),
    ("index", re.compile(r"^\s*[-*]\s*\[[^\]]+\]\([^)]*\.md\)", re.M)),
    ("tool_doc", re.compile(r"用法|usage|--help|参数说明", re.I)),
]


def _inline_code_mask(line: str) -> str:
    """把行内代码片段（`...` / ``...``）替换成空格，避免把示例文本当围栏。"""
    def repl(m: re.Match[str]) -> str:
        return " " * len(m.group(0))
    return INLINE_CODE_RE.sub(repl, line)


def _stray_fence_marker(line: str) -> bool:
    """行内（已去引用前缀、已去行内代码）是否残留"不构成合法围栏"的标记。

    - 整行是 0-3 空格缩进加 ```/~~~ 的开启行：不算 stray（由围栏/未闭合逻辑判定）。
    - 4 空格及以上缩进的行是缩进代码块，其中的 ``` 只是被展示的源码，不算 stray。
    - 紧贴文字的反引号串：必须成对（如 ```x```）才算行内示例，只余单数才算 stray。
    - 波浪线：只有"裸的 ~~~ 独占一行"才有围栏语义；嵌在字符画/清单里的 ~~~ 不算。
    """
    has_ticks = "```" in line
    has_tildes = "~~~" in line
    if not has_ticks and not has_tildes:
        return False
    if line[:1] in (" ", "\t") and len(line) - len(line.lstrip(" ")) >= 4:
        return False
    if FENCE_OPEN_RE.match(line):
        return False        # 能被识别为开启行，交给围栏/未闭合逻辑判定
    if has_ticks:
        return bool(line.count("```") % 2)
    # 波浪线：只有整行就是 ~~~ 才可能是"没配对成功"的围栏
    return line.strip() == "~~~"


def parse_fences(body: str) -> dict[str, Any]:
    """按 CommonMark 规则扫描围栏：反引号/波浪线、长度配对、未闭合检测。

    - 引用块内的围栏（`> ```lang`）同样识别（先剥 `> ` 前缀）。
    - 未被围栏吸收的行里若还有围栏标记，才报 stray_backticks；
      这些行先遮蔽围栏区域、再去掉行内代码，因此 `` `a```b` `` 这类
      行内示例不会误报。
    """
    lines = body.splitlines()
    open_fence: tuple[str, int, int] | None = None  # (char, length, line_no)
    blocks: list[dict[str, Any]] = []
    problems: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        content = strip_blockquote(line)
        if open_fence is None:
            m = FENCE_OPEN_RE.match(content)
            if not m:
                continue
            fence = m.group("fence")
            rest = m.group("info").strip()
            # 开启围栏的 info 里不允许出现与围栏相同的字符（CommonMark 规则）
            if fence[0] == "`" and "`" in rest:
                continue
            open_fence = (fence[0], len(fence), idx)
            blocks.append({"open_line": idx, "char": fence[0], "len": len(fence),
                           "info": rest, "close_line": None,
                           "quoted": content is not line})
            continue
        char, length, _start = open_fence
        stripped = content.strip()
        if (stripped and set(stripped) == {char} and len(stripped) >= length
                and len(content) - len(content.lstrip(" ")) <= 3):
            blocks[-1]["close_line"] = idx
            open_fence = None
    if open_fence is not None:
        problems.append({
            "kind": "unclosed_fence",
            "line": open_fence[2],
            "detail": f"{open_fence[2]} 行开启的 {open_fence[0] * open_fence[1]} 未闭合",
        })

    # 围栏区域之外的裸标记（去引用前缀 + 去行内代码后仍残留）才算 stray；
    # 合法开启行已算在 blocks 里，天然被 fenced 标记覆盖。
    fenced = [False] * (len(lines) + 1)
    for b in blocks:
        end = b["close_line"] or len(lines)
        for n in range(b["open_line"], end + 1):
            fenced[n] = True
    stray_lines = [
        idx for idx, line in enumerate(lines, start=1)
        if not fenced[idx] and _stray_fence_marker(
            _inline_code_mask(strip_blockquote(line)))
    ]
    if stray_lines:
        problems.append({
            "kind": "stray_backticks",
            "line": stray_lines[0],
            "detail": (f"第 {stray_lines[0]} 行等 {len(stray_lines)} 处出现围栏标记"
                       f"但不构成合法围栏（未被任何代码块吸收）"),
        })
    langs = Counter((b["info"].split() or [""])[0].lower() for b in blocks if b["close_line"])
    return {
        "fence_count": len(blocks),
        "closed_fence_count": sum(1 for b in blocks if b["close_line"]),
        "quoted_fence_count": sum(1 for b in blocks if b.get("quoted")),
        "fenced_chars": sum(
            len("\n".join(lines[b["open_line"] - 1:(b["close_line"] or len(lines))]))
            for b in blocks
        ),
        "fence_langs": dict(langs),
        "fence_problems": problems,
    }


def classify_image_target(target: str) -> str:
    t = target.strip().strip("<>").split("?", 1)[0]
    if t.startswith("data:"):
        return "embedded"
    if re.match(r"^(https?:)?//", t):
        return "remote"
    return "local"


def collect_images(body: str, doc_path: Path, kb_dir: Path) -> list[dict[str, Any]]:
    """收集图片引用并分类：local_missing / remote_unverified / embedded。"""
    refdefs = {m.group("label").strip().lower() for m in IMG_REFDEF_RE.finditer(body)}
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(kind_src: str, target: str, line: int | None) -> None:
        t = target.strip().strip("<>")
        cls = classify_image_target(t)
        key = (kind_src, t)
        if key in seen:
            return
        seen.add(key)
        rec = {"source": kind_src, "target": t, "class": cls, "line": line}
        if cls == "local":
            rel = t.split("?", 1)[0]
            resolved = (doc_path.parent / rel)
            try:
                exists = resolved.exists()
            except OSError:
                exists = False
            rec["resolved"] = resolved.relative_to(kb_dir).as_posix() \
                if resolved.is_relative_to(kb_dir) else str(resolved)
            rec["exists"] = exists
        out.append(rec)

    for m in IMG_INLINE_RE.finditer(body):
        add("inline", m.group("target"), body.count("\n", 0, m.start()) + 1)
    for m in IMG_HTML_RE.finditer(body):
        add("html", m.group("target"), body.count("\n", 0, m.start()) + 1)
    for m in IMG_REFDEF_RE.finditer(body):
        if m.group("label").strip().lower() in refdefs:
            # 只有被 ![..][label] 引用的定义才算图片
            pass
    for m in IMG_REFUSE_RE.finditer(body):
        label = (m.group("label") or "").strip().lower()
        if label:
            d = next((x for x in IMG_REFDEF_RE.finditer(body)
                      if x.group("label").strip().lower() == label), None)
            if d:
                add("refused", d.group("target"),
                    body.count("\n", 0, d.start()) + 1)
    return out


def image_dependency(body: str, images: list[dict[str, Any]]) -> dict[str, Any]:
    """区分"有图"与"正文疑似依图"：只有正文出现指代性表述才标疑似。"""
    no_fence = "\n".join(
        strip_blockquote(line) for line in body.splitlines()
        if not FENCE_OPEN_RE.match(strip_blockquote(line))
    )
    hints = [m.group(0) for m in IMAGE_DEPENDENT_RE.finditer(no_fence)]
    return {
        "image_refs": len(images),
        "local_missing": [i["target"] for i in images
                          if i["class"] == "local" and not i.get("exists")],
        "remote_unverified": [i["target"] for i in images if i["class"] == "remote"],
        "image_dependent_hints": hints[:8],
        "image_dependent_hint_count": len(hints),
        # 只有"有指代表述但图不可用"才升格为疑似依图断裂
        "suspect_broken_image_dependency": bool(hints) and (
            any(i["class"] == "local" and not i.get("exists") for i in images)
            or any(i["class"] == "remote" for i in images)
        ),
    }


# ---------------------------------------------------------------------------
# 正文正规化与分块（近似去重用）
# ---------------------------------------------------------------------------


def strip_front_matter_text(raw: str) -> tuple[dict[str, Any], str, bool]:
    """返回 (meta, body, front_matter_parsed)。不抛异常。"""
    try:
        meta, body = split_front_matter(raw)
    except Exception:  # noqa: BLE001 - 解析器可能因极端 YAML 抛任意异常
        return {}, raw, False
    parsed = bool(meta) or raw.lstrip().startswith("---")
    return (meta if isinstance(meta, dict) else {}), body, parsed


def diagnose_front_matter(raw: str) -> tuple[dict[str, Any], str, str]:
    """返回 (meta, body, fm_error)。

    区分三种情况，避免把"YAML 写坏了"误报成"没有元数据"：
      * 没有 front-matter 块      -> "缺少 front-matter..."
      * YAML 语法错误（有块但解析失败） -> "front-matter YAML 解析失败: <错误原文>"
      * 块解析成非映射            -> "front-matter 不是键值映射"
    """
    text = raw.lstrip("\ufeff").lstrip("\n").lstrip("\r\n")
    has_block = text.startswith("---")
    if not has_block:
        return {}, raw, "缺少 front-matter（文件不以 --- 开头）"
    # 自己切块，才能把 YAML 错误和"没有块"区分开
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}, raw, "front-matter 未闭合（缺少结束的 ---）"
    block = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError as e:
        err = " ".join(str(e).split())
        line_no = ""
        mark = getattr(e, "problem_mark", None)
        if mark is not None:
            # +2：0 基下标 -> 1 基行号，再加 front-matter 起始行
            line_no = f"（第 {mark.line + 2} 行）"
        return {}, body, f"front-matter YAML 解析失败{line_no}: {err}"
    except Exception as e:  # noqa: BLE001
        return {}, body, f"front-matter 解析异常: {type(e).__name__}: {e}"
    if loaded is None:
        return {}, body, "front-matter 为空（只有 --- 分隔符）"
    if not isinstance(loaded, dict):
        return {}, body, f"front-matter 不是键值映射（解析为 {type(loaded).__name__}）"
    return loaded, body, ""


LINK_URL_RE = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)(\))")
URL_RE = re.compile(r"https?://\S+")
WS_RE = re.compile(r"\s+")
PUNCT_RE = re.compile(r"[\s\-_—–·.,;:!?'\"“”‘’()（）\[\]【】<>《》/\\|*#>~`]+")


def normalize_body(body: str) -> str:
    """正文正规化：去围栏标记、链接 URL、标点空白、统一全半角、小写。

    目标是比较"散文内容"本身；代码块内容保留字符（因为代码编写方式本身就是
    区分"同题不同解法"的关键信号），只去掉围栏与缩进噪声。
    """
    text = unicodedata.normalize("NFKC", body)
    text = LINK_URL_RE.sub(lambda m: m.group(1) + m.group(3), text)
    text = URL_RE.sub("", text)
    text = re.sub(r"^\s{0,3}(`{3,}|~{3,}).*$", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.M)
    text = PUNCT_RE.sub("", text)
    return text.lower()


def normalize_title(title: str) -> str:
    return PUNCT_RE.sub("", unicodedata.normalize("NFKC", title).lower())


def shingles(norm: str, k: int = SHINGLE_K) -> set[str]:
    if not norm:
        return set()
    if len(norm) <= k:
        return {norm}
    return {norm[i:i + k] for i in range(len(norm) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def containment(a: set[str], b: set[str]) -> float:
    """a 被 b 覆盖的比例（|a∩b|/|a|）；用于识别"摘要卡 ⊂ 完整正文"。"""
    if not a:
        return 0.0
    return len(a & b) / len(a)


def common_snippet(norm_a: str, norm_b: str, width: int = 60) -> str:
    """给候选对一个人可读的公共片段：取较短文本里最长的、也在另一篇出现的子串。"""
    short, long_ = (norm_a, norm_b) if len(norm_a) <= len(norm_b) else (norm_b, norm_a)
    if not short:
        return ""
    lo, hi, best = min(len(short), 12), len(short), ""
    while lo <= hi:
        mid = (lo + hi) // 2
        found = ""
        # 每 7 格取一个位置，避免退化成 O(n^2) 的长串匹配
        for i in range(0, max(1, len(short) - mid + 1), 7):
            cand = short[i:i + mid]
            if cand and cand in long_:
                found = cand
                break
        if found:
            best, lo = found, mid + 1
        else:
            hi = mid - 1
    return best[:width]


# ---------------------------------------------------------------------------
# 盘点
# ---------------------------------------------------------------------------

CONTENT_LICENSE_KEYS = ("license", "origin_license")
VERIFICATION_KEYS = (
    "verification_status", "verification", "repro_status", "reproduced",
    "review_status", "origin_verification", "status",
)


def first_present(meta: dict[str, Any], keys: Sequence[str]) -> tuple[str, str]:
    """返回 (字段名, 值文本)；没有则 ("", "")。不推断值。"""
    for k in keys:
        if k in meta and meta[k] not in (None, "", [], {}):
            return k, str(meta[k]).strip()
    return "", ""


def content_type_of(body: str, meta: dict[str, Any], body_len: int) -> str:
    for name, pat in CONTENT_TYPE_RULES:
        if pat.search(body):
            return name
    if body_len < 300:
        return "stub"
    return "prose"


def audit_doc(path: Path, kb_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """审计单篇；返回 (记录, 解析/读取异常列表)。异常不吞掉。"""
    rel = path.relative_to(kb_dir).as_posix()
    errors: list[dict[str, Any]] = []
    record: dict[str, Any] = {"path": rel}

    # ---- 字节层：内容哈希、编码 ----
    try:
        raw_bytes = path.read_bytes()
        file_size = len(raw_bytes)
        record["file_sha256"] = sha256_bytes(raw_bytes)
    except OSError as e:
        errors.append({"path": rel, "stage": "read", "error": f"{getattr(e, 'errno', '')}: {e}"})
        record.update({"file_sha256": "", "auditable": False,
                       "error": "unreadable"})
        return record, errors

    raw, decode_error = read_text_strict(path)
    if decode_error:
        errors.append({"path": rel, "stage": "decode", "error": decode_error})
        record["decode_error"] = decode_error
    record["bytes"] = file_size

    # ---- front-matter ----
    meta, body, fm_error = diagnose_front_matter(raw)
    if fm_error:
        errors.append({"path": rel, "stage": "frontmatter", "error": fm_error})

    title = str(meta.get("title") or path.stem).strip()
    category = str(meta.get("category") or path.parent.name).strip().lower()
    source = str(meta.get("source") or "").strip()
    lic_key, lic_val = first_present(meta, CONTENT_LICENSE_KEYS)
    ver_key, ver_val = first_present(meta, VERIFICATION_KEYS)
    body_len = len(body)

    # ---- 围栏 ----
    fences = parse_fences(body)
    if fences["fence_problems"]:
        for p in fences["fence_problems"]:
            errors.append({"path": rel, "stage": "fence", "error": p["detail"]})

    # ---- 图片 ----
    images = collect_images(body, path, kb_dir)
    img_info = image_dependency(body, images)

    record.update({
        "auditable": True,
        "title": title,
        "category": category,
        "category_valid": category in VALID_CATEGORIES,
        "source": source,
        "source_host": url_host(source),
        "source_group_key": url_group_key(source),
        "license_field": lic_key,
        "license_value": lic_val,
        "verification_field": ver_key,
        "verification_value": ver_val,
        "body_chars": body_len,
        "body_sha256_raw": sha256_text(body),
        "content_type": content_type_of(body, meta, body_len),
        "fence_count": fences["fence_count"],
        "closed_fence_count": fences["closed_fence_count"],
        "fenced_chars": fences["fenced_chars"],
        "fence_langs": fences["fence_langs"],
        "fence_problems": fences["fence_problems"],
        "has_code": fences["closed_fence_count"] > 0,
        "images": img_info,
        "headings": [m.group(2).strip()
                     for m in re.finditer(r"^(#{1,6})\s+(.*)$", body, re.M)][:40],
        "front_matter_error": fm_error,
        "accent": str(meta.get("origin") or meta.get("origin_kind") or ""),
    })
    return record, errors


# ---------------------------------------------------------------------------
# 邻近去重
# ---------------------------------------------------------------------------


def find_exact_duplicates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_hash: defaultdict[str, list[str]] = defaultdict(list)
    for r in records:
        if r.get("auditable") and r.get("body_sha256_raw"):
            by_hash[r["body_sha256_raw"]].append(r["path"])
    out = []
    for h, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            out.append({"sha256": h, "paths": sorted(paths), "size": len(paths)})
    return out


def find_near_duplicates(
    records: list[dict[str, Any]],
    shingle_sets: dict[str, set[str]],
    *,
    min_shingle_jaccard: float,
    min_containment: float,
    candidate_cap: int = 200000,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """shingle 倒排候选生成 + 阈值反推的共享数下界，不在验证前丢弃高分对。

    关键点：候选过滤不靠"取分数前 N 对"截断，而靠可证明的必要条件——
      jaccard(A,B) >= t        => shared >= t/(1+t) * |A∪B| >= t/(1+t) * max(|A|,|B|)
      containment(A in B) >= c => shared >= c * |A|
    所以逐对算下界 floor(min(t/(1+t)*max, c*min))，达不到的对必不可能过阈值，
    丢掉的都是可证明无关的对；不存在"因为排位靠后被截断"的漏报。
    candidate_cap 只是极端语料下的内存保险，触发时会写进 stats["capped"]。
    """
    stats = {"pairs_examined": 0, "docs": 0, "capped": False,
             "pairs_scored": 0, "min_shared": 0}
    shingle_index: defaultdict[str, list[int]] = defaultdict(list)
    info = []
    for i, r in enumerate(records):
        if not r.get("auditable"):
            continue
        s = shingle_sets.get(r["path"], set())
        if len(s) < MIN_SHINGLES:  # 太短不参与（短卡片自然被长文包含）
            continue
        info.append(i)
        for sh in s:
            shingle_index[sh].append(i)
    stats["docs"] = len(info)
    if not info:
        return [], stats

    # 阈值下界是逐对算的（见 _floor），全局 min_shared 只作为参考值记录
    stats["min_shared"] = 0

    # 倒排累积共享 shingle 数。超高频 shingle 也照常计数：它可能把一对推过
    # min_shared，跳过就会漏报；用整数编码配对代替 tuple，控制内存。
    cand_pairs: Counter[int] = Counter()
    n_docs = len(records)
    for sh, idxs in shingle_index.items():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs)):
            base = idxs[a] * n_docs
            for b in range(a + 1, len(idxs)):
                cand_pairs[base + idxs[b]] += 1
    stats["pairs_scored"] = len(cand_pairs)

    # 逐对下界：达不到就说明两篇不可能过阈值，直接丢，不需要算集合
    def _floor(key: int, shared: int) -> bool:
        i, j = divmod(key, n_docs)
        si = len(shingle_sets[records[i]["path"]])
        sj = len(shingle_sets[records[j]["path"]])
        lo, hi = (si, sj) if si <= sj else (sj, si)
        # 包含度判据只对"两边都不算太短"的对生效；短卡片侧容易被放大成假高分。
        need_j = math.floor(min_shingle_jaccard / (1.0 + min_shingle_jaccard) * hi) \
            if min_shingle_jaccard > 0 else 0
        if min_containment > 0 and lo >= MIN_CONTAINMENT_SHINGLES:
            need_c = math.floor(min_containment * lo)
            need = min(need_j, need_c) if need_j else need_c
        else:
            need = need_j
        return shared >= need

    # 用下界过滤候选（instead of 截断），保证不漏掉任何可能过线的对
    ranked = [(divmod(k, n_docs), v) for k, v in cand_pairs.items() if _floor(k, v)]
    ranked.sort(key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) > candidate_cap:      # 仅为内存/耗时的最后保险，会显式告警
        ranked = ranked[:candidate_cap]
        stats["capped"] = True

    pairs: list[dict[str, Any]] = []
    for (i, j), shared in ranked:
        stats["pairs_examined"] += 1
        ra, rb = records[i], records[j]
        sa, sb = shingle_sets[ra["path"]], shingle_sets[rb["path"]]
        jac = jaccard(sa, sb)
        ca, cb = containment(sa, sb), containment(sb, sa)
        # 短文档侧的包含度不可信（一篇 20 字的卡片能"包含进"任何长文），
        # 所以短边低于 MIN_CONTAINMENT_SHINGLES 时只认 jaccard，不认包含度。
        if min(len(sa), len(sb)) < MIN_CONTAINMENT_SHINGLES:
            ca = cb = 0.0
        if jac < min_shingle_jaccard and max(ca, cb) < min_containment:
            continue
        tiny = min(len(sa), len(sb)) < MIN_CONTAINMENT_SHINGLES
        len_ratio = (min(len(ra["norm"]), len(rb["norm"])) /
                     max(1, max(len(ra["norm"]), len(rb["norm"]))))
        a, b = sorted([ra["path"], rb["path"]])
        method = "jaccard" if jac >= min_shingle_jaccard else "containment"
        pairs.append({
            "a": a, "b": b,
            "score": round(max(jac, ca, cb), 4),
            "jaccard": round(jac, 4),
            "containment_a_in_b": round(ca, 4),
            "containment_b_in_a": round(cb, 4),
            "len_ratio": round(len_ratio, 4),
            "shared_shingles": shared,
            "tiny_doc_containment_ignored": tiny,
            "method": f"char{SHINGLE_K}_shingle+{method}",
            "snippet": common_snippet(ra["norm"], rb["norm"]),
        })
    pairs.sort(key=lambda p: (-p["score"], p["a"], p["b"]))
    return pairs, stats


def classify_pair(pair: dict[str, Any], recs: dict[str, dict[str, Any]]) -> str:
    """给候选对一个人可解释的判读（不是删除建议）。"""
    a, b = recs[pair["a"]], recs[pair["b"]]
    ca, cb = pair["containment_a_in_b"], pair["containment_b_in_a"]
    if pair["jaccard"] >= 0.95:
        return "near_equivalent_copy"
    if pair.get("tiny_doc_containment_ignored"):
        # 短卡片进长文：这类对很可能是"素材片段被整段搬进另一篇"，不是重复文档
        return "short_fragment_of_longer_text"
    if ca >= 0.75 and ca > cb + 0.1:
        return "a_subset_of_b"
    if cb >= 0.75 and cb > ca + 0.1:
        return "b_subset_of_a"
    if max(ca, cb) >= 0.6:
        if a["content_type"] != b["content_type"]:
            return "summary_card_vs_full_text"
        return "large_overlap_different_solution"
    return "weak_overlap_review"


def build_clusters(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """连通分量簇：只表示"同一疑似重复簇"，不宣称簇内两两等价。"""
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[max(rx, ry)] = min(rx, ry)

    for p in pairs:
        union(p["a"], p["b"])
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for node in list(parent):
        groups[find(node)].append(node)
    clusters = []
    pair_by_key = {(p["a"], p["b"]): p for p in pairs}
    for root, members in sorted(groups.items()):
        members = sorted(members)
        if len(members) < 2:
            continue
        inner = [pair_by_key[(members[i], members[j])]
                 for i in range(len(members)) for j in range(i + 1, len(members))
                 if (members[i], members[j]) in pair_by_key]
        direct = len(inner)
        possible = len(members) * (len(members) - 1) // 2
        clusters.append({
            "candidate_cluster": root,
            "members": members,
            "size": len(members),
            "directly_matched_pairs": direct,
            "possible_pairs": possible,
            "note": "簇是传递闭包，成员之间不一定两两等价；请按 pair 逐对判断",
        })
    clusters.sort(key=lambda c: (-c["size"], c["candidate_cluster"]))
    return clusters


# ---------------------------------------------------------------------------
# 导入批专项
# ---------------------------------------------------------------------------


def find_import_manifest(out_dir: Path, project_root: Path) -> Path | None:
    cands = [
        project_root / "work" / "import_cats" / "manifest.json",
        out_dir.parent / "import_cats" / "manifest.json",
    ]
    for c in cands:
        if c.exists():
            return c
    return None


def import_check(records: list[dict[str, Any]], kb_dir: Path,
                 manifest_path: Path | None) -> dict[str, Any]:
    imp = [r for r in records if r["path"].startswith("_imported_cats/")]
    res: dict[str, Any] = {
        "manifest_path": str(manifest_path) if manifest_path else None,
        "manifest_loaded": False,
        "files_on_disk": len(imp),
        "manifest_entries": 0,
        "missing_in_fs": [],
        "unlisted_on_disk": [],
        "hash_mismatch": [],
        "category_mismatch": [],
        "license_field_missing": [],
        "source_field_missing": [],
        "short_docs": [],
        "fence_problems": [],
        "merge_boundary_suspects": [],
        "by_category": dict(Counter(r["category"] for r in imp)),
        "notes": [],
    }
    by_path = {r["path"]: r for r in imp}

    if manifest_path and manifest_path.exists():
        try:
            man = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            res["notes"].append(f"manifest 解析失败: {e}")
            man = {}
        files = man.get("files") or {}
        res["manifest_loaded"] = bool(files)
        res["manifest_entries"] = len(files)
        res["manifest_built_at"] = man.get("built_at")
        res["manifest_src"] = man.get("src")
        res["manifest_dedupe"] = man.get("dedupe")
        listed = set()
        for key, val in files.items():
            rel = key.replace("\\", "/").lstrip("/")
            listed.add(rel)
            rec = by_path.get(rel)
            if rec is None:
                res["missing_in_fs"].append(rel)
                continue
            exp = str((val or {}).get("body_sha256") or "")
            if exp and rec.get("body_sha256_raw") and exp != rec["body_sha256_raw"]:
                res["hash_mismatch"].append({
                    "path": rel, "manifest_body_sha256": exp,
                    "actual_body_sha256": rec["body_sha256_raw"],
                })
            cat = str((val or {}).get("category") or "")
            if cat and cat != rec["category"]:
                res["category_mismatch"].append(
                    {"path": rel, "manifest": cat, "frontmatter": rec["category"]})
        res["unlisted_on_disk"] = sorted(set(by_path) - listed)
    else:
        res["notes"].append("未找到导入 manifest，只做磁盘侧检查")

    for r in imp:
        if not r.get("license_field"):
            res["license_field_missing"].append(r["path"])
        elif not r.get("license_value"):
            res["license_field_missing"].append(r["path"])
        if not r.get("source"):
            res["source_field_missing"].append(r["path"])
        if r["body_chars"] < 400:
            res["short_docs"].append({"path": r["path"], "body_chars": r["body_chars"]})
        if r.get("fence_problems"):
            res["fence_problems"].append({"path": r["path"],
                                          "problems": r["fence_problems"]})
    res["short_docs"].sort(key=lambda x: x["body_chars"])

    # 合并边界嫌疑：正文里出现"多篇/多方向"拼接痕迹
    boundary_pat = re.compile(r"^(?:#+\s*)?(?:来源|原文链接|原文地址|阅读原文)\s*[:：]", re.M)
    for r in imp:
        p = kb_dir / r["path"]
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = len(boundary_pat.findall(text))
        if hits > 3:
            res["merge_boundary_suspects"].append({"path": r["path"], "boundary_lines": hits})
    return res


def stratified_sample(records: list[dict[str, Any]], size: int, seed: int,
                      strata_key: str = "category") -> dict[str, Any]:
    """确定性分层抽样：按 (类别, 来源域名) 分桶，桶键随机定序后轮转抽取。

    池子优先取导入批（``_imported_cats/``，277 篇）；该目录不存在时退回
    ``_imported/``，再退回全部可审计文档——否则换一个语料抽样结果会恒为空。
    """
    pool: list[dict[str, Any]] = []
    pool_source = "all"
    for prefix in ("_imported_cats/", "_imported/"):
        sub = [r for r in records if r["path"].startswith(prefix)]
        if sub:
            pool, pool_source = sub, prefix.rstrip("/")
            break
    if not pool:
        pool = [r for r in records if r.get("auditable")]
    buckets: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for r in pool:
        buckets[(r.get("category") or "(none)",
                 r.get("source_host") or "(no-host)")].append(r["path"])
    keys = sorted(buckets)
    rng = random.Random(seed)
    rng.shuffle(keys)
    picked: list[str] = []
    idx = 0
    while len(picked) < size and keys:
        key = keys[idx % len(keys)]
        bucket = sorted(buckets[key])
        take = bucket[(idx // len(keys)) % len(bucket)]
        if take not in picked:
            picked.append(take)
        idx += 1
        if idx > size * len(keys) * 2:
            break
    return {
        "seed": seed,
        "pool": pool_source,
        "strata_key": strata_key,
        "size_requested": size,
        "size_actual": len(picked),
        "strata": len(buckets),
        "algorithm": (
            "按 (category, source_host) 分桶 → 桶键用 random.Random(seed).shuffle 定序 → "
            "轮转每桶取第 n 个（桶内路径排序）→ 去重，直到达到 size。"
            "种子与算法固定即完全可复现。"
        ),
        "paths": picked,
    }


# ---------------------------------------------------------------------------
# 评测协议（只设计，不实施）
# ---------------------------------------------------------------------------


def eval_protocol() -> dict[str, Any]:
    return {
        "status": "designed_not_executed",
        "explicit_non_claims": [
            "本批未运行任何新评测，不声称检索指标提升",
            "不新增调参优化过的高分查询集",
            "不因当前检索结果反向修改已有 82 条查询",
        ],
        "frozen_before_measurement": [
            "查询集文件路径与 sha256 在采集后冻结",
            "采集样本与标注结果分开提交，标注在评测前完成",
        ],
        "collection": {
            "target_size": {"min": 120, "max": 160},
            "sources": [
                "真实用户提问（避开检索命中）：在未注入上下文的会话里记录原始问句",
                "第三方题库描述（与语料同域但不同来源）",
                "按类别配额：与 kb 实际分布对齐，薄类别设下限",
            ],
            "per_query_fields": [
                "query_id", "query_text", "category", "difficulty",
                "expected_doc_paths(>=1)", "acceptable_doc_paths",
                "must_not_return_paths", "rationale", "annotator", "annotated_at",
            ],
            "leakage_controls": [
                "查询文本不得直接粘贴目标文档标题或独特片段",
                "覆盖度检查：查询文本与目标文档的最长公共子串 < 12 字符",
                "对疑似泄漏条目单独标记 leaked_candidate 并整体剔除后再统计",
            ],
        },
        "annotation": {
            "labeling": "graded: 2=完整解题, 1=相关提示, 0=无关",
            "two_pass": "先盲标（不看检索结果），再抽 20% 双人复核，记录 kappa",
            "disagreement": "以复核标注为准，原始分歧保留在 annotation_log 字段",
        },
        "metrics": ["top1", "hit@5", "recall@5", "MRR", "ndcg@10"],
        "splits": {
            "protocol": "按类别分层 60/20/20（develop/frozen-test/holdout）",
            "rule": "frozen-test 与 holdout 只在最终评估时打开一次",
        },
        "next_batch_preconditions": [
            "Q3 只有在查询集文件 sha256 冻结后才允许试验分块/排序",
            "试验前后都必须报告同一冻结集的完整指标，禁止只报提升项",
        ],
    }


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------


def rule_catalog() -> list[dict[str, str]]:
    return [
        {"rule": "missing_front_matter", "method": "文件不以 --- 开头或 YAML 解析失败",
         "confidence": "高", "false_positive_boundary": "不判断内容质量；仅结构"},
        {"rule": "missing_source", "method": "front-matter 无 source 或为空",
         "confidence": "高（事实）", "false_positive_boundary":
         "不推断正文里是否有来源；缺失≠违规"},
        {"rule": "missing_license_field", "method": "无 license/origin_license 字段",
         "confidence": "高（字段缺失）", "false_positive_boundary":
         "字段存在≠已获许可；本工具从不推断许可状态"},
        {"rule": "unknown_verification", "method": "无任何 verification/repro/review 字段",
         "confidence": "高（unknown）", "false_positive_boundary":
         "未标注≠未复现；只在字段明确时读取"},
        {"rule": "fence_unclosed", "method": "CommonMark 围栏配对扫描（` 与 ~，长度≥开启）",
         "confidence": "高", "false_positive_boundary":
         "缩进代码块（4 空格）不算围栏；行内反引号不参与"},
        {"rule": "local_image_missing", "method": "相对路径图片引用解析到磁盘不存在",
         "confidence": "高", "false_positive_boundary":
         "绝对 URL 与 data: 不检查；大小写/构建期路径替换可能造成误报"},
        {"rule": "remote_image_unverified", "method": "图片指向 http(s)，未联网验证",
         "confidence": "仅线索", "false_positive_boundary":
         "不做网络请求，远端是否可访问未验证"},
        {"rule": "suspect_broken_image_dependency", "method":
         "正文有指代性表述（如图/下图）且图不可用",
         "confidence": "低（疑似）", "false_positive_boundary":
         "文学化用词会误报；必须人工看原文确认"},
        {"rule": "no_fenced_code", "method": "统计合法围栏块数量",
         "confidence": "高（事实）", "false_positive_boundary":
         "无围栏≠无代码（缩进块/纯文本 payload/外部链接）"},
        {"rule": "unreadable_or_decode_error", "method": "读取字节或 UTF-8 严格解码失败",
         "confidence": "高", "false_positive_boundary":
         "解码失败时用替换字符继续审计，内容可能已损坏"},
        {"rule": "exact_body_duplicate", "method": "去 front-matter 后正文 sha256 相同",
         "confidence": "高（等价副本）", "false_positive_boundary":
         "仅正文相同；元数据可能不同，是否保留是人工决策"},
        {"rule": "near_duplicate_candidate", "method":
         f"字符级 {SHINGLE_K}-shingle Jaccard / 包含度 + 长度预筛",
         "confidence": "中（候选）", "false_positive_boundary":
         "中文无分词、模板句多；同题不同解法会被判为包含关系"},
        {"rule": "same_url_clue", "method": "归一化 source URL 相同",
         "confidence": "仅线索", "false_positive_boundary":
         "通用首页 URL 一律不归并；同一 URL 可能对应多方向拆篇"},
    ]


def render_report(meta: dict[str, Any], stats: dict[str, Any],
                  inv_summary: dict[str, Any], dup: dict[str, Any],
                  imp: dict[str, Any], sample: dict[str, Any]) -> str:
    L: list[str] = []
    ap = L.append
    ap("# DB-Q1 知识库只读质量审计报告")
    ap("")
    ap(f"- 生成时间：{meta['generated_at']}")
    ap(f"- 项目：`{meta['project_root']}`")
    ap(f"- 收录规则：`kb.parser.iter_md_paths`（与索引同源）")
    ap(f"- 文档数：**{meta['doc_count']}**（预期 1844）")
    ap(f"- 总耗时：{meta['elapsed_seconds']} s；错误/异常条目：{meta['error_count']}")
    ap(f"- 输入未被修改：`{meta['input_unchanged']}`"
       f"（RUNNING）；跑完后请以 `compare-hash` 结果为准")
    ap("")
    ap("## 1. 规模与分布")
    ap("")
    ap("| 维度 | 值 |")
    ap("|---|---|")
    for k, v in inv_summary["counts"].items():
        ap(f"| {k} | {v} |")
    ap("")
    ap("按方向（front-matter category）：")
    ap("")
    ap("| 方向 | 篇数 |")
    ap("|---|---|")
    for k, v in sorted(inv_summary["by_category"].items(), key=lambda kv: -kv[1]):
        ap(f"| {k} | {v} |")
    ap("")
    ap(f"按顶层目录：{inv_summary['by_top_dir']}")
    ap("")
    ap("## 2. 质量规则与疑似问题")
    ap("")
    ap("每条规则的方法、置信度与误报边界见 `run_meta.json` 的 `rule_catalog`。"
       "下列数字**只有标『事实』的是可直接核实的事实**，其余为疑似。")
    ap("")
    ap("| 规则 | 命中篇数 | 性质 |")
    ap("|---|---|---|")
    for k, v in inv_summary["rule_hits"].items():
        ap(f"| {k} | {v} | {inv_summary['rule_nature'].get(k, '')} |")
    ap("")
    if inv_summary["top_examples"]:
        ap("证据示例（路径: 行号 / 片段）：")
        ap("")
        for line in inv_summary["top_examples"]:
            ap(f"- {line}")
        ap("")
    ap("## 3. 近似重复候选（不删除）")
    ap("")
    ap(f"- 精确正文副本组：**{dup['exact_groups']}** 组，涉及 "
       f"{dup['exact_docs']} 篇")
    ap(f"- 近似候选对：**{len(dup['pairs'])}** 对（阈值 jaccard≥"
       f"{dup['params']['min_shingle_jaccard']} 或 containment≥"
       f"{dup['params']['min_containment']}）")
    ap(f"- 候选簇（candidate_cluster）：**{len(dup['clusters'])}** 个")
    ap(f"- 同 URL 线索组：{len(dup['url_groups'])} 组")
    ap(f"- 候选生成：倒排累积出 {dup['stats']['pairs_scored']} 个共享 shingle 的文档对，"
       f"按逐对阈值下界过滤后 {dup['stats']['pairs_examined']} 对进入评分；"
       f"{dup['stats']['docs']} 篇参与")
    ap(f"- 候选上限触发："
       f"{'是（已截断，结果可能不全）' if dup['stats']['capped'] else '否（无截断，阈值以上的对全部评分）'}")
    ap(f"- 耗时：盘点 {stats['inventory_seconds']} s / 去重 {stats['dup_seconds']} s")
    ap("")
    ap("判读分布：")
    ap("")
    ap("| 判读 | 对数 |")
    ap("|---|---|")
    for k, v in sorted(dup["readout_counts"].items(), key=lambda kv: -kv[1]):
        ap(f"| {k} | {v} |")
    ap("")
    if dup["pairs"]:
        ap("Top 候选对（分数 / 判读 / 路径）：")
        ap("")
        for p in dup["pairs"][:25]:
            ap(f"- `{p['score']}` {p['readout']} — `{p['a']}` ↔ `{p['b']}`"
               f"（片段：{p['snippet'][:40]}）")
        ap("")
    ap("**这些候选一律不自动删除**：完整正文 vs 摘要卡、包含关系 vs 等价副本、"
       "同题不同解法必须人工分别判断。")
    ap("")
    ap("## 4. 导入批（277 篇）专项")
    ap("")
    ap(f"- manifest：`{imp['manifest_path']}`（载入={imp['manifest_loaded']}）")
    ap(f"- 磁盘篇数 {imp['files_on_disk']} / manifest 条目 {imp['manifest_entries']}")
    ap(f"- 清单缺文件：{len(imp['missing_in_fs'])}；未登记文件："
       f"{len(imp['unlisted_on_disk'])}")
    ap(f"- 正文哈希不一致：{len(imp['hash_mismatch'])}")
    ap(f"- 许可字段缺失：{len(imp['license_field_missing'])}；来源缺失："
       f"{len(imp['source_field_missing'])}")
    ap(f"- 异常短篇（<400 字）：{len(imp['short_docs'])}；围栏异常："
       f"{len(imp['fence_problems'])}；合并边界嫌疑："
       f"{len(imp['merge_boundary_suspects'])}")
    ap("")
    ap("## 5. 确定性分层抽样")
    ap("")
    ap(f"- 种子 {sample['seed']}，请求 {sample['size_requested']} 篇，"
       f"实得 {sample['size_actual']} 篇，分层数 {sample['strata']}")
    ap(f"- 算法：{sample['algorithm']}")
    ap("")
    ap("## 6. 规则误报边界与限制")
    ap("")
    ap("- 本批不联网：远端图片可用性、源站原文一致性均**未验证**。")
    ap("- 近似重复只做字符 shingle，不处理改写/翻译/重排；中文短篇的模板句会抬高分数。")
    ap("- 同一 URL 只作线索；通用首页 URL（如站点根、`/index.html`）一律不归并。")
    ap("- 元数据缺失与内容不合规严格分开：缺 license 字段不等于侵权，"
       "缺 verification 不等于未复现。")
    ap("- 解析失败/不可读文件单独列在 `run_meta.json.errors`，不静默跳过。")
    ap("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run_audit(*, project_root: Path, out_dir: Path, kb_dir: Path | None = None,
              min_shingle_jaccard: float = 0.7, min_containment: float = 0.75,
              sample_size: int = 24, seed: int = 20261101,
              max_pairs: int = 200000) -> dict[str, Any]:
    """跑完整审计并把结果写到 ``out_dir``。返回运行元数据。"""
    t0 = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if kb_dir is None:
        cfg = Config.load(project_root / "config.toml")
        kb_dir = cfg.kb_dir
    paths = list(iter_md_paths(kb_dir))

    t_inv = time.perf_counter()
    for p in paths:
        try:
            rec, errs = audit_doc(p, kb_dir)
        except Exception as e:  # noqa: BLE001 - 单篇失败不能毁掉整轮审计
            rec = {"path": p.relative_to(kb_dir).as_posix(), "auditable": False,
                   "error": "exception"}
            errs = [{"path": rec["path"], "stage": "audit",
                     "error": f"{type(e).__name__}: {e}",
                     "trace": traceback.format_exc(limit=3)}]
        records.append(rec)
        errors.extend(errs)
    inventory_seconds = round(time.perf_counter() - t_inv, 3)

    # 正文正规化与 shingle（失败也记录，不静默）
    body_cache: dict[str, str] = {}
    shingle_sets: dict[str, set[str]] = {}
    for r in records:
        if not r.get("auditable"):
            continue
        try:
            text = (kb_dir / r["path"]).read_text(encoding="utf-8", errors="replace")
            _, body = split_front_matter(text)
            norm = normalize_body(body)
        except Exception as e:  # noqa: BLE001
            errors.append({"path": r["path"], "stage": "normalize",
                           "error": f"{type(e).__name__}: {e}"})
            norm = ""
        r["norm"] = norm
        body_cache[r["path"]] = norm
        shingle_sets[r["path"]] = shingles(norm)

    t_dup = time.perf_counter()
    exact = find_exact_duplicates(records)
    pairs, dup_stats = find_near_duplicates(
        records, shingle_sets,
        min_shingle_jaccard=min_shingle_jaccard,
        min_containment=min_containment,
        candidate_cap=max_pairs,
    )
    dup_seconds = round(time.perf_counter() - t_dup, 3)

    recs_by_path = {r["path"]: r for r in records if r.get("auditable")}
    for p in pairs:
        p["readout"] = classify_pair(p, recs_by_path)
    clusters = build_clusters(pairs)

    url_groups = []
    by_url: defaultdict[str, list[str]] = defaultdict(list)
    for r in recs_by_path.values():
        key = r.get("source_group_key") or ""
        if key:
            by_url[key].append(r["path"])
    for key, members in sorted(by_url.items()):
        if len(members) > 1:
            url_groups.append({"url": key, "members": sorted(members),
                               "note": "同 URL 仅作线索；不据此认定同篇"})
    dup_bundle = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": started,
        "params": {
            "shingle_k": SHINGLE_K,
            "min_shingle_jaccard": min_shingle_jaccard,
            "min_containment": min_containment,
            "max_pairs": max_pairs,
            "normalization": "NFKC+去标点空白+去围栏标记+去 URL+小写",
        },
        "exact_groups": len(exact),
        "exact_docs": sum(g["size"] for g in exact),
        "exact_duplicates": exact,
        "pairs": pairs,
        "clusters": clusters,
        "url_groups": url_groups,
        "readout_counts": dict(Counter(p["readout"] for p in pairs)),
        "stats": dup_stats,
        "dup_seconds": dup_seconds,
    }

    imp = import_check(records, kb_dir, find_import_manifest(out_dir, project_root))
    sample = stratified_sample(records, sample_size, seed)
    for r in records:
        r.pop("norm", None)

    # ---- 汇总 ----
    by_cat = Counter(r["category"] for r in records if r.get("auditable"))
    by_top = Counter(r["path"].split("/")[0] for r in records)
    rule_hits: dict[str, int] = {
        "缺少 front-matter": sum(
            1 for r in records if r.get("front_matter_error", "").startswith("缺少")),
        "front-matter YAML 解析失败": sum(
            1 for r in records
            if r.get("front_matter_error", "").startswith("front-matter YAML 解析失败")),
    }
    rule_nature = {
        "缺少 front-matter": "事实",
        "front-matter YAML 解析失败": "事实（语法错误；索引侧会整块丢弃元数据）",
        "缺少 source 字段": "事实（缺失）",
        "缺少 license 字段": "事实（缺失，不等于侵权）",
        "verification 状态 unknown": "事实（unknown）",
        "围栏未闭合（`/~~~）": "事实",
        "本地图片缺失": "事实",
        "远端图片未验证": "仅线索",
        "正文疑似依图但图不可用": "疑似（需人工）",
        "无合法围栏代码块": "事实（不等于无代码）",
        "不可读 / 解码失败": "事实",
        "类别不在白名单": "事实",
    }
    rule_hits["缺少 source 字段"] = sum(1 for r in records
                                     if r.get("auditable") and not r["source"])
    rule_hits["缺少 license 字段"] = sum(
        1 for r in records if r.get("auditable") and not r["license_field"])
    rule_hits["verification 状态 unknown"] = sum(
        1 for r in records if r.get("auditable") and not r["verification_field"])
    rule_hits["围栏未闭合（`/~~~）"] = sum(
        1 for r in records if any(p["kind"] == "unclosed_fence"
                                  for p in r.get("fence_problems", [])))
    rule_hits["本地图片缺失"] = sum(
        1 for r in records if r.get("images", {}).get("local_missing"))
    rule_hits["远端图片未验证"] = sum(
        1 for r in records if r.get("images", {}).get("remote_unverified"))
    rule_hits["正文疑似依图但图不可用"] = sum(
        1 for r in records if r.get("images", {}).get("suspect_broken_image_dependency"))
    rule_hits["无合法围栏代码块"] = sum(
        1 for r in records if r.get("auditable") and not r.get("has_code"))
    rule_hits["不可读 / 解码失败"] = sum(
        1 for e in errors if e["stage"] in ("read", "decode"))
    rule_hits["类别不在白名单"] = sum(
        1 for r in records if r.get("auditable") and not r.get("category_valid"))

    examples: list[str] = []
    for r in records:
        fme = r.get("front_matter_error", "")
        if fme:
            examples.append(f"`{r['path']}` — {fme}")
    for r in records:
        for pb in r.get("fence_problems", [])[:1]:
            examples.append(f"`{r['path']}` — {pb['detail']}")
    for r in records:
        miss = r.get("images", {}).get("local_missing") or []
        if miss:
            examples.append(f"`{r['path']}` — 本地图片不存在: {miss[:2]}")
    for e in errors[:10]:
        if e["stage"] in ("read", "decode", "audit", "normalize"):
            examples.append(f"`{e['path']}` — {e['stage']} 失败: {e['error']}")

    inv_summary = {
        "counts": {
            "Markdown 文件（收录规则内）": len(paths),
            "可审计篇目": sum(1 for r in records if r.get("auditable")),
            "存在 front-matter 错误": (rule_hits["缺少 front-matter"]
                                    + rule_hits["front-matter YAML 解析失败"]),
            "有 fenced code": sum(1 for r in records
                                  if r.get("auditable") and r.get("has_code")),
            "解析/读取异常条目": len(errors),
        },
        "by_category": dict(by_cat),
        "by_top_dir": dict(by_top),
        "rule_hits": rule_hits,
        "rule_nature": rule_nature,
        "top_examples": examples[:40],
    }

    meta = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": started,
        "project_root": str(project_root),
        "kb_dir": str(kb_dir),
        "out_dir": str(out_dir),
        "doc_count": len(paths),
        "expected_doc_count": 1844,
        "matches_expected": len(paths) == 1844,
        "error_count": len(errors),
        "errors": errors,
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "input_unchanged": "verified_by_compare-hash",
        "read_only_guarantees": [
            "不写 kb/、index/、config.toml",
            "只调用 kb.parser 读取接口",
            "所有输出落在 --out-dir",
        ],
        "rule_catalog": rule_catalog(),
        "params": {
            "min_shingle_jaccard": min_shingle_jaccard,
            "min_containment": min_containment,
            "sample_size": sample_size,
            "seed": seed,
            "max_pairs": max_pairs,
        },
        "timings": {"inventory_seconds": inventory_seconds,
                    "dup_seconds": dup_seconds},
    }

    # ---- 落盘 ----
    with (out_dir / "inventory.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in sorted(records, key=lambda x: x["path"]):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    _write_json(out_dir / "duplicate_candidates.json", dup_bundle)
    _write_json(out_dir / "import_check.json", imp)
    _write_json(out_dir / "eval_protocol.json", eval_protocol())
    _write_json(out_dir / "run_meta.json", meta)
    _write_json(out_dir / "sample_plan.json", sample)
    (out_dir / "report.md").write_text(
        render_report(meta, {
            "inventory_seconds": inventory_seconds,
            "dup_seconds": dup_seconds,
        }, inv_summary, dup_bundle, imp, sample),
        encoding="utf-8", newline="\n",
    )
    return meta


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
                    encoding="utf-8", newline="\n")


def snapshot_hashes(root: Path, subdirs: Sequence[str] | Sequence[Path] = ("kb",),
                    *, absolute_keys: bool = False) -> dict[str, str]:
    """对若干子树做逐文件 sha256。

    默认键是相对 ``root`` 的 POSIX 路径（真实语料里就是 ``kb/...``）；
    ``absolute_keys=True`` 时键是绝对 POSIX 路径，用于 --kb-dir 指向别处的场景。
    """
    out: dict[str, str] = {}
    for sub in subdirs:
        base = Path(sub) if Path(sub).is_absolute() else root / Path(sub)
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file():
                key = p.resolve().as_posix() if absolute_keys else p.relative_to(root).as_posix()
                out[key] = sha256_file(p)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    # Windows 控制台默认是 GBK，报告里有 →/⊂/「」等字符，输出前统一切成 UTF-8
    for stream in (sys.stdout, sys.stderr):
        try:
            if (stream.encoding or "").lower().replace("-", "") not in ("utf8", "utf8mb4"):
                stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        prog="audit_corpus.py",
        description="DB-Q1 只读语料质量审计与近似去重候选（不修改 kb/index/config，"
                    "不联网，不重排索引）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  .\\.venv\\Scripts\\python.exe tools\\audit_corpus.py\n"
               "  .\\.venv\\Scripts\\python.exe tools\\audit_corpus.py "
               "--min-jaccard 0.5 --sample-size 30 --seed 7\n"
               "  .\\.venv\\Scripts\\python.exe tools\\audit_corpus.py compare-hash "
               "--before work\\db_quality1\\hash_before.json\n",
    )
    ap.add_argument("--project-root", default=str(TOOLS_DIR.parent),
                    help="项目根目录（默认取本脚本上一级）；子命令也可用（需写在子命令前）")
    ap.add_argument("--kb-dir", default=None,
                    help="知识库目录（默认按 config.toml 解析）")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                    help=f"输出目录（相对项目根；默认 {DEFAULT_OUT_DIR}）")
    ap.add_argument("--min-jaccard", type=float, default=0.7,
                    help="近似重复的 shingle Jaccard 阈值（默认 0.7，保守；"
                         "调低到 0.6 会让同模板不同解法的文档涌入候选）")
    ap.add_argument("--min-containment", type=float, default=0.75,
                    help="包含度阈值，用于摘要卡⊂全文（默认 0.75）")
    ap.add_argument("--max-pairs", type=int, default=200000,
                    help="候选对内存保险上限（默认 200000）；正常语料的候选由"
                         "阈值下界过滤，不靠截断，触发该上限会在报告里显式告警")
    ap.add_argument("--sample-size", type=int, default=24,
                    help="导入批分层抽样篇数（默认 24，≥20）")
    ap.add_argument("--seed", type=int, default=20261101,
                    help="分层抽样种子（默认 20261101；固定即完全可复现）")
    ap.add_argument("--hash-before", action="store_true",
                    help="运行前先落 hash_before.json（kb 逐文件 sha256）")
    sub = ap.add_subparsers(dest="command")
    cp = sub.add_parser("compare-hash", help="比较运行前后的 kb 字节哈希，证明未改正文")
    cp.add_argument("--before", required=True, help="运行前快照 json")
    cp.add_argument("--after-out", default=None, help="运行后快照落盘路径（可选）")
    args = ap.parse_args(argv)

    root = Path(args.project_root).resolve()
    # kb_dir 在子命令分支之前就要解析：compare-hash 也要用同一个目录
    kb_dir = Path(args.kb_dir).resolve() if args.kb_dir else (root / "kb")

    if args.command == "compare-hash":
        before_path = Path(args.before)
        before = json.loads(before_path.read_text(encoding="utf-8"))
        before_map = before["files"] if "files" in before else before
        after_kb = snapshot_hashes(root, (kb_dir,), absolute_keys=True)
        added = sorted(set(after_kb) - set(before_map))
        removed = sorted(set(before_map) - set(after_kb))
        changed = sorted(k for k in set(before_map) & set(after_kb)
                         if before_map[k] != after_kb[k])
        result = {
            "unchanged": not (added or removed or changed),
            "kb_dir": str(kb_dir.resolve()),
            "checked_files": len(after_kb),
            "added": added, "removed": removed, "changed": changed,
        }
        if args.after_out:
            _write_json(Path(args.after_out), {"files": after_kb})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["unchanged"] else 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    if args.hash_before:
        snap = snapshot_hashes(root, (kb_dir,), absolute_keys=True)
        _write_json(out_dir / "hash_before.json", {"files": snap, "kb_dir": str(kb_dir)})
        print(f"hash_before.json: {len(snap)} files -> {out_dir}")

    meta = run_audit(
        project_root=root, out_dir=out_dir, kb_dir=kb_dir,
        min_shingle_jaccard=args.min_jaccard,
        min_containment=args.min_containment,
        sample_size=args.sample_size, seed=args.seed, max_pairs=args.max_pairs,
    )
    print(f"docs={meta['doc_count']} errors={meta['error_count']} "
          f"elapsed={meta['elapsed_seconds']}s -> {out_dir}")
    if not meta["matches_expected"]:
        print(f"[warn] 收录篇数 {meta['doc_count']} != 预期 1844，"
              f"请核对 config 与收录规则（不硬凑）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

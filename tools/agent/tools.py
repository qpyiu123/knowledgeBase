"""Agent 的三个工具：查知识库、读文件、写文件。

安全约束（本机 agent，但仍要防止模型乱跑）：
- 所有文件路径被限制在 WORKSPACE 内（默认 E:\\CTF\\knowledgeBase\\work）
- 读文件额外允许 kb/ 与 index/ 只读访问
- 拒绝绝对路径逃逸、拒绝 .. 穿越、拒绝写 .venv / models / tools
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "work"
KB_DIR = ROOT / "kb"

# 允许读取的额外根目录（只读）
READ_ROOTS = [WORKSPACE, KB_DIR, ROOT / "index"]
# 允许写入的根目录
WRITE_ROOTS = [WORKSPACE]

MAX_READ_BYTES = 200_000
ALLOWED_READ_EXT = {
    ".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml",
    ".c", ".cpp", ".h", ".sh", ".ps1", ".bat", ".html", ".css", ".csv",
    ".log", ".ini", ".cfg", ".xml", ".sql", ".java", ".go", ".rs", ".php",
}
MAX_WRITE_BYTES = 200_000


@dataclass
class ToolResult:
    ok: bool
    content: str


# ------------------------------------------------------------------ 安全路径
def _roots(read: bool) -> list[Path]:
    """运行时读取根目录列表（不要写成模块级常量再在函数里直接用，
    否则测试和运行期改配都不生效）。"""
    if read:
        return list(globals()["READ_ROOTS"])
    return list(globals()["WRITE_ROOTS"])


def _resolve(p: str, roots: list[Path]) -> Path:
    if not p or not isinstance(p, str):
        raise ValueError("路径不能为空")
    raw = Path(p.strip().strip('"').strip("'"))
    parts = raw.parts
    base = roots[0].resolve() if roots else ROOT

    # 剥掉开头的 work/ —— 用户和模型都爱写 work/exp.py，
    # 而 WORKSPACE 本身就是那个目录，不剥会变成 work/work/exp.py
    if len(parts) > 1 and parts[0].lower() == "work":
        raw = Path(*parts[1:])
        parts = raw.parts

    if raw.is_absolute():
        target = raw.resolve()
        for r in roots:
            try:
                target.relative_to(r.resolve())
                return target
            except ValueError:
                continue
        raise PermissionError(f"路径越界: {p} —— 只允许访问 {', '.join(str(r) for r in roots)}")

    # 相对路径：先试 ROOT（能命中 kb/xx.md 这种），再试 roots[0]（workspace）
    for base_dir in (ROOT, base):
        cand = (base_dir / raw).resolve()
        for r in roots:
            try:
                cand.relative_to(r.resolve())
                return cand
            except ValueError:
                continue
    # 最后一律落到 workspace 下（新建文件走这里）
    cand = (base / raw).resolve()
    try:
        cand.relative_to(base)
        return cand
    except ValueError:
        raise PermissionError(
            f"路径越界: {p} —— 只允许访问 {', '.join(str(r) for r in roots)}"
        ) from None


# ------------------------------------------------------------------ 工具 1
def search_kb(query: str, category: str | None = None, top_k: int = 4) -> ToolResult:
    """查本地 CTF 知识库，返回标题 + 路径 + 摘要片段。"""
    if not query or not str(query).strip():
        return ToolResult(False, "query 不能为空")
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from kb.config import Config
    from kb.rag import KB

    cfg = Config.load()
    kb = KB(cfg)
    cats = {"misc", "crypto", "reverse", "pwn", "web", "forensics",
            "mobile", "blockchain", "hardware", "osint", "ai"}
    cat = category if category in cats else None

    hits = kb.search(str(query), top_k=int(top_k or 4), category=cat)
    if not hits:
        return ToolResult(True, "知识库没有命中。可以换个说法再查，或直接给通用经验。")

    out = [f"查询: {query}  命中 {len(hits)} 条\n"]
    for i, h in enumerate(hits, 1):
        out.append(f"{i}. 【{h.category}】{h.title}")
        out.append(f"   路径: {h.doc_path}")
        f = KB_DIR / h.doc_path
        if f.exists():
            body = f.read_text(encoding="utf-8", errors="replace")
            # 取「识别信号」或开头部分，帮模型判断是否同题
            sig = _extract_section(body, ("识别信号", "题目要点", "原理"))
            if sig:
                out.append(f"   要点: {sig[:400]}")
        if h.best_text:
            snippet = " ".join(h.best_text.split())[:200]
            out.append(f"   片段: {snippet}")
        out.append("")
    out.append("提示：需要完整内容就用 read_file 读对应 .md 路径。")
    return ToolResult(True, "\n".join(out))


def _extract_section(body: str, keys: tuple[str, ...]) -> str:
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#") and any(k in ln for k in keys):
            buf = []
            for nxt in lines[i + 1:]:
                if nxt.lstrip().startswith("#"):
                    break
                if nxt.strip():
                    buf.append(nxt.strip())
                if len(buf) >= 6:
                    break
            if buf:
                return " ".join(buf)
    return ""


# ------------------------------------------------------------------ 路径纠错
def _fuzzy_find(path: str) -> Path | None:
    """在知识库里按文件名找目标，容忍丢掉 kb/ 前缀或写错子目录。"""
    name = Path(path.strip().strip('"').strip("'")).name
    if not name:
        return None
    kb = Path(globals()["KB_DIR"])
    if not kb.exists():
        return None

    def safe(p: Path) -> bool:
        try:
            p.resolve().relative_to(kb.resolve())
            return True
        except ValueError:
            return False

    exact = list(kb.rglob(name))
    exact = [p for p in exact if p.is_file() and safe(p)]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return exact[0]

    stem = Path(name).stem.lower()
    if len(stem) >= 4:
        loose = [p for p in kb.rglob("*.md")
                 if p.is_file() and safe(p) and stem in p.stem.lower()]
        if len(loose) >= 1:
            return loose[0]
    return None


# ------------------------------------------------------------------ 工具 2
def read_file(path: str, max_lines: int = 200) -> ToolResult:
    try:
        target = _resolve(path, _roots(True))
    except (ValueError, PermissionError) as e:
        return ToolResult(False, str(e))
    if not target.exists():
        # 小模型常把 kb/ 前缀吃掉，写成 crypto/xxx.md。
        # 与其让它失败后凭记忆瞎编，不如在这里帮忙找回来。
        alt = _fuzzy_find(path)
        if alt is not None:
            target = alt
        else:
            return ToolResult(False, f"文件不存在: {path}")
    if not target.is_file():
        return ToolResult(False, f"不是文件: {path}")
    if target.suffix.lower() not in ALLOWED_READ_EXT:
        return ToolResult(False, f"该扩展名不允许读取: {target.suffix}（支持 {len(ALLOWED_READ_EXT)} 种文本格式）")
    size = target.stat().st_size
    if size > MAX_READ_BYTES:
        return ToolResult(False, f"文件太大 ({size} 字节)，上限 {MAX_READ_BYTES}")
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    lim = max(1, min(int(max_lines or 200), 1000))
    if len(lines) > lim:
        body = "\n".join(lines[:lim])
        return ToolResult(True, f"{target}（共 {len(lines)} 行，显示前 {lim} 行）\n{body}")
    return ToolResult(True, f"{target}\n{text}")


def _unescape_body(s: str) -> str:
    """把 JSON 里转义过的 content 还原成真实文本。

    坑：小模型把工具调用当文本吐时，content 常是**双重转义**的
    （`\\n` 而不是 `\n`），直接写入会把整段脚本写成一行，
    文件语法错误。这里做保守的多轮还原：
      - 如果字符串里没有任何真实换行，但有字面量的 \\n，就还原
      - 同时还原 \\t、\\" 和 \\\\ 
    """
    if not s:
        return s
    has_real_nl = "\n" in s
    has_escaped_nl = "\\n" in s
    if has_escaped_nl and (not has_real_nl or s.count("\\n") > s.count("\n")):
        s = s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
    s = s.replace('\\"', '"')
    s = s.replace("\\\\", "\\") if "\\\\" in s and not re.search(r"\\[nrt]", s) else s
    return s


# ------------------------------------------------------------------ 工具 3
def write_file(path: str, content: str) -> ToolResult:
    try:
        target = _resolve(path, _roots(False))
    except (ValueError, PermissionError) as e:
        return ToolResult(False, f"{e}\n（只能写到 work/ 目录下，例如 work/exp.py）")
    if not target.suffix:
        target = target.with_suffix(".py")
    if target.suffix.lower() not in ALLOWED_READ_EXT:
        return ToolResult(False, f"不允许写该扩展名: {target.suffix}")
    data = _unescape_body(content or "")
    if len(data.encode("utf-8")) > MAX_WRITE_BYTES:
        return ToolResult(False, f"内容太大，上限 {MAX_WRITE_BYTES} 字节")
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(data, encoding="utf-8")
    verb = "已覆盖" if existed else "已创建"
    return ToolResult(True, f"{verb}: {target}  ({len(data)} 字符)")


# ------------------------------------------------------------------ 注册表
TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": (
                "查询本地 CTF 知识库（141 篇，覆盖 misc/crypto/reverse/pwn/web/"
                "forensics/mobile/blockchain/hardware/osint/ai）。"
                "做题时第一步就该调用它，把题面里的特征词作为 query。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "题面特征词，如「n相同 e不同 两组密文」「上传文件 能访问」",
                    },
                    "category": {
                        "type": "string",
                        "description": "可选，限定方向。不确定就别填。",
                        "enum": ["misc", "crypto", "reverse", "pwn", "web",
                                 "forensics", "mobile", "blockchain",
                                 "hardware", "osint", "ai"],
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取工作区里的文本文件。可以读 kb/ 下的知识库条目、work/ 下自己写的脚本。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对路径，如 kb/crypto/rsa-common-modulus-attack.md 或 work/exp.py",
                    },
                    "max_lines": {"type": "integer", "description": "最多读多少行，默认 200"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "把脚本或笔记写到 work/ 目录。用户会拿到文件路径。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对路径，如 work/exp.py"},
                    "content": {"type": "string", "description": "文件完整内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
]

_DISPATCH = {
    "search_kb": search_kb,
    "read_file": read_file,
    "write_file": write_file,
}


def dispatch(name: str, args: dict) -> ToolResult:
    fn = _DISPATCH.get(name)
    if fn is None:
        return ToolResult(False, f"未知工具: {name}。可用：{', '.join(_DISPATCH)}")
    if not isinstance(args, dict):
        return ToolResult(False, "参数必须是对象")
    try:
        return fn(**args)
    except TypeError as e:
        return ToolResult(False, f"参数不匹配: {e}")
    except Exception as e:  # noqa: BLE001
        return ToolResult(False, f"{type(e).__name__}: {e}")


WORKSPACE.mkdir(parents=True, exist_ok=True)

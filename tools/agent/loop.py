"""轻量 CTF Agent —— 核心。

设计原则（针对 4GB 显存 / 18 tok/s 的本地 7B 模型）：
1. **工具极少**：只有 3 个（查知识库、读文件、写文件）。工具定义越少，
   system prompt 越短，6K 上下文的利用率越高。
2. **单步 ReAct**：每轮最多调用一个工具，不做并行批处理——
   小模型处理多工具返回时容易格式崩坏。
3. **结果截断**：工具输出统一截到 2000 字符，避免一次把上下文撑爆。
4. **失败可恢复**：工具异常不中断循环，把错误信息作为 observation 喂回去。

用法：
    from agent.tools import TOOLS
    loop = AgentLoop()
    for ev in loop.run("帮我找找这道题的解法", ...):
        print(ev)
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]

SYSTEM_PROMPT = """你是 CTF 解题助手，运行在用户的 Windows 本机上。

你有六个工具：
【侦察附件】
- list_files(directory)        列出目录里的文件（含类型判断）
- probe_file(path)             自动侦察：真实类型/大小/内嵌文件/可读字符串
- run_tool(tool, path)         调用 file/binwalk/strings/exiftool/zsteg 等
【查资料与落盘】
- search_kb(query, category?)  查本地 CTF 知识库（241 篇，11 个方向）
- read_file(path)              读知识库条目或 work/ 里的文本文件
- write_file(path, content)    把脚本/笔记写到 work/ 目录

**关键：真实比赛的题面通常几乎没有信息。**
「flag 藏在这里，快去找」这种话是废话，不要根据它猜方向。

正确的解题流程：
1. 用户提到附件、或者题面没什么信息 → **第一步必须 list_files("work")**
   看看到底给了什么文件。
2. 对每个附件调用 **probe_file**。它会告诉你：
   - 真实类型（看魔数，不看扩展名——扩展名经常是假的）
   - 有没有内嵌/追加的其它文件
   - 里面有哪些可读字符串（含 flag/key/pass 等关键词的会排前面）
3. 根据 probe_file 的结果判断方向，再决定下一步：
   - 发现 ZIP/PNG 等 → run_tool("binwalk", path) 看能否分离出文件
   - 是图片 → run_tool("exiftool", path) 或 run_tool("zsteg", path)
   - 是 ELF/PE → 属于 reverse/pwn，转去 search_kb
4. 拿到线索后 search_kb 找对应技法，read_file 读全文。
5. 需要写脚本时 write_file 到 work/。

**禁止**：
- 不要因为题面没信息就反问用户「请提供更多信息」。
  你有侦察工具，自己去找线索。
- 不要在没看附件的情况下猜题型。
- 不要编造不存在的工具用法（例如 phpggc 的语法）。
  不确定就说不确定。
- 不要凭记忆写加解密公式，必须 read_file 读到知识库里的模板。

回答用中文，代码块标注语言。"""


# ------------------------------------------------------------------ 事件
@dataclass
class Event:
    kind: str          # token | tool_call | tool_result | done | error
    data: Any = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "data": self.data, **self.extra}


# ------------------------------------------------------------------ 光说不做检测
_STALL_PATTERNS = re.compile(
    r"(我先|我来|让我|现在|接下来).{0,12}(读|查|看|检索|打开|获取|调用)|"
    r"(读取|查询|检索)(一下|该|相关|那个|对应)|"
    r"(请将?|你需要|你可以|用户可以|自行).{0,24}(保存|写入|存到|存为|复制)|"
    r"(保存到|写入到|存到)\s*[`'\"]?\S+\.(py|sh|ps1|js|txt|md)"
)
_IDLE = re.compile(r"^(好的|好|OK|嗯|明白|收到)[，,。.!！\s]*$")

# 把球踢回给用户（反问 / 请求更多信息），而不是给出结论
_PUNT = re.compile(
    r"(请问|请提供|请告诉|需要您|您需要|您想|是否|要不要|"
    r"可以告诉我|能提供|请描述|请补充|what would you|please provide)",
    re.I,
)


def _list_embedded_hints(probe_output: str) -> list[str]:
    """从 probe_file 的输出里抽出「偏移处的内嵌文件」列表。"""
    out = []
    for line in (probe_output or "").splitlines():
        m = re.search(r"(0x[0-9a-f]+)\s*偏移[:：]\s*(\w+)", line)
        if m:
            out.append(f"{m.group(1)}({m.group(2)})")
    return out



def _extract_attachment_paths(prompt: str) -> list[str]:
    """从题面里提取明确点名的附件路径。

    支持：
      附件：work/attachments/locked.zip
      附件: xxx.zip
      附件放在 work/attachments/ 目录下   （目录形式）
    返回可用的相对路径列表。
    """
    out: list[str] = []
    if not prompt:
        return out
    # 明确文件路径
    for m in re.finditer(
            r"附件[：:\s]*([\w./\\-]+\.(?:zip|rar|7z|tar|gz|png|jpg|jpeg|gif|bmp|"
            r"bin|wav|mp3|pdf|pcap|cap|img|txt|exe|elf))", prompt, re.I):
        p = m.group(1).replace("\\", "/")
        if p not in out:
            out.append(p)
    return out

def _pick_attachment(list_output: str) -> str | None:
    """从 list_files 的输出里挑一个最像"附件"的文件路径。"""
    best = None
    for line in (list_output or "").splitlines():
        m = re.search(r"\[FILE\]\s+(\S+)", line)
        if not m:
            continue
        name = m.group(1)
        low = name.lower()
        # 跳过日志/中间产物
        if low.endswith((".log", ".json", ".pid")):
            continue
        # 优先带附件特征的
        if low.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".zip",
                         ".rar", ".7z", ".bin", ".wav", ".mp3", ".pdf",
                         ".pcap", ".cap", ".gz", ".tar", ".txt", ".img")):
            # 从输出里推断所在目录
            dm = re.search(r"目录\s+(\S+?)（", list_output)
            base = dm.group(1) if dm else "work"
            base = base.replace("\\", "/").rstrip("/")
            rel = base.split("knowledgeBase")[-1].lstrip("/")
            cand = f"{rel}/{name}" if rel else name
            if best is None or ".bin" in low or ".zip" in low:
                best = cand
    return best


def _mentions_pending_tool(text: str) -> str | None:
    """模型在回答里提到「应该用 xxx 工具」，但实际没调 —— 返回那个工具名。

    实测失败形态：
      「1) 判断：未知  2) 关键步骤：对导出文件使用 probe_file 分析」
    模型把"下一步该干什么"当成答案交了出去。
    """
    t = (text or "").strip()
    if len(t) > 900:
        return None
    for name in KNOWN_TOOLS:
        if name in t:
            # 排除"已经完成"的描述
            if re.search(r"(已|刚刚|成功).{0,10}" + re.escape(name), t):
                continue
            return name
    return None


def _is_punting(text: str) -> bool:
    """判断模型是不是在反问/踢皮球，而不是给结论。

    短文本 + 出现疑问/请求句式 => 视为踢皮球。
    正常的长回答里偶尔出现"请问"不算。
    """
    t = (text or "").strip()
    if len(t) > 150:
        return False
    return bool(_PUNT.search(t)) or t.endswith(("？", "?"))

# 用户明确要求落盘
_WANTS_FILE = re.compile(
    r"(保存到|写到|存到|存为|写成文件|生成文件|落盘|写个脚本|写一个脚本|"
    r"给我脚本|要能直接运行|save\s+to)",
    re.I,
)


def _wants_file(prompt: str) -> bool:
    return bool(_WANTS_FILE.search(prompt or ""))


def _is_stalling(text: str) -> bool:
    """判断模型是不是"光说要做事，实际没调工具"。

    满足任一即视为停滞：
      - 正文很短且是「好的/明白」之类的附和
      - 出现「我先读取…」「让我查一下…」但没有工具调用
      - 让用户自己保存/复制脚本（把该做的事推给用户）
    真正的最终回答通常较长，不会被误判。
    """
    t = (text or "").strip()
    if len(t) < 4:
        return True
    if _IDLE.match(t):
        return True
    # 出现「请将脚本保存到 xxx.py」这类甩锅话术，不管多长都算停滞
    if re.search(r"(请|你需要|你可以|自行).{0,24}(保存|写入|存到|存为)", t):
        return True
    if len(t) <= 120 and _STALL_PATTERNS.search(t):
        return True
    return False


def _ollama_safe_call(call: dict) -> dict:
    """把一条 tool_call 规范成 Ollama 能接受的形状（arguments 为对象）。"""
    fn = dict(call.get("function") or {})
    args = fn.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    if not isinstance(args, dict):
        args = {}
    fn["arguments"] = args
    out = {"function": fn}
    if call.get("id"):
        out["id"] = call["id"]
    out["type"] = "function"
    return out


# ------------------------------------------------------------------ 文本兜底
# 模型把工具调用当文本吐出时形状很随意，这里要放宽：
#   ```json {"name": ...} ```   /  裸 {"name": ...}
#   {"tool": ...}               /  {"function": {"name": ...}}
# 关键：content 里可能塞了几千字符的脚本，JSON 会跨很多行，
# 所以必须非贪婪 + DOTALL，且不能因为文本长就跳过解析。
_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)
_BARE_JSON = re.compile(
    r'(\{\s*"(?:name|tool|function)"\s*:.*?\})(?=\s*(?:\n\s*\n|```|$))', re.S
)
# 兜底：JSON 被截断、没有收尾括号时，至少能识别出工具名
_TRUNCATED = re.compile(
    r'\{\s*"(?:name|tool)"\s*:\s*"(search_kb|read_file|write_file)"', re.S
)
# 兜底 2：模型把工具调用写成 **Python 函数调用**语法，
# 例如 write_file("work/exp.py", "...")  或  search_kb(query="...")
KNOWN_TOOLS = (
    "list_files", "probe_file", "run_tool", "extract_embedded", "extract_zip", "extract_gzip",
    "suggest_directions",
    "search_kb", "read_file", "write_file",
)

# 这是 7B 模型非常常见的行为，必须识别，否则任务会在最后一步卡死。
# 注意：参数里可能含括号（print(1)），所以不能简单用 [^)]*。
_PY_HEAD = re.compile(
    r"(?:^|[\n`\s])(" + "|".join(KNOWN_TOOLS) + r")\s*\(",
    re.S,
)
_PY_KWARG = re.compile(r"(\w+)\s*=\s*(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|)`?", re.S)


def _parse_text_tool_calls(text: str) -> list[dict]:
    """从纯文本里捞取工具调用。

    兼容这几种模型实际吐出来的形状：
        ```json {"name":"search_kb","arguments":{...}} ```
        {"name": "search_kb", "arguments": {...}}
        {"tool": "search_kb", "args": {...}}
        {"function": {"name": "...", "arguments": {...}}}

    注意 content 里可能包含完整脚本（几千字符、含换行），
    所以不能用"短文本才解析"的启发式，必须 DOTALL 扫全篇。
    """
    if not text or not any(t in text for t in KNOWN_TOOLS):
        return []

    # 先试 Python 函数调用语法（write_file("x", "...")），
    # 因为 ```python ... ``` 代码块会被 _JSON_BLOCK 当成 ```json 抢走。
    py = _parse_python_call(text)

    chunks = [m.group(1) for m in _JSON_BLOCK.finditer(text)]
    if not chunks:
        chunks = [m.group(1) for m in _BARE_JSON.finditer(text)]

    out: list[dict] = []
    for raw in chunks:
        obj = _loads_lenient(raw)
        if obj is None:
            continue
        call = _coerce_call(obj)
        if call:
            out.append(call)
            break          # 单步：只取第一个

    if not out and py:
        out.append(py)
    if not out:
        # 兜底 2：Python 函数调用语法
        call = _parse_python_call(text)
        if call:
            out.append(call)

    if not out:
        # 最后兜底：JSON 被 max_tokens 截断，只能识别出工具名再抢救参数
        m = _TRUNCATED.search(text)
        if m:
            name = m.group(1)
            args = _salvage_args(text[m.start():], name)
            if args is not None:
                out.append({
                    "function": {"name": name,
                                 "arguments": json.dumps(args, ensure_ascii=False)}
                })
    return out


def _parse_python_call(text: str) -> dict | None:
    """识别 `write_file("work/exp.py", content)` 这种 Python 调用写法。

    参数可能是关键字形式 `path="x"` 或位置形式 `("x", "...")`。
    变量名（如 common_modulus_script）解析不出来，返回 None 交回上层。
    """
    for m in _PY_HEAD.finditer(text):
        name = m.group(1)
        argstr = _match_paren(text, m.end() - 1)
        if argstr is None:
            continue
        # 关键字参数
        kwargs = {}
        for km in _PY_KWARG.finditer(argstr):
            try:
                kwargs[km.group(1)] = _py_literal(km.group(2))
            except Exception:  # noqa: BLE001
                pass
        if kwargs:
            need = {"search_kb": ["query"], "read_file": ["path"],
                    "write_file": ["path", "content"],
                    "probe_file": ["path"], "list_files": [],
                    "run_tool": ["tool", "path"]}[name]
            if all(k in kwargs for k in need):
                return {"function": {"name": name,
                                     "arguments": json.dumps(kwargs, ensure_ascii=False)}}
            continue

        # 位置参数
        vals = []
        for p in _split_args(argstr):
            p = p.strip()
            if len(p) >= 2 and p[0] in "'\"" and p[-1] == p[0]:
                try:
                    vals.append(_py_literal(p))
                except Exception:  # noqa: BLE001
                    vals = []
                    break
            else:
                vals = []
                break
        if name == "search_kb" and len(vals) >= 1:
            return {"function": {"name": name,
                                 "arguments": json.dumps({"query": vals[0]}, ensure_ascii=False)}}
        if name == "read_file" and len(vals) >= 1:
            return {"function": {"name": name,
                                 "arguments": json.dumps({"path": vals[0]}, ensure_ascii=False)}}
        if name == "write_file" and len(vals) >= 2:
            return {"function": {"name": name,
                                 "arguments": json.dumps(
                                     {"path": vals[0], "content": vals[1]},
                                     ensure_ascii=False)}}
    return None


def _match_paren(text: str, open_idx: int) -> str | None:
    """从 '(' 位置开始做括号匹配，正确跳过字符串里的括号。"""
    depth = 0
    quote = None
    i = open_idx
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i]
        i += 1
    return None


def _py_literal(raw: str):
    import ast
    return ast.literal_eval(raw)


def _split_args(s: str) -> list[str]:
    """按顶层逗号切分 Python 实参，忽略字符串/括号内的逗号。"""
    out, buf, depth, quote = [], [], 0, None
    i = 0
    while i < len(s):
        ch = s[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and i + 1 < len(s):
                buf.append(s[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        out.append("".join(buf))
    return out


def _loads_lenient(raw: str) -> dict | None:
    """解析 JSON，容忍尾部被截断（补 1~3 个括号）。"""
    for attempt in (0, 1, 2, 3):
        cand = raw + "}" * attempt if attempt else raw
        try:
            obj = json.loads(cand)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            continue
    return None


def _coerce_call(obj: dict) -> dict | None:
    fn = obj.get("function") if isinstance(obj.get("function"), dict) else obj
    name = fn.get("name") or fn.get("tool") or obj.get("tool")
    if name not in KNOWN_TOOLS:
        return None
    args = fn.get("arguments")
    if args is None:
        args = fn.get("args") or fn.get("parameters") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    if not isinstance(args, dict):
        args = {}
    return {"function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}


def _salvage_args(segment: str, name: str) -> dict | None:
    """从被截断的 JSON 里抢救出仍能用的参数。"""
    if name == "search_kb":
        m = re.search(r'"query"\s*:\s*"([^"]{1,200})"', segment)
        return {"query": m.group(1)} if m else None
    if name == "read_file":
        m = re.search(r'"path"\s*:\s*"([^"]{1,300})"', segment)
        return {"path": m.group(1)} if m else None
    if name == "write_file":
        m = re.search(r'"path"\s*:\s*"([^"]{1,300})"', segment)
        c = re.search(r'"content"\s*:\s*"(.*)$', segment, re.S)
        if not (m and c):
            return None
        body = c.group(1).rstrip()
        while body and body[-1] in '}],"':
            body = body[:-1]
        body = body.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        if not body.strip():
            return None
        return {"path": m.group(1), "content": body}
    return None


def _strip_tool_json(text: str) -> str:
    """把文本里那段工具调用 JSON 抹掉，避免它混进最终回答。"""
    text = _JSON_BLOCK.sub("", text)
    text = _BARE_JSON.sub("", text)
    return text.strip()


# ------------------------------------------------------------------ 工具
@dataclass
class ToolResult:
    ok: bool
    content: str

    def as_message(self, name: str, args: dict) -> str:
        status = "OK" if self.ok else "ERROR"
        return f"[{name}({json.dumps(args, ensure_ascii=False)}) -> {status}]\n{self.content}"


class AgentLoop:
    def __init__(self, cfg=None, host: str = "http://127.0.0.1:11434",
                 model: str = "qwen25-coder-7b-local:latest",
                 max_steps: int = 10, max_obs_chars: int = 800,
                 num_ctx: int = 8192, temperature: float = 0.2):
        self.host = host.rstrip("/")
        self.model = model
        self.max_steps = max_steps
        self.max_obs_chars = max_obs_chars
        self.num_ctx = num_ctx
        self.temperature = temperature

        import sys as _sys
        _sys.path.insert(0, str(ROOT / "tools"))
        from agent.tools import TOOL_SPECS, dispatch
        try:
            from agent.recon import TOOL_SPECS as RECON_SPECS
            from agent.recon import dispatch as recon_dispatch
        except Exception:  # noqa: BLE001
            RECON_SPECS, recon_dispatch = [], None
        self.tool_specs = list(RECON_SPECS) + list(TOOL_SPECS)
        self._dispatch = dispatch
        self._recon_dispatch = recon_dispatch

    # ---------- 模型 ----------
    def _chat(self, messages: list[dict]) -> dict:
        import requests
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "tools": self.tool_specs,
            "keep_alive": "30m",
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_predict": 1024,
            },
        }
        r = requests.post(f"{self.host}/api/chat", json=payload, timeout=600)
        if r.status_code != 200:
            raise RuntimeError(f"Ollama {r.status_code}: {r.text[:300]}")
        return r.json()

    # ---------- 主循环 ----------
    def run(self, prompt: str, history: list[dict] | None = None,
            allow_tools: bool = True) -> Iterator[Event]:
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in (history or []):
            messages.append(h)
        messages.append({"role": "user", "content": prompt})
        self._nudges = 0
        self._used_tools: list[str] = []
        self._wants_file = _wants_file(prompt)
        self._called_sigs: set[str] = set()
        self._repeat = 0
        self._punt_retry = 0
        self._handled_offsets: set[str] = set()
        self._last_probe_target: str | None = None
        self._probe_targets: dict[str, list[int]] = {}
        self._auto_done = False
        self._explicit_attachments = _extract_attachment_paths(prompt)

        for step in range(self.max_steps):
            yield Event("thinking", {"step": step + 1})
            try:
                resp = self._chat(messages)
            except Exception as e:  # noqa: BLE001
                yield Event("error", str(e))
                return

            msg = resp.get("message") or {}
            calls = msg.get("tool_calls") or []
            text = msg.get("content") or ""

            # 小模型的常见失败模式：不支持原生 tool_calls，或把工具调用
            # **当普通文本**吐出来（例如 ```json {"name":"search_kb",...} ```）。
            # 4GB 显存跑 7B 时这种情况很普遍，必须做文本兜底解析。
            if not calls and allow_tools:
                calls = _parse_text_tool_calls(text)
                if calls:
                    text = _strip_tool_json(text)

            if not calls or not allow_tools:
                final = text.strip()
                # 小模型经常一上来就反问"请提供具体参数"，什么都不调。
                # 只要还没用过任何工具，就先逼它调 search_kb，
                # 而不是把反问当最终答案（那等于什么都没做）。
                if allow_tools and not self._used_tools and self._nudges < 2 \
                        and step < self.max_steps - 1:
                    self._nudges += 1
                    messages.append({"role": "assistant", "content": final})
                    messages.append({
                        "role": "user",
                        "content": (
                            "（系统指令）不要向用户提问，也不要请求更多参数。"
                            "先调用 search_kb 检索知识库；"
                            "拿到结果后调用 read_file 读全文；"
                            "需要写脚本时调用 write_file 保存到 work/ 目录。"
                            "现在开始调用工具。"
                        ),
                    })
                    continue
                if allow_tools and self._used_tools and step < self.max_steps - 1 \
                        and self._nudges < 3:
                    need_file = self._wants_file and "write_file" not in self._used_tools
                    if need_file or _is_stalling(final):
                        self._nudges += 1
                        messages.append({"role": "assistant", "content": final})
                        if need_file:
                            messages.append({
                                "role": "user",
                                "content": (
                                    "（系统指令）用户明确要求把脚本保存成文件。"
                                    "不要只把代码贴在回答里，也不要让用户自己复制或保存。"
                                    "请立刻调用 write_file 工具：path 用 work/exp.py，"
                                    "content 放完整可运行的脚本。只输出工具调用，不要输出文字。"
                                ),
                            })
                        else:
                            messages.append({
                                "role": "user",
                                "content": "（系统指令）你只是说要做事，但还没真正调用工具。请立刻发起工具调用。",
                            })
                        continue
                self._nudges = 0
                # 说完"请问您需要什么操作"就停 —— 这是最典型的失败收尾。
                # 实测模型会在这句上反复打转（连续 3 次说同一句话），
                # 光加提示没用，必须在第二次就由系统接替决策。
                if allow_tools and self._used_tools and _is_punting(final):
                    self._punt_retry += 1
                    if self._punt_retry >= 2:
                        # 系统接管：把待办的工具真正执行掉，再用结果收尾
                        acted = yield from self._auto_continue(messages)
                        if acted:
                            self._punt_retry = 0
                            continue
                        yield Event("answer",
                                    self._finalize_from_history(messages),
                                    {"forced": True})
                        return
                    messages.append({"role": "assistant", "content": final})
                    pending = _mentions_pending_tool(final)
                    tip = (f"具体请立刻调用 {pending}。" if pending else "")
                    messages.append({
                        "role": "user",
                        "content": (
                            "（系统指令）不要反问用户。基于你已经读到的内容继续推进，"
                            + tip +
                            "如果还有没处理完的附件片段，逐个导出并分析，"
                            "直到找到 flag 或确认没有为止。只输出工具调用，不要输出文字。"
                        ),
                    })
                    continue

                # 把"下一步该用某工具"当成答案交出去 —— 逼它真的调用
                if allow_tools and self._used_tools and step < self.max_steps - 1 \
                        and self._punt_retry < 3:
                    pending = _mentions_pending_tool(final)
                    if pending:
                        self._punt_retry += 1
                        messages.append({"role": "assistant", "content": final})
                        messages.append({
                            "role": "user",
                            "content": (
                                f"（系统指令）你只是描述了要用 {pending}，但没有真的调用。"
                                f"请立刻发起 {pending} 的工具调用，不要输出文字说明。"
                            ),
                        })
                        continue
                yield Event("answer", final, {
                    "eval_count": resp.get("eval_count"),
                    "eval_duration": resp.get("eval_duration"),
                })
                return

            # 记录 assistant 的工具调用意图。
            # ⚠️ 关键坑：Ollama 要求 tool_calls[].function.arguments 是 **JSON 对象**，
            # 而 OpenAI 规范要求是**字符串**。传字符串会 400：
            #   {"error":"Value looks like object, but can't find closing '}' symbol"}
            # 所以回传前必须把字符串反序列化成对象。
            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [_ollama_safe_call(c) for c in calls],
            })

            for call in calls[:1]:      # 单步：一次只跑一个工具
                fn = call.get("function") or {}
                name = fn.get("name") or ""
                raw_args = fn.get("arguments")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except json.JSONDecodeError:
                    args = {}
                    yield Event("tool_result", {
                        "name": name, "args": raw_args, "ok": False,
                        "content": "参数不是合法 JSON，请重新调用。",
                    })
                    messages.append({
                        "role": "tool", "name": name,
                        "content": "[参数不是合法 JSON] 请用正确的 JSON 重新调用工具。",
                    })
                    continue

                yield Event("tool_call", {"name": name, "args": args})
                self._used_tools.append(name)

                # 去重：同一个工具 + 同样的参数重复调用，说明模型卡在循环里。
                # 不必再执行一次，直接告诉它"已经做过了，请收尾"。
                sig = f"{name}:{json.dumps(args, ensure_ascii=False, sort_keys=True)}"
                if sig in self._called_sigs:
                    self._repeat += 1
                    yield Event("tool_result", {
                        "name": name, "args": args, "ok": True,
                        "content": "（该调用与之前完全相同，已跳过重复执行）", "ms": 0,
                    })
                    messages.append({
                        "role": "tool", "name": name,
                        "content": f"[{name}] 这个调用你已经做过了，结果就在上面的历史里。"
                                   f"请不要再重复，直接根据已有结果给出最终回答。",
                    })
                    if self._repeat >= 1:
                        # 连续重复，强制用已有信息收尾
                        yield Event("answer",
                                    self._finalize_from_history(messages),
                                    {"forced": True})
                        return
                    continue
                self._called_sigs.add(sig)
                self._repeat = 0
                t0 = time.time()
                try:
                    res = self._call_tool(name, args)
                except Exception as e:  # noqa: BLE001
                    res = ToolResult(False, f"{type(e).__name__}: {e}")

                content = res.content
                if len(content) > self.max_obs_chars:
                    content = content[: self.max_obs_chars] + "\n...(已截断)"

                # ---- 记录侦察状态（必须在 res 生成之后！）----
                if name == "probe_file" and isinstance(args, dict):
                    src = args.get("path")
                    self._last_probe_target = src
                    # 只登记**原始附件**的内嵌偏移：对 _probe/ 下的导出物
                    # 再登记，会把 22 字节的片段关联上原文件偏移，后续提取越界。
                    is_derived = "_probe" in (src or "")
                    if is_derived:
                        self._last_probe_target = None
                    elif "内嵌" in content and src:
                        offs = [int(m.group(1), 16)
                                for m in re.finditer(r"(0x[0-9a-f]+)\s*偏移", content)]
                        if offs:
                            self._probe_targets[src] = offs
                if name == "extract_embedded" and isinstance(args, dict):
                    off = args.get("offset")
                    if off is not None:
                        self._handled_offsets.add(f"0x{int(off):x}")

                yield Event("tool_result", {
                    "name": name, "args": args, "ok": res.ok,
                    "content": content, "ms": round((time.time() - t0) * 1000),
                })
                messages.append({
                    "role": "tool",
                    "name": name,
                    "content": f"[{name} 返回]\n{content}",
                })
                # 只列了目录就停：小模型有时调完 list_files 就开始叙述或卡住，
                # 不再往下走。这里强制它去侦察实际附件。
                if name == "list_files" and step < self.max_steps - 2:
                    cand = self._target_attachment(content)
                    if cand and "probe_file" not in self._used_tools:
                        messages.append({
                            "role": "user",
                            "content": (
                                f"（系统指令）题目指定的附件是 {cand}，"
                                f"请立刻对它调用 probe_file 侦察。"
                                "不要分析其它文件，直接发起工具调用，不要输出文字。"
                            ),
                        })
                # 小模型拿到 search_kb 结果后经常"说一句我要读文件"就停，
                # 不真的发调用。这里在工具返回后立刻注入一条强指令，
                # 不依赖对模型文本的猜测，最稳。
                elif name == "search_kb" and step < self.max_steps - 2:
                    messages.append({
                        "role": "user",
                        "content": (
                            "（系统指令）请现在调用 read_file 读取第 1 条结果的完整内容，"
                            "路径用上面列出的那个完整路径（以 kb/ 开头）。"
                            "不要只回复文字，必须真的发起工具调用。"
                        ),
                    })
                # 侦察到多个内嵌文件时，催它把所有都看一遍。
                # 实测模型常常只处理第一个（比如只提了 JPEG 就停），
                # 漏掉后面藏着 flag 的 ZIP/GZIP。
                elif name == "probe_file" and step < self.max_steps - 2:
                    multi = _list_embedded_hints(content)
                    done = self._handled_offsets
                    left = [h for h in multi if h not in done]
                    src_is_original = "_probe" not in (self._last_probe_target or "")
                    # 只要还有 ≥1 个没处理的内嵌片段，且是原始附件，系统就直接接管。
                    # 实测模型会盯着第一个片段（常是填充用的 JPEG）反复打转，
                    # 永远不会主动去看后面的 ZIP/GZIP。
                    if left and not self._auto_done and src_is_original:
                        self._auto_done = True
                        acted = yield from self._auto_continue(messages)
                        if acted:
                            messages.append({
                                "role": "user",
                                "content": (
                                    "（系统指令）上面是系统替你做完的提取与解压结果。"
                                    "请直接根据这些结果给出结论：如果里面有 flag，原样输出；"
                                    "如果没有，说明还剩什么没做。不要再描述计划。"
                                ),
                            })
                            continue
                    elif left:
                        hint = "、".join(left[:5])
                        messages.append({
                            "role": "user",
                            "content": (
                                f"（系统指令）这个文件里还有 {len(left)} 个内嵌片段没处理：{hint}。"
                                "请对每一个都用 extract_embedded 导出，"
                                "再对导出结果 probe_file（是 ZIP 就用 extract_zip）。"
                                "不要只处理第一个就停。"
                            ),
                        })

        yield Event("error", f"超过 {self.max_steps} 步仍未给出最终回答。"
                             f"建议把问题拆小，或直接跑 kb search。")

    def _call_tool(self, name: str, args: dict):
        """统一入口：先试侦察工具（返回 tuple），再试资料工具（返回 ToolResult）。"""
        # 侦察类工具全部走 recon 分发器；其余走资料/落盘工具。
        # 注意：新增侦察工具时必须同步加到这里，否则会被误派到 tools.dispatch
        # 而报「未知工具」——这是之前 3 道复杂题全失败的直接原因。
        RECON = {"list_files", "probe_file", "run_tool",
                 "extract_embedded", "extract_zip", "extract_gzip",
                 "suggest_directions"}
        if name in RECON:
            if self._recon_dispatch is None:
                return ToolResult(False, "侦察工具不可用")
            ok, text = self._recon_dispatch(name, args)
            return ToolResult(ok, text)
        return self._dispatch(name, args)

    def _auto_continue(self, messages: list[dict]):
        """模型卡住时由系统代跑一轮：把 probe_file 报告的内嵌片段全部导出分析。

        返回是否执行过动作（yield Event，所以用生成器）。
        这是"确定性兜底"：模型不可靠时，工具链仍然能走完。
        """
        acted = False
        # 只用【原始附件 -> 偏移】这张表。不要再用 messages 里的
        # probe 结果去反推源文件——对导出物的 probe 会污染映射，
        # 之前就因此拿 22 字节的片段去套原文件偏移 246/444 而越界。
        for src, offs in list(self._probe_targets.items()):
            # 只处理题目明确点名的附件；否则会把目录里其它测试文件的
            # flag 当成答案（实测发生过）。
            if self._explicit_attachments:
                src_name = Path(src).name
                if not any(src_name == Path(a).name for a in self._explicit_attachments):
                    continue
            pending = [o for o in offs if f"0x{o:x}" not in self._handled_offsets]
            for off in pending[:4]:
                name, args = "extract_embedded", {"path": src, "offset": off}
                yield Event("tool_call", {"name": name, "args": args})
                try:
                    res = self._call_tool(name, args)
                except Exception as e:  # noqa: BLE001
                    res = ToolResult(False, str(e))
                self._handled_offsets.add(f"0x{off:x}")
                self._used_tools.append(name)
                yield Event("tool_result", {
                    "name": name, "args": args, "ok": res.ok,
                    "content": (res.content or "")[:1500], "ms": 0,
                    "auto": True,
                })
                messages.append({"role": "tool", "name": name,
                                 "content": f"[{name} 返回]\n{res.content}"})
                acted = True

                # 对导出的文件跑一次 probe_file，再按类型一解到底
                mm = re.search(r"->\s*(\S+)", res.content or "")
                if not mm or self._recon_dispatch is None:
                    continue
                out = mm.group(1)
                try:
                    ok2, text2 = self._recon_dispatch("probe_file", {"path": out})
                except Exception:  # noqa: BLE001
                    continue
                if not ok2:
                    continue
                yield Event("tool_result", {
                    "name": "probe_file", "args": {"path": out},
                    "ok": True, "content": text2[:1500], "ms": 0, "auto": True,
                })
                messages.append({"role": "tool", "name": "probe_file",
                                 "content": f"[probe_file 返回]\n{text2}"})

                for tool_name, tag in (("extract_zip", "ZIP"),
                                       ("extract_gzip", "GZIP")):
                    if tag not in text2:
                        continue
                    try:
                        ok3, text3 = self._recon_dispatch(tool_name, {"path": out})
                    except Exception:  # noqa: BLE001
                        continue
                    if not ok3:
                        continue
                    yield Event("tool_result", {
                        "name": tool_name, "args": {"path": out},
                        "ok": True, "content": text3[:1500], "ms": 0, "auto": True,
                    })
                    messages.append({"role": "tool", "name": tool_name,
                                     "content": f"[{tool_name} 返回]\n{text3}"})
                    dm = re.search(r"已解压到\s*(\S+)", text3)
                    if not dm:
                        continue
                    for t in sorted(Path(dm.group(1)).rglob("*"))[:6]:
                        if not t.is_file():
                            continue
                        if t.suffix.lower() not in (
                                ".txt", ".md", ".flag", ".log", ".py", ""):
                            continue
                        try:
                            body = t.read_text(encoding="utf-8", errors="replace")[:800]
                        except Exception:  # noqa: BLE001
                            continue
                        yield Event("tool_result", {
                            "name": "read_file", "args": {"path": str(t)},
                            "ok": True, "content": body, "ms": 0, "auto": True,
                        })
                        messages.append({"role": "tool", "name": "read_file",
                                         "content": f"[read_file 返回]\n{body}"})
        return acted

    def _finalize_from_history(self, messages: list[dict]) -> str:
        """模型陷入重复调用时，用已完成的工具结果拼一个可用的收尾说明。"""
        written = []
        searched = []
        extracted = []
        inspected = []
        for m in messages:
            if m.get("role") != "tool":
                continue
            c = m.get("content") or ""
            name = m.get("name")
            if name == "write_file":
                # 只取真正的落盘结果行（形如 "已创建: path (n 字符)"），
                # 跳过"已跳过重复执行"这类提示，避免把提示当文件名写进总结。
                first = (c.splitlines()[0] if c else "").strip()
                if first.startswith(("已创建", "已覆盖")):
                    written.append(first)
            elif name == "search_kb":
                for line in c.splitlines():
                    if line.strip().startswith("路径:"):
                        searched.append(line.split("路径:")[-1].strip())
            elif name in ("extract_zip", "extract_embedded"):
                for line in c.splitlines():
                    s = line.strip()
                    if s.startswith("已解压到") or s.startswith("已导出"):
                        extracted.append(s)
                    elif ".txt" in s or ".md" in s or ".bin" in s:
                        extracted.append("  " + s)
            elif name in ("probe_file", "list_files", "run_tool"):
                for line in c.splitlines():
                    s = line.strip()
                    if "flag{" in s.lower() or "Flag_B64" in s or "⚠" in s:
                        inspected.append("  " + s[:160])

        # 先在所有工具结果里找 flag —— 找到就直接作为结论放最前面。
        # 模型没给出答案时，自动汇总往往是我们唯一的输出，
        # 这时把 flag 埋在侦察记录里等于没用。
        found_flag = None
        for m in messages:
            if m.get("role") != "tool":
                continue
            fm = re.search(r"flag\{[^}\r\n]{1,200}\}", m.get("content") or "",
                           re.I)
            if fm:
                found_flag = fm.group(0)
                break

        lines = []
        if found_flag:
            lines.append(f"**找到 flag：{found_flag}**")
            lines.append("")
            lines.append("以下是侦察过程：")
        else:
            lines.append("已完成以下步骤（这里是自动汇总，未直接找到 flag）：")

        if searched:
            lines.append(f"- 查阅知识库：{', '.join(dict.fromkeys(searched))}")
        if inspected:
            lines.append("- 侦察发现的线索：")
            lines.extend(dict.fromkeys(inspected) or [])
        if extracted:
            lines.append("- 提取结果：")
            lines.extend(dict.fromkeys(extracted))
        if written:
            lines.append(f"- 已生成文件：{written[-1]}")
        if not (searched or extracted or written or inspected) and not found_flag:
            lines.append("- 没有产生有效结果，建议换个说法重试。")
        return "\n".join(lines)

    def _target_attachment(self, listing: str) -> str | None:
        """确定该分析哪个附件：优先用题目里点名的那一个。

        踩过的坑：题面写「附件：work/attachments/locked.zip」，
        但目录里有多个测试文件，模型挑成了 mixed.bin，
        系统接管之后忠实地分析了错误的文件，把别人的 flag 当答案。
        所以只要有明确的题目附件路径，就必须以它为准。
        """
        # 1) 题面里明确写了路径（用户在 prompt 里给了附件）
        if self._explicit_attachments:
            return self._explicit_attachments[0]
        # 2) 退化：从目录列表里猜
        return _pick_attachment(listing)

    def chat_plain(self, prompt: str, history: list[dict] | None = None) -> str:
        """不加工具的纯对话（省上下文，用于闲聊或复述）。"""
        messages = [{"role": "system", "content": "你是简洁的 CTF 助手。用中文回答。"}]
        for h in (history or []):
            messages.append(h)
        messages.append({"role": "user", "content": prompt})
        resp = self._chat(messages)
        return (resp.get("message") or {}).get("content", "")

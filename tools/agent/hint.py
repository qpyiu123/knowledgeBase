"""方向建议：选手没思路时，从附件/题面推出下一步该试什么。

设计要点（来自实测）：

1. **侦察在前，模型在后。**
   先跑 recon.probe_file 拿到硬事实（类型/偏移/内嵌/解码结果），
   再把侦察结果喂给模型。绝不让模型凭空猜。

2. **小模型只做"翻译"，不做"发明"。**
   Qwen3-4B 在「根据给定事实给建议」上表现好（24 tok/s，
   三道测试题全部命中要害），但让它自己想候选就全错。
   所以这里的 prompt 明确要求「依据侦察结果里的哪条线索」。

3. **知识库参与，但不主导。**
   用侦察结果去检索知识库拿相关技法，作为背景塞进 prompt，
   增加模型给出正确术语的概率。

4. **输出结构化，但允许降级。**
   JSON 解析失败时退回纯文本展示，不要让用户什么都看不到。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

try:                                    # 允许单独运行
    from . import recon as _recon
except ImportError:                     # pragma: no cover
    import recon as _recon              # type: ignore

PROMPT = """你是 CTF 解题助手。选手完全没有思路，需要你给出方向。

下面是工具对附件的自动侦察结果（这些是**已确认的事实**）：

{probe}

{extra}

请给出 **3 个**最值得先试的方向。要求：
- 每个方向的依据必须引用上面侦察结果里的**具体某条线索**
- 做法要具体到可执行的命令或步骤
- 不要给泛泛而谈的建议（如"仔细检查文件"）
- **按最可能出 flag 的顺序排**。体积大、含文本/ZIP/可读数据的内嵌片段优先；
  纯填充用的短片段（如 20 字节的 JPEG 头）放最后

严格按 JSON 输出，不要 markdown 代码块：
{{"directions": [
  {{"idea": "方向名", "why": "依据哪条线索", "how": "具体命令或步骤"}}
]}}"""


@dataclass
class Hint:
    idea: str
    why: str
    how: str

    def to_dict(self) -> dict:
        return {"idea": self.idea, "why": self.why, "how": self.how}


@dataclass
class HintResult:
    path: str = ""
    probe: str = ""              # 原始侦察结果，便于核对
    related: list[str] = field(default_factory=list)   # 知识库相关条目
    hints: list[Hint] = field(default_factory=list)
    raw: str = ""
    model: str = ""
    tok_s: float = 0.0
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "probe": self.probe,
            "related": self.related,
            "hints": [h.to_dict() for h in self.hints],
            "model": self.model,
            "tok_s": round(self.tok_s, 1),
            "note": self.note,
        }

    def render(self) -> str:
        lines = []
        if self.hints:
            lines.append("建议的探索方向：\n")
            for i, h in enumerate(self.hints, 1):
                lines.append(f"  {i}. {h.idea}")
                if h.why:
                    lines.append(f"     依据: {h.why}")
                if h.how:
                    lines.append(f"     做法: {h.how}")
        elif self.raw:
            lines.append("（模型输出未能解析成结构化建议，原文如下）\n")
            lines.append(self.raw)
        if self.note:
            lines.append(f"\n注: {self.note}")
        if self.related:
            lines.append("\n知识库相关条目：")
            lines.extend(f"  - {r}" for r in self.related)
        return "\n".join(lines)


def _parse(text: str) -> dict | None:
    """容忍小模型的各种 JSON 毛病。"""
    t = text.strip()
    # 去掉 markdown 围栏
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    cands = [t]
    if m:
        cands.insert(0, m.group(1).strip())
    m2 = re.search(r"\{.*\}", t, re.S)
    if m2:
        cands.append(m2.group(0))

    for s in cands:
        if not s:
            continue
        try:
            o = json.loads(s)
            if isinstance(o, dict):
                return o
        except json.JSONDecodeError:
            # 对象间漏逗号
            try:
                o = json.loads(re.sub(r"\}\s*\{", "},{", s))
                if isinstance(o, dict):
                    return o
            except json.JSONDecodeError:
                continue
    return None


def hint_for(path: str, question: str = "", kb=None,
             model: str | None = None, host: str = "http://127.0.0.1:11434",
             ollama_model: str = "qwen3-4b-local:latest") -> HintResult:
    """对单个附件生成方向建议。

    kb 传入 KB 实例时会把知识库相关条目作为背景；不传也能工作。
    """
    import requests

    res = HintResult(path=path)

    ok, probe = _recon.probe_file(path)
    if not ok:
        res.note = f"侦察失败：{probe}"
        return res
    res.probe = probe

    # 用侦察结果里的关键词去检索知识库
    extra = ""
    if kb is not None:
        try:
            q = _query_from_probe(probe, question)
            hits = kb.search(q, top_k=6)
            hits = _rerank_by_type_fit(hits, probe)[:4]
            if hits:
                res.related = [f"{h.title} ({h.doc_path})" for h in hits]
                extra = "相关知识库条目（可参考其中技法）：\n" + "\n".join(
                    f"- {h.title}: {h.doc_path}" for h in hits)
        except Exception:  # noqa: BLE001
            pass

    prompt = PROMPT.format(probe=probe[:2600], extra=extra)
    if question.strip():
        prompt = f"题目描述：{question.strip()}\n\n" + prompt

    try:
        r = requests.post(f"{host}/api/chat", json={
            "model": ollama_model if model is None else model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_ctx": 6144, "num_predict": 1400,
                        "temperature": 0.3},
        }, timeout=600)
        r.raise_for_status()
        j = r.json()
    except Exception as e:  # noqa: BLE001
        res.note = f"模型调用失败：{type(e).__name__}: {e}"
        return res

    res.model = ollama_model if model is None else model
    ec = j.get("eval_count") or 0
    ed = (j.get("eval_duration") or 1) / 1e9
    res.tok_s = ec / ed if ed else 0.0
    res.raw = (j.get("message") or {}).get("content", "")

    parsed = _parse(res.raw)
    if parsed and isinstance(parsed.get("directions"), list):
        for d in parsed["directions"][:6]:
            if not isinstance(d, dict):
                continue
            res.hints.append(Hint(
                idea=str(d.get("idea") or "").strip(),
                why=str(d.get("why") or "").strip(),
                how=str(d.get("how") or "").strip(),
            ))
    if not res.hints:
        res.note = "JSON 解析失败，已退回原文展示"

    return res


def _rerank_by_type_fit(hits: list, probe: str) -> list:
    """按"文件格式是否对得上"重排。

    踩过的坑：PNG 题检索出「JPG 图片隐写」，因为向量模型对
    PNG/JPG 区分不好。这里用标题里出现的格式名做硬约束：
    附件是 PNG 时，标题只提 JPG 的条目降权。
    """
    kind = ""
    for line in probe.splitlines():
        if line.strip().startswith("类型判定"):
            v = line.split(":", 1)[-1].strip()
            for k in ("PNG", "JPEG", "GIF", "BMP", "ZIP", "RAR", "PDF",
                      "ELF", "PE", "WAV", "MP3", "MP4", "PCAP"):
                if k in v:
                    kind = k
                    break
            break
    if not kind:
        return hits

    # 互斥组：命中哪个就压哪个
    groups = {
        "PNG":  {"JPG", "JPEG", "GIF", "BMP"},
        "JPEG": {"PNG", "GIF", "BMP"},
        "GIF":  {"PNG", "JPG", "JPEG"},
        "BMP":  {"PNG", "JPG", "JPEG"},
        "ZIP":  {"RAR", "7Z"},
        "WAV":  {"MP3", "MP4"},
        "MP3":  {"WAV", "MP4"},
    }
    conflict = groups.get(kind, set())

    def score(h) -> int:
        t = (h.title or "").upper()
        s = 0
        if kind in t:
            s += 3
        if any(c in t for c in conflict):
            s -= 3
        return s

    return sorted(hits, key=lambda h: (-score(h),))


def _query_from_probe(probe: str, question: str) -> str:
    """从侦察结果里抽关键词拼检索 query。

    要点：只用**能对应到技法**的词（文件类型、异常现象），
    不要把 "类型判定" 这种字段名也塞进去——实测那样会命中
    「硬件 CTF 方法论」「惜字如金」之类完全不相关的条目。
    """
    bits: list[str] = []
    # 题面不参与检索：真实比赛的题面多是套话，塞进去只会引入噪声
    # （实测「各位选手好，这是综合题」会把「硬件 CTF 方法论」
    #   和「Docker for Everyone」检出来）。

    types: list[str] = []
    for line in probe.splitlines():
        s = line.strip()
        # 内嵌片段："0xf6 偏移: ZIP (138 字节)" -> ZIP
        m = re.search(r"偏移:\s*([A-Za-z0-9]+)\s*\(", s)
        if m:
            types.append(m.group(1))
            continue
        # 异常：扩展名不符、追加数据、文本块
        if "⚠" in s:
            if "扩展名" in s:
                bits.append("文件头 魔数 扩展名 伪装")
            elif "IEND" in s:
                bits.append("PNG 尾部 追加数据")
            elif "文本块" in s:
                bits.append("PNG 元数据 tEXt")
            elif "RIFF" in s or "追加" in s:
                bits.append("音频 尾部 追加数据")
            continue
        # 解码结果
        if "-->" in s:
            bits.append("base64 解码")
            continue
        # 类型判定：只取具体类型
        if s.startswith("类型判定"):
            val = s.split(":", 1)[-1].strip()
            if "未知" not in val:
                types.append(val.split("（")[0].strip())

    # 有多个内嵌片段时，优先检索"雕刻/分离"这一技法
    if len(types) >= 2:
        bits.insert(0, "内嵌文件 雕刻 分离 提取")
    bits.extend(types)

    return " ".join(dict.fromkeys(bits))[:200] or "文件头 魔数 识别"

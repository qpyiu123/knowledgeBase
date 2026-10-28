"""适用条件三态：已知 / 未知 / 不满足。

判定完全由规则完成，不调用模型：

1. `requires` 图谱关系：命中条目声明的前置文档是否已经在本次上下文里，
   或用户是否直接点名了它。没有证据就是 **unknown**，不会假装满足。
2. `applicability_rules.json` 里的确定性规则：关键词（含否定词）与
   libc 版本区间。查到支持线索是 known，查到否定线索是 unsatisfied，
   两者都没有是 unknown。

输出给检索解释、ask 提示和评测复用；本模块不改变检索排序。
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from .parser import _as_list, split_front_matter

STATUS_KNOWN = "known"
STATUS_UNKNOWN = "unknown"
STATUS_UNSATISFIED = "unsatisfied"

STATUS_LABEL = {
    STATUS_KNOWN: "已知",
    STATUS_UNKNOWN: "未知",
    STATUS_UNSATISFIED: "不满足",
}

_RULES_FILE = Path(__file__).with_name("applicability_rules.json")

_LIBC_VERSION_RE = re.compile(
    r"(?:glibc|libc)[^0-9]{0,12}([0-9]+\.[0-9]+)"
    r"|(?<![0-9.])(2\.(?:1[6-9]|2[0-9]|3[0-9]|4[0-5]))(?![0-9.])"
)


def _norm(text: str) -> str:
    """去空白 + casefold：让「没有 canary」和「没有canary」等价判定。"""
    return re.sub(r"\s+", "", str(text or "").casefold())


@lru_cache(maxsize=4)
def _load_rules_cached(path: str, mtime_ns: int) -> tuple[dict, ...]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rules = data.get("rules") or []
    out = []
    for r in rules:
        if not isinstance(r, dict) or not r.get("id") or not r.get("paths"):
            continue
        out.append(r)
    return tuple(out)


def load_rules() -> tuple[dict, ...]:
    try:
        stat = _RULES_FILE.stat()
        return _load_rules_cached(str(_RULES_FILE), stat.st_mtime_ns)
    except (OSError, json.JSONDecodeError, ValueError):
        return ()


def _read_meta(kb_dir: Path, rel: str) -> dict[str, Any]:
    p = kb_dir / rel
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    meta, _body = split_front_matter(text)
    if not isinstance(meta, dict):
        return {}
    return meta


@lru_cache(maxsize=32)
def _paths_by_name(kb_dir: str, _mtime_ns: int) -> dict[str, tuple[str, ...]]:
    root = Path(kb_dir)
    out: dict[str, list[str]] = {}
    if not root.is_dir():
        return {}
    for p in root.rglob("*.md"):
        if any(part in {"_templates", ".obsidian", ".git", "node_modules"}
               for part in p.relative_to(root).parts[:-1]):
            continue
        out.setdefault(p.name, []).append(p.relative_to(root).as_posix())
    return {k: tuple(v) for k, v in out.items()}


def resolve_target(kb_dir: Path, target: str) -> str | None:
    """把 requires 里的路径/文件名解析成 kb 内相对路径。"""
    t = str(target or "").strip().replace("\\", "/")
    if not t:
        return None
    exact = kb_dir / t
    if exact.is_file():
        return t
    if not t.endswith(".md") and (kb_dir / (t + ".md")).is_file():
        return t + ".md"
    try:
        mtime = kb_dir.stat().st_mtime_ns
    except OSError:
        return None
    matches = _paths_by_name(str(kb_dir), mtime).get(Path(t).name) or ()
    return matches[0] if len(matches) == 1 else None


def _rule_status(rule: dict, query: str) -> dict[str, Any]:
    kind = str(rule.get("kind") or "keywords").lower()
    q = _norm(query)
    if kind == "version":
        return _version_status(rule, q)
    return _keyword_status(rule, q)


def _keyword_status(rule: dict, q: str) -> dict[str, Any]:
    any_terms = [str(t) for t in (rule.get("any") or []) if str(t).strip()]
    none_terms = [str(t) for t in (rule.get("none") or []) if str(t).strip()]
    for term in none_terms:
        if _norm(term) and _norm(term) in q:
            return {
                "status": STATUS_UNSATISFIED,
                "evidence": f"查询中出现否定线索「{term}」",
                "need": any_terms[:4],
            }
    for term in any_terms:
        if _norm(term) and _norm(term) in q:
            return {
                "status": STATUS_KNOWN,
                "evidence": f"查询中出现「{term}」",
                "need": any_terms[:4],
            }
    return {
        "status": STATUS_UNKNOWN,
        "evidence": "查询里没有找到支持或否定该前提的线索",
        "need": any_terms[:4],
    }


def _version_status(rule: dict, q: str) -> dict[str, Any]:
    lo = str(rule.get("min") or "")
    hi = str(rule.get("max") or "")
    try:
        lo_f = float(lo)
        hi_f = float(hi)
    except ValueError:
        return {"status": STATUS_UNKNOWN, "evidence": "规则版本区间无效",
                "need": []}

    versions: list[str] = []
    for m in _LIBC_VERSION_RE.finditer(q):
        v = m.group(1) or m.group(2)
        if v and v not in versions:
            versions.append(v)
    if not versions:
        return {
            "status": STATUS_UNKNOWN,
            "evidence": f"查询未给出 glibc 版本（需要 {lo}–{hi}）",
            "need": [f"glibc {lo}–{hi}"],
        }
    inside = [v for v in versions if lo_f - 1e-9 <= float(v) <= hi_f + 1e-9]
    if inside:
        return {
            "status": STATUS_KNOWN,
            "evidence": f"查询给出 glibc {inside[0]}，在 {lo}–{hi} 内",
            "need": [f"glibc {lo}–{hi}"],
        }
    return {
        "status": STATUS_UNSATISFIED,
        "evidence": f"查询给出 glibc {versions[0]}，超出 {lo}–{hi}",
        "need": [f"glibc {lo}–{hi}"],
    }


def _requires_conditions(kb_dir: Path, rel: str, query: str,
                         context_paths: set[str]) -> list[dict[str, Any]]:
    meta = _read_meta(kb_dir, rel)
    targets = _as_list(meta.get("requires"))
    out: list[dict[str, Any]] = []
    for target in targets:
        target_rel = resolve_target(kb_dir, target)
        target_title = target_rel or target
        if target_rel:
            tmeta = _read_meta(kb_dir, target_rel)
            target_title = str(tmeta.get("title") or target_rel)
        q = _norm(query)
        hit = (target_rel in context_paths) if target_rel else False
        named = bool(_norm(target_title)) and _norm(target_title) in q
        if hit or named:
            status = STATUS_KNOWN
            evidence = ("前提资料已在本次检索上下文中"
                        if hit else "查询直接点名了该前提")
        else:
            status = STATUS_UNKNOWN
            evidence = "本次上下文没有包含该前提资料"
        out.append({
            "id": f"requires:{target_rel or target}",
            "label": f"先掌握《{target_title}》",
            "status": status,
            "status_label": STATUS_LABEL[status],
            "evidence": evidence,
            "need": [target_title],
            "source": f"kb/{target_rel}" if target_rel else str(target),
            "trace": "requires",
        })
    return out


def evaluate_conditions(kb_dir: str | Path, rel: str, query: str,
                        context_paths: Iterable[str] = ()) -> dict[str, Any]:
    """返回单篇资料的适用条件三态与可操作提示。"""
    root = Path(kb_dir)
    rel = str(rel or "").replace("\\", "/")
    ctx = {str(p).replace("\\", "/") for p in (context_paths or ()) if p}
    conditions: list[dict[str, Any]] = []

    for rule in load_rules():
        paths = [str(p).replace("\\", "/") for p in (rule.get("paths") or [])]
        if rel not in paths:
            continue
        res = _rule_status(rule, query)
        status = str(res["status"])
        conditions.append({
            "id": str(rule.get("id")),
            "label": str(rule.get("label") or rule.get("id")),
            "status": status,
            "status_label": STATUS_LABEL.get(status, status),
            "evidence": str(res.get("evidence") or ""),
            "need": list(res.get("need") or []),
            "source": f"kb/{rule.get('source')}",
            "trace": "rule",
        })

    conditions.extend(_requires_conditions(root, rel, query, ctx))

    if not conditions:
        return {"status": STATUS_KNOWN, "status_label": STATUS_LABEL[STATUS_KNOWN],
                "label": "无额外适用前提", "conditions": [], "hint": "",
                "trace": {"rules": 0, "requires": 0}}

    statuses = {c["status"] for c in conditions}
    if STATUS_UNSATISFIED in statuses:
        overall = STATUS_UNSATISFIED
    elif STATUS_UNKNOWN in statuses:
        overall = STATUS_UNKNOWN
    else:
        overall = STATUS_KNOWN

    hints = []
    for c in conditions:
        if c["status"] == STATUS_UNKNOWN:
            need = " / ".join(c["need"][:3]) or c["label"]
            hints.append(
                f"缺少前提：{c['label']}（unknown）；可确认：{need}；参见 {c['source']}"
            )
        elif c["status"] == STATUS_UNSATISFIED:
            hints.append(
                f"不满足：{c['label']}（unsatisfied）；{c['evidence']}；"
                f"参见 {c['source']}"
            )

    trace = {
        "rules": sum(1 for c in conditions if c["trace"] == "rule"),
        "requires": sum(1 for c in conditions if c["trace"] == "requires"),
    }
    return {
        "status": overall,
        "status_label": STATUS_LABEL[overall],
        "label": "条件" + STATUS_LABEL[overall],
        "conditions": conditions,
        "hint": "；".join(hints),
        "trace": trace,
    }


def evaluate_paths(kb_dir: str | Path, paths: Iterable[str], query: str) -> dict[str, Any]:
    """一次判定多篇资料，供 ask 提示与评测使用。"""
    items = []
    ctx = list(paths)
    for rel in ctx:
        items.append({"path": rel,
                      "applicability": evaluate_conditions(kb_dir, rel, query, ctx)})
    unknown = sum(1 for i in items
                  if i["applicability"]["status"] == STATUS_UNKNOWN)
    unsatisfied = sum(1 for i in items
                      if i["applicability"]["status"] == STATUS_UNSATISFIED)
    lines = []
    for i in items:
        app = i["applicability"]
        for c in app["conditions"]:
            if c["status"] == STATUS_UNKNOWN:
                lines.append(f"- {i['path']}：缺少前提：{c['label']}（unknown）")
            elif c["status"] == STATUS_UNSATISFIED:
                lines.append(f"- {i['path']}：不满足：{c['label']}（unsatisfied）")
    if not lines:
        summary = "所有可判定前提均已知，或该资料没有额外前提。"
    else:
        summary = "以下前提尚未确认，回答时不要假设它成立：\n" + "\n".join(lines)
    return {
        "status": (STATUS_UNSATISFIED if unsatisfied else
                   STATUS_UNKNOWN if unknown else STATUS_KNOWN),
        "items": items,
        "unknown": unknown,
        "unsatisfied": unsatisfied,
        "hint": summary,
    }

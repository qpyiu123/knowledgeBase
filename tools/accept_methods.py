"""方法卡格式、来源与脚本验收。只执行库内已审阅脚本的 --selftest。"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

from kb.parser import VALID_CATEGORIES, split_front_matter

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("title", "category", "tags", "signals", "difficulty", "source", "tools", "updated")
SCRIPT_RE = re.compile(r"kb[/\\]_methods[/\\]scripts[/\\]([\w-]+\.py)")


def source_paths(value) -> list[str]:
    """兼容 YAML 列表与旧卡片的逗号分隔路径；保留文件名里的空格。"""
    if isinstance(value, str):
        return [s.strip() for s in re.split(r"[,，;；]", value) if s.strip()]
    if isinstance(value, list):
        return [str(s).strip() for s in value if str(s).strip()]
    return []


def inspect_card(card: Path, root: Path = ROOT) -> dict:
    raw = card.read_text(encoding="utf-8-sig")
    result = {"path": card.relative_to(root).as_posix(), "errors": [], "scripts": [], "sources": []}
    errors = result["errors"]
    try:
        meta, body = split_front_matter(raw, strict=True)
    except (yaml.YAMLError, ValueError) as exc:
        errors.append(f"YAML 无法解析：{exc}")
        return result
    if not meta:
        errors.append("缺少 front-matter 字段")
        return result
    for field in FIELDS:
        if field not in meta or meta[field] in (None, "", []):
            errors.append(f"缺少字段：{field}")
    if meta.get("category") not in VALID_CATEGORIES:
        errors.append("category 不在支持的方向中")
    if meta.get("difficulty") not in ("easy", "medium", "hard"):
        errors.append("difficulty 必须为 easy、medium 或 hard")
    for name in ("tags", "signals", "tools"):
        values = meta.get(name)
        if not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
            errors.append(f"{name} 必须是非空字符串列表")
    signals = meta.get("signals")
    if isinstance(signals, list):
        if not 4 <= len(signals) <= 8:
            errors.append("signals 需要 4–8 条")
        if any(isinstance(s, str) and len(s) > 40 for s in signals):
            errors.append("每条 signal 最多 40 字")
    for source in source_paths(meta.get("source")):
        source = source.replace("\\", "/")
        path = (root / source).resolve()
        if not path.is_relative_to((root / "kb").resolve()) or not path.is_file() or path.suffix != ".md":
            errors.append(f"来源不存在或不在 kb 内：{source}")
        else:
            result["sources"].append(source)
    if not result["sources"]:
        errors.append("需要至少一篇库内 Markdown 来源")
    for section in ("适用场景", "前置条件", "步骤", "失效场景"):
        if not re.search(rf"^##\s+[^\n]*{section}", body, re.M):
            errors.append(f"缺少章节：{section}")
    for name in sorted(set(SCRIPT_RE.findall(body))):
        path = root / "kb" / "_methods" / "scripts" / name
        if not path.is_file():
            errors.append(f"脚本不存在：{name}")
        else:
            result["scripts"].append(path.relative_to(root).as_posix())
    if not result["scripts"] and "无脚本速查卡" not in body:
        errors.append("需要脚本路径，或注明无脚本速查卡及手工步骤")
    result["difficulty"] = meta.get("difficulty")
    result["signals"] = meta.get("signals", [])
    return result


def accept(root: Path = ROOT, *, selftest: bool = False) -> dict:
    root = root.resolve()
    cards = [inspect_card(p, root) for p in sorted((root / "kb/_methods").glob("*.md"))]
    scripts = []
    if selftest:
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        for name in sorted({s for card in cards for s in card["scripts"]}):
            try:
                proc = subprocess.run([sys.executable, str(root / name), "--selftest"],
                                      cwd=root, env=env, capture_output=True, text=True,
                                      encoding="utf-8", errors="replace", timeout=30)
                scripts.append({"path": name, "ok": proc.returncode == 0 and "selftest ok" in proc.stdout.lower(),
                                "exit": proc.returncode, "output": (proc.stdout + proc.stderr)[-2000:]})
            except subprocess.TimeoutExpired:
                scripts.append({"path": name, "ok": False, "error": "自检超过 30 秒"})
    return {"cards_total": len(cards), "accepted": sum(not c["errors"] for c in cards),
            "ok": bool(cards) and all(not c["errors"] for c in cards) and all(s["ok"] for s in scripts),
            "cards": cards, "scripts": scripts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--selftest", action="store_true", help="运行引用脚本的离线自检")
    parser.add_argument("--output", type=Path, help="JSON 报告输出路径")
    args = parser.parse_args()
    report = accept(args.root, selftest=args.selftest)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    print(f"方法卡 {report['accepted']}/{report['cards_total']}，脚本自检 {sum(s['ok'] for s in report['scripts'])}/{len(report['scripts'])}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

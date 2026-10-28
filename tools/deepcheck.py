"""深度体检：检查被掐断可能留下的半截文件。

检查项：
  1. front-matter 完整闭合
  2. 代码块围栏配平
  3. 文件是否以"说了一半"结尾（无句末标点、以逗号/冒号结尾、异常短）
  4. 六个标准章节是否齐全
  5. 是否存在 U+FFFD 替换字符（编码损坏）
  6. 行尾混用（CRLF 混入 LF）
  7. python 代码块能否 ast.parse
"""
from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from kb.config import Config
from kb.parser import iter_docs, split_front_matter

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "kb"

REQUIRED_SECTIONS = ["识别信号", "原理", "参考"]
FENCE = re.compile(r"^\s*```", re.M)
# 注意：列表项下的代码块，开闭围栏都带缩进。如果这里用
#   r"```python\n(.*?)```"
# 那么闭合围栏前的空格会被算进 code 的末尾，再经过 split/strip
# 会表现为"第 2 行多了 4 格缩进"的假阳性。
# 所以这里显式吸收围栏前后的缩进与空行。
PY_FENCE = re.compile(r"[ \t]*```python[ \t]*\r?\n(.*?)[ \t]*```", re.S)

issues: dict[str, list] = defaultdict(list)


def add(kind: str, path: str, detail: str):
    issues[kind].append(f"{path}: {detail}")


def main() -> int:
    files = [p for p in KB.rglob("*.md") if not p.name.startswith("_")]
    print(f"扫描 {len(files)} 个文件\n")

    for p in files:
        rel = p.relative_to(KB).as_posix()
        raw_bytes = p.read_bytes()

        # 6. 行尾混用
        crlf = raw_bytes.count(b"\r\n")
        lf = raw_bytes.count(b"\n") - crlf
        if crlf and lf:
            add("行尾混用", rel, f"CRLF={crlf} LF={lf}")

        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            add("编码错误", rel, str(e))
            continue

        # 5. 替换字符
        if "\ufffd" in text:
            add("编码损坏(U+FFFD)", rel, f"出现 {text.count(chr(0xFFFD))} 次")

        # BOM
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            add("含BOM", rel, "UTF-8 BOM")

        # 1. front-matter
        if not text.startswith("---"):
            add("front-matter缺失", rel, "首行不是 ---")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            add("front-matter未闭合", rel, "只有开头的 ---")
            continue
        meta, body = split_front_matter(text)
        if not meta:
            add("front-matter解析失败", rel, "YAML 无法解析")

        # 2. 围栏配平
        fences = FENCE.findall(text)
        if len(fences) % 2 != 0:
            add("代码围栏不配对", rel, f"``` 出现 {len(fences)} 次（奇数）")

        # 3. 结尾是否"说了一半"
        tail = body.strip()
        if tail:
            last_line = tail.splitlines()[-1].strip()
            # 有明显未完成迹象
            if re.search(r"[，,：:、（(]$", last_line):
                add("疑似截断", rel, f"末尾: {last_line[-40:]!r}")
            if len(tail.splitlines()) < 40:
                add("正文过短", rel, f"body {len(tail.splitlines())} 行")

        # 4. 标准章节
        missing = [s for s in REQUIRED_SECTIONS if s not in body]
        if missing:
            add("缺章节", rel, f"缺 {missing}")

        # 7. python 语法
        for i, code in enumerate(PY_FENCE.findall(body)):
            code = code.strip()
            if not code or len(code) < 20:
                continue
            # --- 排除几类"本就不是合法 Python"的代码块，避免误报 ---
            head = code[:120]
            if _is_sage(head):
                continue                    # SageMath 专用语法
            if _is_pseudocode(code):
                continue                    # 含 ... / 0x... 等占位符的示例
            if _is_shell(code):
                continue                    # 混入的 shell 命令
            try:
                ast.parse(code)
            except SyntaxError as e:
                # 列表项下的代码块在 Markdown 里必须缩进，
                # 去掉公共缩进后再试一次；仍失败才算真错。
                ded = _dedent(code)
                if ded != code:
                    try:
                        ast.parse(ded)
                        continue
                    except SyntaxError:
                        pass
                snippet = code[:80].replace("\n", " ")
                add("python语法错误", rel,
                    f"第{i+1}个代码块 line{e.lineno}: {e.msg} | {snippet!r}")

    print("=" * 70)
    if not issues:
        print("未发现任何问题")
    else:
        total = sum(len(v) for v in issues.values())
        print(f"发现 {total} 个问题，分 {len(issues)} 类：\n")
        for kind, items in sorted(issues.items(), key=lambda kv: -len(kv[1])):
            print(f"\n### {kind} （{len(items)}）")
            for it in items[:40]:
                print(f"  - {it}")
            if len(items) > 40:
                print(f"  ... 另有 {len(items)-40} 条")
    return 0


def _dedent(code: str) -> str:
    """去掉所有非空行的公共缩进。"""
    lines = code.split("\n")
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return code
    prefix = min(len(ln) - len(ln.lstrip(" ")) for ln in non_empty)
    if prefix == 0:
        return code
    return "\n".join((ln[prefix:] if ln.strip() else ln) for ln in lines)


def _is_sage(head: str) -> bool:
    """SageMath 专用语法：R.<x> = ...、Integer()、small_roots、GF(p) 等。"""
    markers = ("R.<", "PolynomialRing", "small_roots", "Integer(", "GF(",
               "Zmod(", "matrix(", "vector(", "# sage", "factor(",
               "EllipticCurve", "discrete_log", "ZZ[")
    low = head.lower()
    return any(m.lower() in low for m in markers)


def _is_pseudocode(code: str) -> bool:
    """含占位符的示例代码（0x...、1385...、<TARGET> 等），不追求可运行。"""
    if re.search(r"0x\.\.\.|Integer\(0x|=\s*\.\.\.|\d+\s*\.\.\.", code):
        return True
    if re.search(r"（[^）]*）|\[待填|TODO|YOUR_|TARGET|PAYLOAD", code):
        return True
    # 大量中文行内注释 + 简短片段，通常是讲解性伪代码
    lines = [ln for ln in code.splitlines() if ln.strip()]
    if lines:
        comment_ratio = sum(1 for ln in lines if ln.strip().startswith("#")) / len(lines)
        if comment_ratio > 0.5:
            return True
    return False


def _is_shell(code: str) -> bool:
    first = next((ln.strip() for ln in code.splitlines() if ln.strip()), "")
    return first.startswith(("python ", "pip ", "sudo ", "$ ", "curl ", "git "))


if __name__ == "__main__":
    raise SystemExit(main())

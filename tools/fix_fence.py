"""彻底修复列表内代码块的缩进不一致。

现象（修复残缺状态）：
    ```python              ← 无缩进（顶格）
    jmprel = ...           ← 无缩进
       reloc_arg = ...     ← 3 空格（错误，上一轮遗留）
    ```

正确形态二选一：
  A) 代码块完全顶格（围栏与内容都无缩进）
  B) 代码块在列表项下，围栏与内容都缩进 3 空格

本脚本统一采用 A：把围栏和内容都拉到顶格。这样无论是否在列表内，
渲染与复制粘贴都正确（列表内的顶格代码块仍会正常渲染）。
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KB = Path("kb")
TARGETS = [
    "pwn/ret2dlresolve.md",
    "pwn/tcache-stashing-unlink.md",
    "pwn/partial-overwrite-oob.md",
    "pwn/seccomp-bypass-advanced.md",
    "pwn/heap-house-of-einherjar.md",
]

FENCE = re.compile(r"(?m)^([ \t]*)```(\w*)[ \t]*\n(.*?)\n[ \t]*```[ \t]*$", re.S)


def fix(text: str) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        indent, lang, body = m.group(1), m.group(2), m.group(3)
        lines = body.split("\n")
        non_empty = [ln for ln in lines if ln.strip()]
        if non_empty:
            common = min(len(ln) - len(ln.lstrip(" ")) for ln in non_empty)
        else:
            common = 0
        # 统一剥掉公共缩进 + 围栏自身的缩进 → 全部顶格
        strip = max(common, len(indent)) if indent else common
        # 但若内容本身还有更深的缩进（代码逻辑），需要保留相对层级
        new_lines = []
        for ln in lines:
            if not ln.strip():
                new_lines.append("")
            else:
                cut = min(strip, len(ln) - len(ln.lstrip(" ")))
                new_lines.append(ln[cut:])
        if indent or common:
            n += 1
            return f"```{lang}\n" + "\n".join(new_lines) + "\n```"
        return m.group(0)

    return FENCE.sub(repl, text), n


def main() -> int:
    for rel in TARGETS:
        p = KB / rel
        text = p.read_text(encoding="utf-8")
        new, n = fix(text)
        if n:
            p.write_text(new, encoding="utf-8")
        print(f"{rel}: 修复 {n} 块")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

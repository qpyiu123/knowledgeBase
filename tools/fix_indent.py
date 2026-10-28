"""修复 pwn 里 5 个缩进错误的代码块：开头多了 3 个空格的整段需要反缩进。

策略：对指定的 (文件, 代码块序号)，检查是否「所有非空行都至少有 3 空格公共缩进」，
是则统一去掉这个公共缩进，并同步修正代码围栏与内容之间的空行。
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KB = Path("kb")

TARGETS = [
    ("pwn/ret2dlresolve.md", 1),
    ("pwn/tcache-stashing-unlink.md", 1),
    ("pwn/partial-overwrite-oob.md", 3),
    ("pwn/seccomp-bypass-advanced.md", 1),
    ("pwn/heap-house-of-einherjar.md", 1),
]

FENCE_RE = re.compile(r"(```python\r?\n)(.*?)(```)", re.S)


def dedent_block(code: str) -> tuple[str, int]:
    lines = code.split("\n")
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return code, 0
    prefix = min(len(ln) - len(ln.lstrip(" ")) for ln in non_empty)
    if prefix == 0:
        return code, 0
    out = []
    for ln in lines:
        if ln.strip():
            out.append(ln[prefix:])
        else:
            out.append("")
    return "\n".join(out), prefix


def main() -> int:
    fixed = 0
    for rel, idx in TARGETS:
        p = KB / rel
        text = p.read_text(encoding="utf-8")
        blocks = list(FENCE_RE.finditer(text))
        if idx > len(blocks):
            print(f"跳过 {rel}: 只有 {len(blocks)} 块")
            continue
        m = blocks[idx - 1]
        code = m.group(2)
        new_code, removed = dedent_block(code)
        if removed == 0:
            print(f"跳过 {rel} block{idx}: 无需反缩进")
            continue
        # 首行通常是空行，保持原样结构
        new_text = text[: m.start()] + m.group(1) + new_code + m.group(3) + text[m.end():]
        p.write_text(new_text, encoding="utf-8")
        print(f"已修复 {rel} block{idx}: 去掉 {removed} 空格缩进")
        fixed += 1
    print(f"\n共修复 {fixed} 处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

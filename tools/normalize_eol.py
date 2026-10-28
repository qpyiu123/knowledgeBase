"""统一行尾为 LF，并清理修复过程中残留的问题。

背景：
- 这 5 个 pwn 文件是 CRLF 换行，其余文件是 LF。
- fix_fence.py 按 "\n" 切分后重组，导致行尾残留 "\r"。
- 统一转 LF 即可，同时也让全库行尾一致。
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KB = Path("kb")

changed = []
for p in KB.rglob("*.md"):
    b = p.read_bytes()
    if b"\r\n" not in b:
        continue
    nb = b.replace(b"\r\n", b"\n")
    p.write_bytes(nb)
    changed.append(p.relative_to(KB).as_posix())

print(f"统一行尾的文件 {len(changed)} 个：")
for c in changed:
    print("  ", c)

# 再全库确认一遍
bad = [p.relative_to(KB).as_posix() for p in KB.rglob("*.md") if b"\r\n" in p.read_bytes()]
print("\n仍有 CRLF 的文件：", bad or "无")

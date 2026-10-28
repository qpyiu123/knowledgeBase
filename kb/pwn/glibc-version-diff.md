---
title: glibc 2.27 ~ 2.41 版本差异速查（Pwn 视角）
category: pwn
tags: [glibc版本, 版本差异, tcache, hook, safe-linking, 适配]
signals: [拿到新 libc 不知道能用哪招, writeup 跑不通, __free_hook 找不到, unaligned tcache chunk detected, 题目 Dockerfile 写了 ubuntu 版本]
difficulty: medium
source: "how2heap / glibc source / 0x434b heap techniques overview"
tools: [pwntools, glibc-all-in-one, patchelf, checksec, libc-database]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件给了 `libc.so.6`，`strings libc.so.6 | grep 'GNU C Library'` 显示版本，但不知道对应哪些招式。
- 网上 writeup 能跑通一半，卡在 `malloc(): unaligned tcache chunk detected` 或 `free(): invalid pointer`。
- `libc.sym['__free_hook']` 抛 `KeyError`。
- 题目 `Dockerfile` 写着 `FROM ubuntu:20.04` / `ubuntu:22.04` / `ubuntu:24.04`。
- 本地能打通、远程秒崩 —— 版本不一致的典型症状。

## 二、原理

glibc 每次版本升级都在 `malloc.c` / `libio` 里加检查，直接决定哪条利用链还能用。

### 关键时间线（64 位 x86）

| 版本 | 发行版 | 关键变化 | 影响 |
|---|---|---|---|
| 2.27 | Ubuntu 18.04 | 无 safe-linking；有 `__free_hook` | 经典 tcache poisoning 最好用 |
| 2.29 | — | tcache 加 `key` 字段；unsorted attack 加检查 | double-free 需清 `key` |
| 2.31 | Ubuntu 20.04 | `key` 检查完善；`main_arena` 不再导出符号 | 仍可打 `__free_hook` |
| **2.32** | Ubuntu 21.04 | **safe-linking**（fd mangling）+ 对齐检查 | 必须有 heap 泄露 |
| 2.33 | Ubuntu 21.10 | 小修补，`_IO` 相关检查 | 与 2.32 基本同路 |
| **2.34** | Ubuntu 22.04 | **删除 `__malloc_hook` / `__free_hook`** | 全面转向 FSOP / 栈 |
| 2.35 | Ubuntu 22.04.1 | `_IO_str_jumps` 的 `_allocate_buffer` 改动 | House of Orange 变体失效 |
| 2.37/2.38 | — | tcache / largebin 检查增强 | 需重算 fake chunk 布局 |
| 2.39/2.41 | Ubuntu 24.04 | `tcache_key` 随机化、更多对齐校验 | 建议直接走栈 / FSOP |

### 三条硬性差异

1. **safe-linking（2.32+）**：`next = (pos >> 12) ^ ptr`。改 `next` 前必须先有 heap 地址。
2. **hook 删除（2.34+）**：`__malloc_hook` / `__free_hook` 不存在，替代目标是 `_IO_list_all` / `_IO_2_1_stdout_` / 栈 / `tls_dtor_list`。
3. **对齐检查（2.32+）**：`tcache_get` / `_int_malloc` 校验 `aligned_OK(e)`，伪目标必须 16 字节对齐。

## 三、checksec 判读与利用思路

先判定版本，再决定打法：

```text
<= 2.31  → __free_hook = system    （最省事）
2.32~2.33 → 同上，但 tcache 部分要 mangle
2.34~2.36 → _IO_FILE / FSOP / 栈 ROP
>= 2.37  → 优先「任意读泄露 + 栈 ROP」，堆手法做基线
```

快速判定脚本：

```python
libc.version          # pwntools 自动解析，如 (2, 31)
'__free_hook' in libc.sym     # False 即 2.34+
libc.sym.get('_IO_wfile_jumps')
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 版本自适应利用框架：先探测能力，再选路线
from pwn import *

context.binary = elf = ELF("./pwn")
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

def v(lc):
    return tuple(int(x) for x in (lc.version or (0, 0)))

FEATURES = {
    "tcache":            (2, 26),
    "tcache_key":        (2, 29),
    "safe_linking":      (2, 32),
    "no_malloc_hook":    (2, 34),
    "io_str_jumps_fix":  (2, 35),
    "tcache_key_random": (2, 39),
}

def caps(lc):
    ver = v(lc)
    out = {k: ver >= thr for k, thr in FEATURES.items()}
    out["version"] = ver
    for s in ("__free_hook", "__malloc_hook", "_IO_list_all",
              "_IO_wfile_jumps", "_IO_str_jumps", "environ"):
        out[s] = s in lc.sym
    return out

def mangle(pos, ptr, c):
    return ((pos >> 12) ^ ptr) if c["safe_linking"] else ptr

def demangle(pos, enc, c):
    return ((pos >> 12) ^ enc) if c["safe_linking"] else enc

def plan(c):
    """根据能力矩阵给出推荐路线"""
    if c["version"] < (2, 34):
        return "__free_hook + system  （最稳）"
    if c["_IO_wfile_jumps"]:
        return "_IO_wfile_jumps FSOP 或 environ→栈 ROP"
    return "environ→栈 ROP"

# ---------- 统一：把 tcache 攻击抽象成「写任意地址」 ----------
def tcache_write(chunk_pos, target, value, c):
    """chunk_pos: 被改写的 tcache chunk 的 next 字段地址"""
    enc = mangle(chunk_pos, target, c)
    log.info(f"mangled next = {hex(enc)}  (safe_linking={c['safe_linking']})")
    return p64(enc), value           # 第一次 edit 写 enc，第二次 add 时写 value

def heap_leak_from_enc(chunk_pos, enc, c):
    """2.32+ 从 mangled next 反推真实指针"""
    if not c["safe_linking"]:
        return enc
    return demangle(chunk_pos, enc, c)

if __name__ == "__main__":
    c = caps(libc)
    for k, val in c.items():
        info(f"{k:22s} = {val}")
    success("推荐路线: " + plan(c))

    # 用 libc 里的已知符号算出 arm 位置，用于各版本适配
    if c["version"] < (2, 34):
        success(f"__free_hook = {hex(libc.sym['__free_hook'])}")
    if c["_IO_list_all"]:
        success(f"_IO_list_all = {hex(libc.sym['_IO_list_all'])}")
    p = start()
    p.interactive()
```

本地对齐运行环境（关键一步）：

```bash
# 1) 下载对应版本 libc
./glibc-all-in-one/download 2.31-0ubuntu9.9_amd64
# 2) patchelf 到题目版本
patchelf --set-interpreter ./ld-2.31.so --set-rpath . ./pwn_patched
# 3) 验证
./pwn_patched        # ldd 应显示 ./libc.so.6
```

## 五、常见坑 / 变体

- **2.31 的 `main_arena`**：不再导出符号，`libc.sym['main_arena']` 报错；用 `__malloc_hook + 0x10 + 0x60` 近似，或用 libc-database 反查低 12 位。
- **2.32 的 `unlink`**：safe-linking 同时作用于 fastbin 与 tcache，`fd` 也要 mangle。
- **2.34 的 writeup 全废**：网上大量老 writeup 用 `__free_hook`，遇到 22.04 环境必须换招。
- **2.35 的 `_IO_str_jumps`**：`_allocate_buffer` 改为内部 `malloc`，House of Orange 需要重写。
- **2.39+ 的 `tcache_key`**：`key = tcache ^ (pos>>12)`，double-free 检测更难绕。
- **musl 环境**：完全不同的分配器（`mallocng`），上述所有手法失效。
- **静态链接**：`libc.version` 拿不到，用 `strings` 读版本号后手工对照本表。

## 六、参考来源

- [0x434b: Overview of GLIBC heap exploitation techniques](https://0x434b.dev/overview-of-glibc-heap-exploitation-techniques/)
- [how2heap（按 glibc 版本分目录的 demo）](https://github.com/shellphish/how2heap)
- [glibc 最新 malloc.c](https://elixir.bootlin.com/glibc/latest/source/malloc/malloc.c)
- [glibc 2.31 malloc.c（hook 时代）](https://elixir.bootlin.com/glibc/glibc-2.31/source/malloc/malloc.c)
- [glibc-all-in-one（各版本 libc / ld 下载）](https://github.com/matrix1001/glibc-all-in-one)
- [ir0nstone: Safe Linking](https://ir0nstone.gitbook.io/notes/binexp/heap/safe-linking)
- [Research Innovations: Bypassing Safe Linking](https://www.researchinnovations.com/post/bypassing-the-upcoming-safe-linking-mitigation)

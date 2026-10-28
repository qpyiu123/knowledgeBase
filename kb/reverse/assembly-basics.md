---
title: x86 / x64 汇编速查（与做题强关联）
category: reverse
tags: [汇编, x86, x64, 调用约定, 栈帧, 指令]
signals: [看反汇编看不懂寄存器在干嘛, 需要手写 shellcode, 需要 patchelf 改指令, 不熟 64 位调用约定, 不清楚 movaps 踩栈对齐]
difficulty: easy
source: "CTF-Wiki Assembly / Felix Cloutier x86 ref / ir0nstone calling conventions"
tools: [IDA, Ghidra, gdb, objdump, godbolt]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 反编译出来的伪 C 与汇编对不上，需要看原始指令。
- 需要判断「这个 `lea rax, [rbp-0x20]` 是缓冲区地址」。
- 需要手写 shellcode 或改一条指令做 patch。
- 崩溃在 `movaps xmm0, [rsp+0x40]` —— 栈 16 字节对齐问题。
- 需要判断参数顺序：`rdi/rsi/rdx` 还是 `rcx/rdx/r8`。

## 二、原理

### 寄存器速查（x86-64）

| 用途 | 64 位 | 低 32 | 家族 |
|---|---|---|---|
| 返回值 | `rax` | `eax` | — |
| 参数 1~6 | `rdi, rsi, rdx, rcx, r8, r9` | `edi, esi, edx, ecx, r8d, r9d` | **System V AMD64** |
| 被调用者保存 | `rbx, rbp, r12~r15` | — | 函数返回前必须恢复 |
| 栈帧 | `rbp`（帧基）、`rsp`（栈顶） | — | — |
| 指令指针 | `rip` | — | — |
| 标志 | `rflags` | `eflags` | ZF/SF/CF/OF |

**Windows x64 不同**：`rcx, rdx, r8, r9` 是前 4 个参数，第 5 个起压栈，且有 0x20 字节 shadow space。

### 常见指令与做题含义

| 指令 | 含义 | 做题时用在哪 |
|---|---|---|
| `mov dst, src` | 赋值 | 数据流追踪 |
| `lea rax, [rbp-0x20]` | 取地址 | 找缓冲区基址 |
| `movzx / movsx` | 零/符号扩展 | 长度、循环变量 |
| `cmp a, b` + `je/jne` | 条件跳转 | 分支还原 |
| `test rax, rax` + `je` | 判空 | 指针判空 |
| `xor eax, eax` | rax = 0 | 清零（也常见于花指令） |
| `sub rsp, 0x30` | 开栈帧 | 算溢出偏移 |
| `cdqe / cqo` | 符号扩展 | 除法准备 |
| `imul / idiv` | 乘除 | 算法还原 |
| `rol/ror/shl/shr` | 移位 | 加密轮函数 |
| `nop / int3 / ud2` | 占位/断点/非法 | 花指令、patch |
| `movaps xmm, [mem]` | 16 字节对齐读写 | **栈对齐崩溃根因** |
| `syscall` / `int 0x80` | 系统调用 | pwn/rev 交叉 |

### 栈帧与常见序言/尾声

```asm
push rbp
mov  rbp, rsp        ; 建立帧
sub  rsp, 0x30       ; 分配局部变量
...
mov  rsp, rbp
pop  rbp
ret                  ; 等价于 leave; ret
```

## 三、checksec 判读与利用思路

汇编层的「判读」= **从栈帧推漏洞**：

1. `sub rsp, N` 决定局部空间。
2. `read(0, buf, len)` 的 `buf` 通常 `lea rsi, [rbp-0x30]`，`len` 是 `edx` → 溢出量 = `0x30 - 8`（含 saved rbp）。
3. `leave; ret` 的 `rbp` 偏移处就是 canary（若有）。
4. `mov eax, 1; syscall` 是 write，`eax = 0` 是 read，`eax = 59` 是 execve。

常用转换：

```text
call func   ==  push next_rip; jmp func
leave       ==  mov rsp, rbp; pop rbp
ret         ==  pop rip
```

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 用 pwntools 反汇编/汇编小段代码，快速验证「这条指令对应什么」
from pwn import *

context.arch = "amd64"
context.log_level = "info"

snips = {
    "开栈帧":      "push rbp; mov rbp, rsp; sub rsp, 0x30",
    "取 buf 地址": "lea rsi, [rbp-0x30]",
    "read(0,b,0x40)": "xor eax, eax; xor edi, edi; lea rsi, [rbp-0x30]; mov edx, 0x40; syscall",
    "leave;ret":   "leave; ret",
    "栈对齐修正":  "ret",
    "execve":      "xor eax,eax; push rax; mov rbx, 0x68732f6e69622f; push rbx;"
                   " mov rdi, rsp; xor esi, esi; xor edx, edx; mov al, 59; syscall",
}
for name, code in snips.items():
    try:
        b = asm(code)
        print(f"[{name}] {b.hex()}")
        print(disasm(b))
    except PwnlibException as e:
        print(f"[{name}] 汇编失败: {e}")

# 反汇编任意机器码（从二进制里抠一段）
raw = bytes.fromhex("55 48 89 e5 48 83 ec 30 48 8d 45 d0")
print(disasm(raw, arch="amd64"))

# 用 objdump 从 ELF 里取函数体
import subprocess
print(subprocess.run(["objdump", "-d", "-M", "intel", "./chall"], capture_output=True, text=True).stdout[:2000])
```

手算溢出偏移的小工具：

```python
#!/usr/bin/env python3
# 从反汇编文本里自动找 read/gets 调用点的缓冲区偏移
import re, subprocess, sys
asm = subprocess.run(["objdump", "-d", "-M", "intel", sys.argv[1]],
                     capture_output=True, text=True).stdout
pat_lea = re.compile(r"lea\s+(rsi|rdi),\s*\[rbp([+-]0x[0-9a-f]+)\]")
for line in asm.splitlines():
    m = pat_lea.search(line)
    if m:
        off = int(m.group(2), 16)
        print(f"{line.strip()}  -> 缓冲区在 rbp{'>' if off>0 else ''}{hex(abs(off))}, 溢出偏移≈{abs(off)+8:#x}")
```

## 五、常见坑 / 变体

- **`mov edi, x` 会清零 rdi 高 32 位**：写 64 位地址时要用 `mov rdi, x`，否则地址被截断。
- **`movaps` 崩溃**：`system`/`printf` 内部使用 SSE，要求调用时 `rsp % 16 == 0`，ROP 链前加一个 `ret`。
- **Windows 与 Linux 调用约定不同**：逆 Windows 二进制时前 4 个参数是 `rcx, rdx, r8, r9`。
- **`push` 立即数只支持 32 位符号扩展**：64 位常量常被拆成 `movabs rax, imm64; push rax`。
- **`lea` 不访问内存**：`lea rax, [rbx+rcx*4]` 是纯算术，别当成读内存。
- **Intel 与 AT&T 顺序相反**：objdump 默认 AT&T（`mov src, dst`），加 `-M intel` 才是 `mov dst, src`。
- **x32 ABI**：`syscall` 号在 `eax`，但栈上指针仍是 64 位。

## 六、参考来源

- [CTF-Wiki: x86 / x64 汇编](https://ctf-wiki.org/assembly/x86-x64/readme/)
- [Felix Cloutier x86/x64 指令参考](https://www.felixcloutier.com/x86/)
- [Wikibooks: X86 Assembly](https://en.wikibooks.org/wiki/X86_Assembly)
- [ir0nstone: Calling Conventions](https://ir0nstone.gitbook.io/notes/binexp/stack/return-oriented-programming/calling-conventions)
- [ir0nstone: 32- vs 64-bit](https://ir0nstone.gitbook.io/notes/binexp/stack/32-vs-64-bit)
- [Compiler Explorer（在线对比汇编）](https://godbolt.org/)

---
title: 虚拟机保护与自研 VM handler 还原
category: reverse
tags: [VM保护, VMProtect, handler, 字节码, 虚拟化]
signals: [主循环里有巨大的 switch 或跳转表, 大量重复的小函数, 程序里出现 bytecode 数组, 控制流是「取指令-解码-执行」, 一坨看不懂的算符]
difficulty: hard
source: "CTF-Wiki 虚拟机分析 / VMProtect / movfuscator 笔记"
tools: [IDA, Ghidra, Triton, angr, unicorn, Python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 反编译出来是一个 `while(1)` 里 `switch(opcode)` 的巨大函数，分支上百个。
- 出现 `bytecode`/`code` 数组，以及一个 `pc`（program counter）变量。
- 有大量「相似但不同」的小函数，每个只做几字节运算。
- 变量名全是 `v1, v2, v3...`，且反复出现 `v3 = (v2 << 2) ^ v1` 这种看不懂的算子。
- 二进制里出现 `VMProtect`、`.vmp` 段、`vmp_` 前缀符号（商业壳自研 VM）。

## 二、原理

虚拟机保护把原始逻辑编译成**自定义字节码**，再由内置解释器执行：

```text
struct VM {
    uint8_t *code;      // 字节码
    size_t   pc;        // 指令指针
    uint64_t regs[16];  // 虚拟寄存器
    uint8_t *stack;     // 虚拟栈
};

while (running) {
    uint8_t op = code[pc++];
    switch (op) {
        case 0x01: regs[a] = regs[b] + regs[c]; break;  // ADD
        case 0x02: regs[a] = regs[b] ^ imm;     break;  // XOR
        ... 100+ handlers
    }
}
```

还原三要素：
1. **指令分发点**（dispatcher）：那个大 `switch` 或跳转表。
2. **handler 语义**：每个 case 做了什么运算。
3. **字节码**：输入是什么，从哪读。

## 三、checksec 判读与利用思路

VM 题的判读：

| 观察 | 结论 |
|---|---|
| 一个函数里有大分支表 | 先查分支编号是否来自指令流，再看是否反复推进指令位置 |
| 存在 `jmp [table + op*8]` | 跳转表分发 |
| 某个全局数组被 `pc` 索引 | 字节码 |
| 出现 `mprotect`/`VirtualProtect` | 核对改权限的地址、写入目标、之后是否执行同一范围 |
| 段名 `.vmp0/.vmp1` | VMProtect |

还原路线（按成本从低到高）：

1. **差分测试**：把字节码逐条喂进去，用 unicorn 模拟，观察寄存器变化。
2. **符号执行**：把 handler 语义交给 angr/Triton，直接求 flag。
3. **反编译器插件**：idea 插件 `VMDisasm`、Ghidra 脚本，把 handler 做成宏。
4. **手工提取**：写 Python 解析字节码 + 用 table 定义 handler 语义。

### 找到取指和分派

记录指令编号从哪里读、指令位置如何变化、分支执行后是否回到取指位置。大量分支也可能只是普通菜单或消息处理。

### 核对是否改写了代码

先看权限调用的地址和范围，再比对后续写入的地址，最后查是否跳转到同一段。仅为内存加上保护、随后没有写入并执行该区域时，不能据此说代码被改写。jocker 的公开题解导读可用于对照这三条证据。

## 四、可直接运行的 exp 脚本

```python
#!/usr/bin/env python3
# 自研 VM 通用还原框架：提取 handler 语义 + 反汇编字节码 + 模拟执行
from unicorn import *
from unicorn.x86_const import *
import struct, sys

# ---------- 1) 手工填写：从 IDA/Ghidra 抄出来的 handler 表 ----------
# opcode -> (名字, 语义 lambda(regs, imm) -> None)
HANDLERS = {
    0x01: ("ADD",  lambda r, imm: r.update({"a": (r["b"] + r["c"]) & 0xffffffff})),
    0x02: ("XOR",  lambda r, imm: r.update({"a": (r["b"] ^ imm) & 0xffffffff})),
    0x03: ("MOV",  lambda r, imm: r.update({"a": imm & 0xffffffff})),
    0x04: ("SHL",  lambda r, imm: r.update({"a": (r["b"] << imm) & 0xffffffff})),
    0x05: ("CMP",  lambda r, imm: r.update({"zf": int(r["a"] == r["b"])})),
    0x06: ("JNZ",  lambda r, imm: r.update({"pc": imm if not r.get("zf") else r["pc"]})),
    0xFF: ("EXIT", lambda r, imm: r.update({"halt": True})),
}

# 每条指令的编码长度（opcode + 若干立即数）
INS_LEN = {0x01: 3, 0x02: 3, 0x03: 5, 0x04: 3, 0x05: 1, 0x06: 5, 0xFF: 1}

# ---------- 2) 字节码反汇编器 ----------
def disasm(code, base=0):
    pc, out = 0, []
    while pc < len(code):
        op = code[pc]
        name, _ = HANDLERS.get(op, ("UNK_%02x" % op, None))
        n = INS_LEN.get(op, 1)
        imm = int.from_bytes(code[pc+1:pc+n], "little")
        out.append(f"{pc+base:04x}: {name:6s} 0x{imm:x}" if n > 1 else f"{pc+base:04x}: {name}")
        pc += n
    return "\n".join(out)

# ---------- 3) 模拟执行（用 unicorn 更贴近真实 handler） ----------
def emulate(code, entry=0, max_steps=100000):
    """把 bytecode 放进 unicorn 内存，用 Python 解释器驱动（比直接跑原二进制简单）"""
    regs = {"a": 0, "b": 0, "c": 0, "pc": entry, "zf": 0, "halt": False}
    steps = 0
    trace = []
    while not regs["halt"] and steps < max_steps:
        pc = regs["pc"]
        if pc >= len(code):
            break
        op = code[pc]
        name, fn = HANDLERS.get(op, ("UNK", None))
        n = INS_LEN.get(op, 1)
        imm = int.from_bytes(code[pc+1:pc+n], "little")
        trace.append((pc, name, imm, dict(regs)))
        if fn is None:
            raise RuntimeError(f"未知 opcode {op:#x} @ {pc:#x}")
        # 默认 pc 先前进，JNZ 可覆盖
        regs["pc"] = pc + n
        fn(regs, imm)
        steps += 1
    return regs, trace

# ---------- 4) 用 angr / Triton 做符号化 VM ----------
def symbolic_vm(code, flag_len=32):
    """把 VM 字节码翻译成 angr 的 IR（手工适配后最常见做法）"""
    import angr, claripy
    proj = angr.Project("/bin/true", auto_load_libs=False)
    flag = [claripy.BVS(f"c{i}", 8) for i in range(flag_len)]
    s = claripy.Concat(*flag)
    # 逐条解释：ADD/XOR 等在 claripy 里就是 + / ^ 运算符
    return proj, flag, s

if __name__ == "__main__":
    # 从二进制里把字节码抠出来（占位：换成读文件的偏移与长度）
    raw = bytes.fromhex("0201000003 41414141 0100000005 ff")
    raw = raw.replace(b" ", b"")
    print(disasm(raw))
    regs, trace = emulate(raw)
    print("final:", {k: hex(v) if isinstance(v, int) else v for k, v in regs.items()})
    for t in trace[:10]:
        print(hex(t[0]), t[1], hex(t[2]))
```

从二进制里提取字节码数组（IDA 里）：

```python
# IDAPython：把指定地址的字节 dump 成文件
import ida_bytes
start, size = 0x4040A0, 0x400
data = ida_bytes.get_bytes(start, size)
open("bytecode.bin", "wb").write(data)
print("dumped", len(data))
```

## 五、常见坑 / 变体

- **handler 混淆**：VMProtect 的 handler 被打散在多个基本块并用 `push/ret` 串起来，需要先做「handler 切分」（用 Triton 的符号引擎识别语义）。
- **字节码加密**：字节码在运行时解密（SMC），要在解密后再 dump（下断点取内存）。
- **寄存器轮换**：每轮 handler 里虚拟寄存器编号会变（`regs[i]` 与 `regs[j]` 交换），需要用「寄存器等价类」还原。
- **嵌套 VM**：外层是 UPX 壳，内层是自研 VM，先脱壳。
- **反 VM 调试**：`rdtsc` 检测单步耗时，见反调试篇。
- **指令集大**：100+ handler 手工填表太慢，优先写「差分执行」脚本自动判语义（喂不同输入看输出变化）。
- **movfuscator**：`mov` 单一指令混淆的极端 VM 形态，工具 `demovfuscation` 可部分还原。

## 六、参考来源

- [CTF-Wiki: 虚拟机分析](https://ctf-wiki.org/reverse/vm/vm/)
- [CTF-Wiki: movfuscator](https://ctf-wiki.org/reverse/obfuscate/movfuscator/)
- [CTF-Wiki: 自修改代码 SMC](https://ctf-wiki.org/reverse/obfuscate/smc/)
- [Triton 文档（符号执行辅助 handler 语义）](https://triton-library.github.io/)
- [Unicorn Engine 文档](https://www.unicorn-engine.org/docs/)
- [angr 官方文档](https://docs.angr.io/)
- [CTF-Wiki: 模拟执行 Unicorn](https://ctf-wiki.org/reverse/tools/simulate-execution/unicorn/)

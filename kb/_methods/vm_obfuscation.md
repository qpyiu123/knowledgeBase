---
title: 方法卡 · 自研 VM 逆向（handler 判语义 / 字节码反汇编 / 模拟执行）
category: reverse
tags: [方法卡, vm, bytecode, dispatcher, handler, 模拟执行, 花指令, 平坦化]
signals:
  - 一个函数 switch 分支超过 30 个
  - 出现 jmp [table + op*8] 跳转表分发
  - 全局数组被 pc 索引后逐条解码
  - 有 bytecode 数组与 pc 变量
  - 大量相似但不同的小 handler 函数
  - 反编译报 call analysis failed
  - 函数里 jmp 跳到指令中间
  - 主循环加 state 变量分发
difficulty: hard
source: kb/reverse/vm-protection.md, kb/reverse/obfuscation-junk.md
tools: [python, 内置脚本, ida, ghidra, unicorn, triton]
updated: 2026-11-03
---

# 方法卡 · 自研 VM 逆向（handler 判语义 / 字节码反汇编 / 模拟执行）

## 适用场景

- 反编译出来是一个 `while(1)` 里 `switch(opcode)` 的巨大函数，分支上百个；
- 二进制里能挖出 `bytecode` 数组 + 一个 `pc` 变量，程序行为由它驱动；
- 校验逻辑被搬进 VM，`Correct`/`Wrong` 只差 VM 跑完后的一个分支；
- 混合保护：外有 `call analysis failed` 花指令、内有平坦化 `switch(state)`，VM 埋在中间；
- 题面要 flag，直接爆破不行（输入要过 VM 里的多轮运算），必须还原指令集。

## 前置条件

- 能静态定位**指令分发点**（大 `switch` 或 `jmp [table + op*8]`）与 handler 表基址；
- 能 dump 出字节码（静态从段里抠，或 SMC 解密后下断点取内存）；
- 已经过反调试层（`rdtsc`/`ptrace` 检测，见 `kb/reverse/anti-debugging.md`）；
- 本卡脚本**只做纯 Python 的语义判定与模拟执行**，不加载 unicorn/angr，离线可跑。

## 步骤

1. **认 VM**：`switch` > 30 分支、`jmp [table+op*8]`、`code[pc++]` 三件套任意满足两件即可判定。
2. **切 handler**：VMProtect 的 handler 被 `push/ret` 打散，先按跳转表把每个 case 的入口切出来，
   记下 `opcode -> 入口地址 -> 指令长度（opcode + 立即数字节数）`。
3. **差分判语义**：给每个 handler 喂 `regs` 不同取值，看输出怎么变——
   `r[a] = r[b] + r[c]` 呈现线性可加、`r[a] = r[b] ^ imm` 呈现按位翻转、`r[a]=imm` 与输入无关。
   本卡脚本 `judge_handler(samples)` 直接从采样中推出 `out = k1*x + k2*y + c (mod 2^32)` 或异或常数。
4. **填指令集**：把 `OPCODES` 表（本卡给了一套 7 条示范集：ADD/XOR/MOV/SHL/CMP/JNZ/EXIT）改成交付题的真实表。
5. **反汇编 + 模拟**：`--dis` 出汇编，`--emu` 用 Python 解释器跑，把 `flag[i]` 当未知量；
   需要真解时把 trace 喂给 angr/Triton（本卡给出 `--smt` 的纯 Python 求逆路径：线性约束直接高斯消元）。

```powershell
# 反汇编字节码（演示指令集：MOV a=0x41 / XOR a=r[b]^0 / EXIT）
.\.venv\Scripts\python.exe kb/_methods/scripts/vm_obfuscation.py --dis '0341 0200 ff'
# 模拟执行并打印寄存器轨迹（输出 AB）
.\.venv\Scripts\python.exe kb/_methods/scripts/vm_obfuscation.py --emu --trace --hex '0341 07 0342 07 ff'
# 从采样推断某个 handler 的语义（每组 x y out，至少 3 组）
.\.venv\Scripts\python.exe kb/_methods/scripts/vm_obfuscation.py --judge 1000 1 5661 --judge 2000 3 6663 --judge 3000 5 7665
```

## 脚本

脚本路径：`kb/_methods/scripts/vm_obfuscation.py`（纯标准库，离线）

- `OPCODES`：`opcode -> (名字, 立即数字节数, 语义函数)`，默认 7 条；
- `disasm(code)`：按 `INS_LEN` 逐条切分，遇到未知 opcode 明确报错并给出偏移；
- `emulate(code, trace=False, max_steps=100000)`：带 `pc` 前进与 `JNZ` 覆盖 pc 的简单解释器，
  有步数上限防死循环；返回 `(regs, trace)`；
- `judge_handler(samples)`：输入若干 `(x, y, out)` 采样，判定是 `const` / `xor_const` / `x + k2*y + c (mod 2^32)`，
  至少 3 组；采样不足会明确报错而不是乱猜；
- `--selftest`：固定 seed 下自检（反汇编、模拟输出、拒绝、语义差分、参数不足），退出码 0 才算过。

## 失效场景

- **handler 被打散（VMProtect）**：`push/ret` 串起来的 handler 用纯静态表切不出来，要先做 handler 切分（Triton 符号引擎），
  本卡的 `judge_handler` 只对"一函数一 handler"的样式有效。
- **字节码运行时解密（SMC）**：静态 dump 到的是密文，必须下断点取解密后的内存，否则 `--dis` 全是垃圾。
- **寄存器轮换**：每轮 `regs[i]` 与 `regs[j]` 交换，静态表里的 `index` 会漂移，要先建"寄存器等价类"再套 `OPCODES`。
- **花指令导致错位**：`jmp loc+1` / `push imm32; ret` 会让线性反汇编错位，`call analysis failed` 时先 `del_items` + `create_insn`。
- **嵌套 VM / movfuscator**：外层壳内层 VM，或单指令（`mov`）混淆的极端形态，`demovfuscation` 只能部分还原，别指望脚本直出。
- **判语义误判**：采样点太少时 `judge_handler` 会把 `x + 2y` 判成 `x + y`，至少给 3 组线性无关采样。

## 相关文档

- `kb/reverse/vm-protection.md`（dispatcher / handler / bytecode 三要素与 unicorn 框架）
- `kb/reverse/obfuscation-junk.md`（花指令、控制流平坦化、`switch(state)` 还原）
- `kb/reverse/anti-debugging.md`（VM 外面包的一层反调试）
- 方法卡：`kb/_methods/binary_patch.md`（直接把 VM 里的分支 patch 掉）

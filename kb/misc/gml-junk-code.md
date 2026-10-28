---
title: 垃圾代码与程序流反转（junk code / gml 脚本）
category: misc
tags: [花指令, 垃圾代码, 控制流反转, 混淆, gml, 逆向]
signals: [程序里有一堆无关指令, 反汇编出现 call 后紧跟垃圾字节, 程序逻辑看起来是反的, 输入正确却说错误, 题面提到 gml 或脚本, 反编译结果跳转很乱]
difficulty: hard
source: "CTF-Wiki 花指令章节 / 控制流平坦化 / movfuscator 文档"
tools: [ida, ghidra, x64dbg, radare2, python, capstone, remill]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 反汇编里到处是 `jmp +0`、`push/pop` 成对出现、`xor eax,eax; inc eax` 这种无意义指令。
- IDA 的 F5 反编译结果**逻辑明显不对**（比如判断条件反了）。
- 题面直接给 `challenge.gml`（GameMaker 脚本）或一段用脚本语言写的混淆逻辑。
- x64dbg 单步时不断跳进"垃圾代码"后再跳回来。
- 二进制体积比源码大很多，`.text` 段熵值很高。

## 二、原理

**花指令（junk code）** 是插在正常指令流里的**永远不执行**或**执行了也不影响状态**的指令，目的有两个：

1. **打断线性反汇编**：静态分析器按字节线性扫描，插入的垃圾字节会让后续指令解码错位（如 `EB 01 xx` 制造假分支）。
2. **阻断反编译**：令 CFG 变形，F5/Hex-Rays 放弃或给出错误伪代码。

**程序流反转（control-flow inversion）**：把 `if (correct) success();` 改写成 `if (!correct) goto fail; success();`，再插入多层嵌套与混淆，使静态阅读时"成功分支"看起来是失败分支。**gml/脚本类题目**里更常见的是：出题人写一个脚本把"flag 校验"写反，或者用 GML（GameMaker Language）的 `with`/事件驱动把判断藏在不同事件里。

**做题核心思想**：不看反汇编，看**行为**——动态执行、patch 掉花指令、或用符号执行/ESIL 让引擎自己走过去。

## 三、操作步骤

1. **定位关键输出**：`strings` 找 `Correct`/`Wrong`/`flag`，交叉引用回算法处。
2. **识别花指令模式**：`jmp $+5` / `call $+5; pop reg` / `pushf; ...; popf` / 条件恒假的跳转。
3. **用 IDA 的 `P` 键**把错位处重新定义为代码，手动 patch 掉垃圾字节。
4. **动态跟**：在成功/失败分支下断点，观察真实走向，配合条件断点跳过循环。
5. **脚本化**：用 capstone/unicorn 写脚本，自动识别并 NOP 掉花指令。
6. **gml 类**：找到入口脚本（`gml_Object_obj_xxx_Create_0`），用 GameMaker 的 `show_debug_message` 或改 `gml_GlobalScript_*` 让判断反向。

## 四、命令/脚本

### 识别常见花指令模式

```bash
# 1) EB 00 / EB 01 / E9 00 00 00 00：跳到下一条指令
# 2) 68 xx xx xx xx C3：push addr; ret —— 等价 jmp
# 3) 50 58：push eax; pop eax（成对无意义）
# 4) 9C 9D：pushf; popf
# 5) E8 00 00 00 00 58：call $+5; pop eax，用于拿到 EIP
# 用 capstone 扫描（Python）
```

```python
#!/usr/bin/env python3
# junk_scan.py —— 用 capstone 标出可疑花指令序列
import sys
from capstone import *
from capstone.x86 import *

data = open(sys.argv[1], 'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True
hits = 0
for ins in md.disasm(data, 0):
    s = f'{ins.mnemonic} {ins.op_str}'
    if (ins.mnemonic == 'jmp' and ins.op_str in ('0x0',)) or \
       (ins.mnemonic == 'call' and ins.op_str == str(ins.address + 5)) or \
       (ins.mnemonic in ('push', 'pop') and ins.op_str in ('rax', 'eax')):
        print(f'0x{ins.address:x}: {s}')
        hits += 1
print('suspects:', hits)
```

### GCC inline asm 花指令的构造方式（理解题目如何生成）

```c
// 理解花指令的制造手法，便于反推
#define JUNK() asm volatile(
  "jmp 1f\n"
  "1: xor %eax, %eax\n"
  "push %eax\n"
  "pop %eax\n"
  ::: "eax");
```

### 在 IDA 里批量清理

```
1. 打开 Options -> General -> 勾选 "Stack pointer"（便于观察异常）
2. 在垃圾指令处按 U（取消定义），再用 C 从正确起点重新反汇编
3. 选中花指令区间 -> Edit -> Patch program -> Change byte -> 改成 90 (NOP)
4. 保存到输入文件后交给动态调试验证
```

### 用 Unicorn 跑通（只看行为，不反编译）

```python
#!/usr/bin/env python3
# unicorn_emu.py —— 把二进制加载到 Unicorn 里执行核心函数（伪代码，按目标调整）
from unicorn import *
from unicorn.x86_const import *

CODE = 0x400000
STACK = 0x7ffff000
uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(CODE, 0x10000)
uc.mem_map(STACK, 0x10000)
uc.mem_write(CODE, open('target.bin', 'rb').read()[:0x10000])
uc.reg_write(UC_X86_REG_RSP, STACK + 0x8000)
uc.reg_write(UC_X86_REG_RIP, CODE)

try:
    uc.emu_start(CODE, CODE + 0x5000, timeout=3 * 10**6)
except UcError as e:
    print('stop:', e, hex(uc.reg_read(UC_X86_REG_RIP)))
```

### GameMaker（gml）脚本反转

```python
# GameMaker 的 data.win（或 game.unx）里有 gml 字节码；
# UndertaleModTool 可以反编译并导出全部脚本，找判断逻辑。
# 导出后常见写法：
#   if (flag_ok) { show_message("Wrong!"); } else { show_message("Correct!"); }
# 直接改条件或把 show_message 内容对调即可。
```

```bash
# 用 undertale-tool / UndertaleModCli 批量导出
UndertaleModCli.exe dump data.win -o dumpdir
grep -rn "gml_GlobalScript" dumpdir | head
# 找到校验脚本后，改 show_message 参数即可
```

### 反转判断的最短路径

```asm
; 原始：jnz fail   （真实语义：不等就失败）
; 反转：改成 jz fail / 或直接 nop 掉整个分支
; 在 x64dbg 里：
;   Ctrl+G 跳到地址 -> 空格编辑汇编 -> 把 jnz 改成 nop / jmp
;   Ctrl+P 把补丁应用回文件
```

## 五、常见坑 / 变体

- **只 NOP 不重设 CFG**：IDA 不会自动重新分析交叉引用，需 `Options → General → 重新分析`。
- **花指令依赖真实执行**：有些题的花指令**确实会被执行**（比如 `push reg; ret` 实现跳转），直接 NOP 会崩，要按语义还原成 `jmp`。
- **movfuscator**：整个程序只用 `mov` 指令实现，静态分析几乎不可行，只能用动态 trace 或直接给它任意输入看行为。
- **控制流平坦化（OLLVM）**：用 `deflat.py`（IDA 插件）或 angr 的 CFG 还原。
- **gml 版本差异**：GameMaker 2.3+ 用 `gml_GlobalScript_xxx` 命名，导出后按字符串定位。
- **misc 与 reverse 交叉**：本题在 misc 下更强调"看清行为再猜逻辑"，算法还原部分见 kb/reverse。

## 六、参考来源

- [CTF Wiki - 花指令](https://ctf-wiki.org/reverse/obfuscate/junk-code/)
- [CTF Wiki - 控制流平坦化](https://ctf-wiki.org/reverse/obfuscate/control-flow-flatten/)
- [CTF Wiki - movfuscator](https://ctf-wiki.org/reverse/obfuscate/movfuscator/)
- [capstone 反汇编框架文档](https://www.capstone-engine.org/lang_python.html)
- [Unicorn 引擎文档](https://www.unicorn-engine.org/docs/)
- [UndertaleModTool - GameMaker data.win 反编译](https://github.com/UnderminersTeam/UndertaleModTool)

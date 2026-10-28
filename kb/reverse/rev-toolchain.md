---
title: 逆向工具链与快捷键速查（IDA / Ghidra / Binary Ninja / radare2）
category: reverse
tags: [工具链, IDA, Ghidra, Binary Ninja, radare2, 快捷键]
signals: [拿到 exe/elf 不知用哪个工具, 需要批量看函数, 想用命令行自动化, 团队里工具不统一, 需要脚本扩展分析]
difficulty: easy
source: "CTF-Wiki Reverse Tools / Ghidra 官方文档 / IDA 官方"
tools: [IDA, Ghidra, Binary Ninja, radare2, Cutter, x64dbg]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 PE（`.exe`/`.dll`）、ELF、Mach-O，需要先判断用什么工具。
- 题目规模大（函数上千），需要能批量搜索/自动标注的工具。
- 需要写脚本扩展（IDA IDAPython / Ghidra Jython / BN Python3 / r2 pipe）。
- 队友用不同工具，需要一个「同一操作在四个工具里怎么做」的对照。

## 二、原理

反汇编器把字节解成指令，反编译器把指令重建为类 C 代码。四类工具的分工：

| 工具 | 反编译器 | 脚本 | 强项 |
|---|---|---|---|
| IDA Pro | Hex-Rays（最强） | IDAPython | 生态、FLIRT、调试器集成 |
| Ghidra | 自带 C 反编译器 | Java / Jython / Python(Jython) | 免费、开源、逆向工程 API 全面 |
| Binary Ninja | BNIL（多级 IR） | Python3 | API 优雅、批量分析、IL 好用 |
| radare2/Cutter | pdc / ghidra-decompiler 插件 | r2pipe | 命令行、批处理、管道化 |

**关键概念**（四家通用）：
- 交叉引用（XREF）：谁调用了这个函数 / 谁读了这块数据。
- 函数签名（signature）：还原参数个数与类型（FLIRT / 类型库）。
- 结构体定义：把 `mov eax, [rcx+0x10]` 变成 `s->field_10`。

## 三、checksec 判读与利用思路

逆向题的「判读」是**文件格式判读**：

```bash
file ./chall                      # PE / ELF / Mach-O / .pyc / .apk / .wasm
python3 -c "import pefile,sys; pe=pefile.PE(sys.argv[1]); print([e.dll for e in pe.DIRECTORY_ENTRY_IMPORT])" ./chall.exe
readelf -hS ./chall               # ELF 段表 / 入口
strings -a ./chall | head -50     # 先扫字符串找提示
```

| 特征 | 判断 | 首选工具 |
|---|---|---|
| `UPX!` 段 | UPX 壳 | `upx -d` |
| `.NET` 目录、`mscoree.dll` | .NET | dnSpyEx / ILSpy |
| `UnityPlayer.dll`、`GameAssembly.dll` | Unity il2cpp | Il2CppDumper |
| `libil2cpp.so`、`global-metadata.dat` | Android il2cpp | Il2CppDumper |
| `classes.dex` | APK | jadx / apktool |
| `.pyc` magic（`\x55\x0d\x0d\x0a` 等） | Python 字节码 | pycdc / decompyle3 |
| Go build id、`runtime.*` | Golang | GoReSym |
| `rust_panic`、`core::` | Rust | rustfilt |
| `<Import>` 里 `System` 一大堆 | .NET | ILSpy |
| 大量 `br_table`、`i32.load` | WebAssembly | wabt / wasm2wat |

## 四、可直接运行的 exp 脚本

### IDA / IDAPython 常用片段

```python
# IDAPython 3.x（在 IDA 的 Script Command 里执行，或存成 .py 用 Alt+F7）
import idautils, idc, idaapi, ida_funcs, ida_bytes

def dump_funcs(lo=0x401000, hi=0x410000):
    for ea in idautils.Functions(lo, hi):
        print(hex(ea), ida_funcs.get_func_name(ea), idc.get_func_attr(ea, idc.FUNCATTR_SIZE))

def xrefs_of(ea):
    return [hex(x.frm) for x in idautils.XrefsTo(ea)]

def find_imm(target):
    """全局搜索立即数引用（找 magic 比较）"""
    return [hex(ea) for ea in idautils.Heads() if ida_bytes.is_imm(ida_bytes.get_flags(ea), target)]

def callchain(fname):
    ea = idc.get_name_ea_simple(fname)
    for x in idautils.XrefsTo(ea, 0):
        print(hex(x.frm), idc.get_func_name(x.frm))
```

### Ghidra 无头批处理（导出全部反编译）

```python
# ghidra_export.py —— 用 analyzeHeadless 跑
# $GHIDRA/support/analyzeHeadless /tmp/proj MyProj -import ./chall -postScript dump.py
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

decomp = DecompInterface(); decomp.openProgram(currentProgram)
monitor = ConsoleTaskMonitor()
for f in currentProgram.getFunctionManager().getFunctions(True):
    res = decomp.decompileFunction(f, 60, monitor)
    if res and res.decompileCompleted():
        print("/* %s @ %s */" % (f.getName(), f.getEntryPoint()))
        print(res.getDecompiledFunction().getC())
```

### radare2 命令行（最适合批量 + 管道）

```bash
r2 -A ./chall                      # -A = 完整分析
# 在 r2 内：
#   afl              列函数
#   pdf @ main       反汇编 main
#   pdc @ main       伪 C 反编译
#   axt @ sym.imp.strcmp   交叉引用
#   /R pop rdi; ret  搜 ROP gadget
#   iz / izz         字符串
#   s 0x401000       跳转
# 一条命令直接出结果：
r2 -q -c "aaa; pdf @ main" ./chall
# 批量导出所有函数反汇编
r2 -q -c "aaa; afl~[0]" ./chall | while read a; do r2 -q -c "pdf @ $a" ./chall; done > all.asm
```

### Binary Ninja Python

```python
# BN 的 Python 控制台
from binaryninja import *
bv = load("/path/to/chall", options={"analysis.mode": "full"})
for f in bv.functions:
    print(hex(f.start), f.name, f.symbol.type)
# MLIL 看变量流（比汇编高一档）
for mlil_insn in bv.get_function_at(0x401000).mlil:
    print(mlil_insn)
```

## 五、常见坑 / 变体

- **Ghidra 中文显示乱码**：`Edit → Tool Options → Listing Fields → set charset = GB2312/GBK`，或在脚本里 `setCharset`。
- **IDA 自动切到 Thumb/ARM**：`Alt+G` 手动指定；ARM64 用 `64-bit ARM`。
- **r2 分析太慢**：用 `aa` 代替 `aaa`，或 `e anal.timeout=60`。
- **Binary Ninja 免费版功能受限**：`analysis.mode` 只能用 basic，函数名不还原。
- **Ghidra 反编译空函数**：先 `Analyze Headless` 完整跑一遍，或 `Auto Analyze` 勾上 `Decompiler Parameter ID`。
- **IDA 的 FLIRT 签名**：找静态库函数（如 libc 静态链接）先跑 `sig` 库识别，能省一半时间。

## 六、参考来源

- [CTF-Wiki: IDA Pro](https://ctf-wiki.org/reverse/tools/static-analyze/ida/)
- [CTF-Wiki: Ghidra](https://ctf-wiki.org/reverse/tools/static-analyze/ghidra/)
- [Ghidra 官方（NSA）](https://ghidra.re/)
- [Ghidra GitHub 仓库与 GhidraDocs](https://github.com/NationalSecurityAgency/ghidra)
- [Hex-Rays IDA Pro 官方](https://hex-rays.com/ida-pro/)
- [Binary Ninja 官方文档](https://docs.binary.ninja/)
- [radare2 官方](https://rada.re/n/)
- [Cutter（radare2 GUI）](https://cutter.re/)

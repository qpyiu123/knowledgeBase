---
title: Ghidra 反编译实战流程
category: reverse
tags: [Ghidra, 反编译, headless, 脚本, 类型恢复]
signals: [只有 Ghidra 可用（无 IDA 授权）, 需要批量分析上千函数, 需要写脚本自动找 flag 校验, 需要还原结构体与函数签名, 需要做二进制对比]
difficulty: medium
source: "Ghidra 官方 / GhidraClass / ghidra.re API 文档"
tools: [Ghidra, analyzeHeadless, ghidra_scripts, jython]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 环境里没有 IDA Pro，只能用免费工具。
- 题目函数极多（>1000），需要脚本自动化找比较点。
- 需要把反编译结果导出成 C 代码喂给 LLM 或 grep。
- 需要做版本 diff（Ghidra 有 Version Tracking 功能）。
- 目标是 Linux ELF / Android so，Ghidra 对多架构支持好。

## 二、原理

Ghidra 的分析流水线：

```text
Import（识别格式：PE/ELF/Mach-O/DEX…）
  → Disassembly（线性扫描 + 递归下降）
  → Decompiler Parameter ID（推断参数与局部变量类型）
  → Data Type Propagation（结构体传播）
  → Decompiler（生成 C 伪代码）
  → 脚本/插件（PCode 级分析）
```

反编译器输出的是 **P-Code** 中间表示再还原成 C，所以：
- 变量命名靠类型推断，`undefined8` / `longlong` 表示未知类型。
- 结构体需要手动 `Create Structure` + `Auto Fill in`。
- 函数签名可从库签名库（`.gdt`）批量套用。

## 三、checksec 判读与利用思路

Ghidra 中没有 checksec，但有等价的**分析前置检查**：

```text
File → Properties        ：看架构、编译器、语言（x86:LE:64:default）
Window → Memory Map      ：看段权限（RWX 段是可疑点）
Functions → Function ID  ：识别库函数
Search → For Strings     ：找 flag 提示
```

分析策略：

1. **入口点定位**：ELF 看 `entry`，PE 看 `EntryPoint`，Android 看 `JNI_OnLoad`。
2. **字符串交叉引用**：`Search → For Strings`，右键 `References → Show References to`。
3. **结构调整**：`Decompiler → Edit Function Signature`，把 `f(undefined8 a, undefined8 b)` 改成 `f(char *buf, int len)`。
4. **批量脚本**：`Windows → Script Manager`，或 `analyzeHeadless`。

## 四、可直接运行的 exp 脚本

### 1. 无头批量反编译（推荐主力）

```bash
# Linux/macOS 路径示例
GHIDRA=/opt/ghidra
$GHIDRA/support/analyzeHeadless /tmp/ghproj MyProj \
  -import ./chall \
  -overwrite \
  -scriptPath ./scripts \
  -postScript dump_decomp.py \
  -deleteProject
# 输出重定向
$GHIDRA/support/analyzeHeadless /tmp/ghproj P -import ./chall -postScript dump.py > decomp.c 2>err.log
```

### 2. dump_decomp.py（导出所有函数伪 C）

```python
#@category CTF
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

decomp = DecompInterface()
decomp.openProgram(currentProgram)
monitor = ConsoleTaskMonitor()

fm = currentProgram.getFunctionManager()
count = 0
for f in fm.getFunctions(True):
    res = decomp.decompileFunction(f, 60, monitor)
    if res and res.decompileCompleted():
        code = res.getDecompiledFunction().getC()
        print("// ===== %s @ %s (size=%d)" % (f.getName(), f.getEntryPoint(), f.getBody().getNumAddresses()))
        print(code)
        count += 1
print("// total functions decompiled:", count)
```

### 3. find_cmp.py（自动找「输入与常量比较」的位置）

```python
#@category CTF
# 思路：找 CMP / CMP const 且操作数涉及输入缓冲区指针的函数
from ghidra.program.model.symbol import SymbolType

hits = []
listing = currentProgram.getListing()
for ins in listing.getInstructions(True):
    mn = ins.getMnemonicString().upper()
    if mn not in ("CMP", "SUB", "XOR", "TEST"):
        continue
    for i in range(ins.getNumOperands()):
        obj = ins.getOpObjects(i)
        for o in obj:
            # 立即数且看起来像输入比较
            try:
                if o.isConstant() and 0x20 <= o.getValue() <= 0x7e:
                    hits.append("%s  %s" % (ins.getAddress(), ins))
            except Exception:
                pass

for h in hits[:200]:
    print(h)
print("// total:", len(hits))
```

### 4. 用 P-Code 还原简单混淆常量

```python
#@category CTF
# 把 mov eax, imm 的数字打印出来，便于发现魔数（AES S-box / CRC 表）
from ghidra.program.model.lang import Register
for ins in currentProgram.getListing().getInstructions(True):
    pcode = ins.getPcode()
    for p in pcode:
        if "COPY" in p.getMnemonic() and p.getNumInputs() == 1:
            inp = p.getInput(0)
            if inp.isConstant() and inp.getValue() > 0x10000:
                print("%s  const=0x%x   (%s)" % (ins.getAddress(), inp.getValue(), ins))
```

### 5. 用 API 调 Decompiler（Python 直接调 headless 更灵活）

```python
#!/usr/bin/env python3
# 通过 pyhidra / ghidra_bridge 从普通 Python 调 Ghidra
import pyhidra
pyhidra.start()
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

with pyhidra.open_program("./chall") as api:
    prog = api.getCurrentProgram()
    dec = DecompInterface(); dec.openProgram(prog)
    mon = ConsoleTaskMonitor()
    for f in prog.getFunctionManager().getFunctions(True):
        r = dec.decompileFunction(f, 60, mon)
        if r and r.decompileCompleted():
            print(r.getDecompiledFunction().getC())
```

## 五、常见坑 / 变体

- **Ghidra 默认字符集**：中文二进制显示乱码，改为 `GBK` 或在脚本里 `setBytes` 后自行解码。
- **Thumb 与 ARM 混排**：Ghidra 自动判错时手动 `Disassemble` 并指定 `ARM/Thumb`。
- **Jython 而非 Python3**：`analyzeHeadless` 默认 Jython 2.7，不能用 f-string 与 `pathlib`；要 Python3 用 `pyhidra`。
- **函数签名推断失败**：先跑 `Auto Analyze` 勾上 `Decompiler Parameter ID`（耗时但效果好）。
- **`-deleteProject` 会删掉分析结果**：需要反复跑时去掉该参数复用项目。
- **导出代码量巨大**：`dump_decomp.py` 对 1000+ 函数会输出几十 MB，加过滤（只导有字符串引用的函数）。
- **P-Code 与汇编混用**：做数据流分析用 P-Code，找人肉逻辑用伪 C，两者交叉验证。

## 六、参考来源

- [Ghidra 官方站点](https://ghidra.re/)
- [Ghidra GitHub（含 GhidraDocs 与 GhidraClass）](https://github.com/NationalSecurityAgency/ghidra)
- [GhidraClass 培训课件目录](https://github.com/NationalSecurityAgency/ghidra/tree/master/GhidraDocs/GhidraClass)
- [Ghidra 反编译改进技术讲义（PDF）](https://github.com/NationalSecurityAgency/ghidra/blob/stable/GhidraDocs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf)
- [Ghidra API 文档（Program/Listing）](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/package-summary.html)
- [CTF-Wiki: Ghidra](https://ctf-wiki.org/reverse/tools/static-analyze/ghidra/)

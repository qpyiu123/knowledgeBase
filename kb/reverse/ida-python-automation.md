---
title: IDA 插件与 Python 自动化（批量分析、自动改名、反编译导出）
category: reverse
tags: [idapython, ida, automation, decompile, plugin]
signals: [目标函数上千个且需要批量处理, 需要把伪代码批量导出成文本, 有大量逐字节比较函数需要自动识别, 题面要求「找出所有引用 X 的地方」, 二进制有几百个 sub_ 需要命名, 需要提取所有字符串并关联引用, 题目带 .idb / .i64 数据库, 需要比对两个版本的差异函数, 存在大量相似的结构体要批量命名]
difficulty: medium
source: "IDA Python API / Ghidra Headless"
tools: [ida, idapython, python, ghidra]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 手工点了几百个 `sub_` 还没头绪，题目需要"批量分析"。
- 题目描述里提到"给出所有可疑函数"、"自动提取"、"批量 dump"。
- 二进制里字符串、常量、比较循环重复数百次。
- 需要把函数伪代码导出来用 grep/脚本二次处理。
- 题面有 `.idb`、`.i64` 附件（说明是 IDA 工程），或要求"用 IDA 分析"。
- 需要跨版本 diff（两个 `.so`）。
- 需要给 `qword_*`、`off_*` 批量应用结构体。

## 二、原理

### 1. IDAPython 的三个入口

| 场景 | 模块 | 用途 |
|---|---|---|
| IDA GUI 脚本 | `idaapi`、`idc`、`idautils` | 交互式分析 |
| 交互式控制台 | `ida_kernwin` | 命令、窗口 |
| **无 GUI 批处理** | `ida -A -S script.py target` | CI / 批量 |

### 2. 关键 API

```python
idautils.Functions()              # 所有函数地址
idautils.FuncItems(ea)            # 函数内指令
idautils.CodeRefsTo(ea, flow)     # 谁调用了它
idautils.Names()                  # 所有命名
ida_bytes.get_strlit_contents()   # 字符串
ida_funcs.set_func_name()         # 改名
ida_hexrays.decompile(ea)         # 反编译（需要 Hex-Rays）
ida_typeinf.apply_type()          # 应用结构体
```

### 3. Hex-Rays 批量反编译

`ida_hexrays.decompile(func_ea)` 返回 `cfunc` 对象，`str(cfunc)` 得到伪代码。**注意**：反编译很慢，建议先 `init_hexrays_plugin()` 并开启 `decompiler_ready`。

## 三、解题步骤

1. **确认环境**：`ida64.exe -A -S"script.py" target`，脚本里判断 `idc.get_inf_attr(INF_MODULE_NAME)`。
2. **先摸清函数数**：`len(list(idautils.Functions()))`，决定是否要分批。
3. **写定向脚本**：
   - 找 `strcmp`/`memcmp` 调用者 → 自动改名 `check_<hash>`。
   - 找 `XOR` 密集函数 → 标 `crypto_candidate`。
   - 找引用 `flag` 字符串的函数 → 反向追踪。
4. **导出伪代码**：逐函数 dump 到 `decompiled/`。
5. **二次处理**：grep 出 `if ( *a1 == 0x66 )` 之类的逐字比较。
6. **应用结果**：`idc.set_name()` 改名、`ida_typeinf` 赋结构体，最后保存。

## 四、可直接运行的脚本

无 GUI 批处理骨架：

```python
# ida_batch.py
import idaapi, idautils, idc, ida_funcs, ida_bytes, ida_hexrays, ida_nalt

def main():
    out = []
    n = 0
    for ea in idautils.Functions():
        name = idc.get_func_name(ea)
        if name.startswith("sub_"):
            n += 1
            out.append((ea, name, idc.get_func_size(ea)))
    print("unnamed funcs:", n)
    with open("unnamed.txt", "w") as f:
        for ea, name, size in out:
            f.write("0x%X %s %d\n" % (ea, name, size))

main()
idaapi.qexit(0)
```

```bash
# 运行（-A 表示无界面，-S 指定脚本）
ida64 -A -S"ida_batch.py" target.exe
```

批量反编译并导出伪代码：

```python
# ida_decompile_all.py
import os, idaapi, idautils, idc, ida_hexrays

OUT = "decompiled"
os.makedirs(OUT, exist_ok=True)

if not ida_hexrays.init_hexrays_plugin():
    print("Hex-Rays 不可用")
    idaapi.qexit(1)

ok = 0
for ea in idautils.Functions():
    try:
        cf = ida_hexrays.decompile(ea)
        if cf is None:
            continue
        fn = "%s_%X.c" % (idc.get_func_name(ea).replace(".", "_"), ea)
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write("// %s @ 0x%X\n%s" % (idc.get_func_name(ea), ea, str(cf)))
        ok += 1
    except Exception as e:
        pass
print("decompiled", ok)
idaapi.qexit(0)
```

自动给"逐字节比较"函数改名（CTF 最常用）：

```python
# rename_checks.py —— 识别形如 if (byte_XXX[i] == const) 的检查函数
import idautils, idc, ida_bytes, ida_hexrays, re

PAT = re.compile(r"==\s*0x([0-9A-Fa-f]{1,2})")

def rename_checks():
    for ea in idautils.Functions():
        name = idc.get_func_name(ea)
        if not name.startswith("sub_"):
            continue
        try:
            cf = ida_hexrays.decompile(ea)
        except Exception:
            continue
        if cf is None:
            continue
        src = str(cf)
        cmps = PAT.findall(src)
        if len(cmps) >= 4:                       # 连续比较 → 大概率是校验
            new = "maybe_check_%x" % ea
            idc.set_name(ea, new, idc.SN_NOWARN | idc.SN_FORCE)
            print("0x%X -> %s (%d cmps)" % (ea, new, len(cmps)))

rename_checks()
```

导出所有字符串与其引用：

```python
# dump_strings.py
import idautils, idc, ida_bytes, ida_funcs

for s in idautils.Strings():
    try:
        txt = str(s)
    except Exception:
        continue
    if len(txt) < 4:
        continue
    refs = []
    for ea in idautils.CodeRefsTo(s.ea, 0):
        f = ida_funcs.get_func(ea)
        refs.append("%s+0x%X" % (idc.get_func_name(f.start_ea) if f else "?",
                                 ea - (f.start_ea if f else ea)))
    if refs:
        print("%-60s %s" % (txt[:60], ", ".join(refs[:5])))
```

无 IDA 时用 Ghidra Headless 做同样的事：

```bash
analyzeHeadless.bat C:\ghidra_proj proj1 \
  -import target.exe -postScript ExportAllFunctions.java -deleteProject
```

## 五、常见坑 / 变体

- **`-A` 模式没有 GUI**：任何 `idaapi.warning()` 会阻塞，用 `print` 代替。
- **`qexit` 必须调用**，否则进程不退出。
- **Hex-Rays 反编译大函数很慢**：先筛 `func_size`，跳过超过 20KB 的。
- **中文字符串**：`ida_bytes.get_strlit_contents` 的编码要设 `STRTYPE_C_16` 或 UTF-8。
- **改名冲突**：`SN_NOWARN | SN_FORCE` 强制覆盖。
- **变体：IDAPython 与 IDA 版本绑定**：IDA 7.x 用 `idaapi`，IDA 9.x 部分 API 移到 `ida_*` 子模块。
- **变体：source-level debug 信息**：`ida_nalt.retrieve_input_file_pdb` 自动加载 PDB。
- **变体：导出为 .py 脚本给 Ghidra**：用 `ida_kernwin.execute_sync` 分线程。
- **变体：跨版本 diff**：用 `bindiff` 或自己写 `idautils.Functions()` 的哈希对比。

## 六、参考来源

- [idapython/src](https://github.com/idapython/src)
- [IDA Python API 文档](https://python.docs.hex-rays.com/)
- [Hex-Rays 官方站](https://www.hex-rays.com/)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
- [Ghidra Headless Analyzer](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Features/Base/src/main/java/ghidra/app/util/headless/HeadlessAnalyzer.java)
- [Reverse Engineering StackExchange — 批量改名](https://python.docs.hex-rays.com/)

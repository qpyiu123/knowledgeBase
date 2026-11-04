---
title: 方法卡 · HTTP 请求走私（CL.TE / TE.CL / TE.TE / H2 降级）
category: web
tags: [request-smuggling, cl-te, te-cl, te-te, h2-downgrade, 缓存投毒]
signals: [Server 是 nginx 但报错栈是 Tomcat 或 Gunicorn, 响应出现 Via 或 X-Cache 说明有反代, 非法 chunked 请求后下一个请求才 400, 题面出现 反代 或 前后端不一致 或 smuggling, 同时出现 Content-Length 与 Transfer-Encoding, 浏览器侧 HTTP2 而回源是 HTTP1.1]
difficulty: hard
source: kb/web/http-request-smuggling.md, kb/web/web-cache-poisoning-deception.md
tools: [burpsuite, python, http-smuggler]
updated: 2026-11-03
---

# 方法卡 · HTTP 请求走私（CL.TE / TE.CL / TE.TE / H2 降级）

## 适用场景

- 响应头组合异常：`Server: nginx` + `X-Powered-By: Servlet/3.1`，或 `Server: cloudflare` + 后端 500 堆栈；
- 出现 `Via:`、`X-Cache:`、`X-Forwarded-For:` → 明确两层（前端代理 + 后端应用）；
- 题面提示：`反代`、`前后端`、`proxy`、`smuggling`、`走私`、`chunked`、`TE`、`Content-Length`；
- `Transfer-Encoding: chunked` 且 body 不合法时，前端放行而后端 400（或反之）；
- 有 bot/爬虫访问、要求"让 admin 访问 `/admin`"、有 CSRF token 但"能绕过一次"；
- 浏览器侧 HTTP/2 且路径里能塞 `%0d%0a`。

## 前置条件

- 前后端对**请求边界**的判定必须不同（CL 与 TE 取舍、重复 TE、`TE :` 空格、大小写）；
- 连接必须**可复用**：前端 keep-alive 才有效，每次新建连接走私不成立；
- 不能用 `requests`：它会重写 header、拒绝 `\r\n` 与 CL+TE 共存 → 用原始 socket 或 Burp；
- 本卡脚本**离线**：只拼原始报文、给判定建议，不发包。

## 步骤

1. **确认两层**：`Server`、`Via`、`X-Cache`、`X-Powered-By` 全看一遍，脚本 `--cache-headers` 可分析键控关系。
2. **探 CL.TE**：`--build HOST --kind cl.te --cl <len>`，前端按 CL 截断 → 残留成为下一请求；第二次请求超时/错位即命中。
3. **探 TE.CL**：`--build HOST --kind te.cl`，前端只转发块尺寸行，后端按 chunked 继续等数据。
4. **探 TE.TE**：`--te-variants` 出两两混淆组合（`identity`、`TE :`、`\t`、`xchunked`、大小写），哪一端不认哪一个就成立。
5. **H2 降级**：`--kind h2`，`Content-Length: 0` + `Transfer-Encoding: chunked` + 残留 body；Burp 切 HTTP/2 时 header 名必须小写。
6. **利用**：伪造 `/404-xyz` 确认错位（`--judge` 判定），再升级为前缀劫持（偷下一个用户的 cookie）、绕前端鉴权（前端看 `/public`、后端看 `/admin`）、配合 `--cache-probes` 打缓存投毒。

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/http_smuggling.py --build target --kind cl.te --cl 18 --raw
.\.venv\Scripts\python.exe kb/_methods/scripts/http_smuggling.py --te-variants
.\.venv\Scripts\python.exe kb/_methods/scripts/http_smuggling.py --judge '第二次请求返回 404'
```

## 脚本

脚本路径：`kb/_methods/scripts/http_smuggling.py`（纯标准库，离线）

- `build(host, kind, smuggled, path, cl, te_headers)`：`cl.te` / `te.cl` / `te.te` / `cl.cl` / `h2` 五类原始报文；`cl` 显式给出时按该长度**截断** body，模拟前端只转发一部分；
- `front_back(req, front, back)`：按两端对 CL/TE 的取舍算消耗字节与残留，`desync=True` 即可能走私；
- `_chunked_len(body)`：chunked 实际被消耗的字节数；`te_candidates()`：TE 混淆组合；
- `cache_probes(path)` / `cache_key_analysis(headers)` / `judge(text)`：缓存欺骗探针、键控分析、现象判定；
- `--selftest`：6 组固定断言，退出码 0 才算过。

## 失效场景

- **后端 HTTP/1.0**：完全不认 chunked，报文直接 400，走私不成立。
- **前端归一化**：Nginx 默认把 TE 改写为 `chunked` 并按 CL 判定，CL.TE 被打，必须换 TE.CL 或 TE.TE。
- **连接不复用**：CDN 每次新建连接则残留随连接销毁，永远打不到下一个用户。
- **两端都是同版本框架**：RFC 9110 里 TE 优先的规则实现一致，无可利用差异。
- **H2 header 名大写**：H2 强制小写，大写名直接判协议错误，降级走私失败。
- **污染共享连接池**：走私会打乱别人会话，且每次复测前必须重连，否则误判。

## 相关文档

- `kb/web/http-request-smuggling.md`（原理表、CL.TE/TE.CL 报文、Burp 插件用法）
- `kb/web/web-cache-poisoning-deception.md`（走私配合缓存投毒、缓存欺骗后缀探针）

---
title: "SECCON 13 CTF Final 作問記"
category: pwn
tags: ["SECCON 13 CTF Final", "pwn", "fastcgi", "go", "http-header-injection", "host-splitting"]
signals: ["SECCON 13 CTF Final 2025", "fastcgi", "go", "http-header-injection", "host-splitting", "report-to", "crlf-injection", "url-shortener", "open-redirect", "pwn_unknown", "SECCON", "CTF", "Final", "FastCGI"]
difficulty: hard
source: "https://www.ctfiot.com/230944.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON 13 CTF Final 作問記

> 赛事：SECCON 13 CTF Final 2025 | 方向：pwn | 难度：hard

## 一句话总结

SECCON 13 CTF Final 作問記：FastCGI HTTP 头注入 HTTP_GIVEMEFLAG 触发 flag + URL 短链 + nginx ngx_http_validate_host ':' 切分触发 host 注入 + OAuth 错位 + CSP Report-To 缓存中毒。

## 攻击链

1. 题目 1 fcgi-go: 自建 FastCGI 服务器 + HTTP 头 Givemeflag 触发 flag
2. nginx.conf 拦截 $http_givemeflag return 403
3. 绕过: FastCGI 协议头 FCGI_PARAMS type=4 注入 HTTP_GIVEMEFLAG=true
4. a\x01\x04\x00\x01\x00\x15\x00\x00\x0f\x04HTTP_GIVEMEFLAGtrue + 大量 a
5. 题目 2 url-shortener: OAuth 流程 + URL 短链 + nginx 路由
6. 短链 original_url = URLShortener.get_original_url(short_code)
7. if scheme != http/https → normalized_url = https://Host/+url
8. nginx ngx_http_validate_host host 包含 : 切分 sw_usual/sw_rest
9. host_len = i (':' 位置) + state = sw_rest → host->len = host_len
10. 攻击: Host: app:%0d%0ahogehoge → host 切到 app: + 后续 \r\n 注入新响应头
11. proxy_set_header Host $http_host 传递注入的 host
12. 注入 Report-To / NEL 头触发 SSRF
13. admin.example.com + Cookie: state=a + /auth/callback?code=...%23 → OAuth state 绕过
14. get_state_from_cookie(req.headers.get('Cookie')) 取 state 比对
15. 302 Location: https://app:hogehoge/anything 触发 host 头截断
16. URL: code 参数注入 %26login_target=APP%23 二次解析
17. 利用 CSP 允许 script-src-elem sha256 + inline JS 写 CSP
18. nginx proxy_cache HIT 缓存中毒 + 路径重定向到攻击者服务器
19. 完整链: Host 头注入 → URL 短链 + OAuth 错位 → 缓存中毒 → CSP 报告接收 → flag

## 关键 payload

```
Host: app:%0d%0ahogehoge + FastCGI FCGI_PARAMS \x01\x04\x00\x01\x00\x15\x00\x00\x0f\x04HTTP_GIVEMEFLAGtrue
```

## 经验教训

nginx ngx_http_validate_host host 头遇 ':' 切分是 CR/LF 注入经典绕过；FastCGI FCGI_PARAMS 可注入 HTTP 头绕 nginx $http_givemeflag 拦截；OAuth state 仅从 cookie 读取但路径 /auth/callback 可被短链劫持是经典 open-redirect 链。

## 标签

fastcgi、go、http-header-injection、host-splitting、report-to、crlf-injection、url-shortener、open-redirect、oauth-flow、csp-bypass

## 参考来源

- https://www.ctfiot.com/230944.html
- 原文件：SECCON_13_CTF_Final_作問記.full.md

---
title: "SUCTF 2026 Ez_Router"
category: web
tags: ["SUCTF 2026", "web", "IoT", "router", "HTTP-CGI", "login-bypass"]
signals: ["SUCTF 2026 2026", "IoT", "router", "HTTP-CGI", "login-bypass", "JSON-XSS", "base64-decode", "RWX-heap", "UAF", "auth_bypass", "pwn_unknown", "web_unknown", "CGI", "RWX"]
difficulty: hard
source: "https://www.ctfiot.com/304030.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SUCTF 2026 Ez_Router

> 赛事：SUCTF 2026 2026 | 方向：web | 难度：hard

## 一句话总结

IoT 路由器 CGI 消息队列 + UAF 改函数指针 + RWX heap 跑 shellcode

## 攻击链

1. 前端越权: GET /www/http?auth=0&action=login → 拿 session_id=72cb56e041a043ee6dfc3427033ef203
2. 登录后访问 /control.html 控制台
3. 二进制架构: http (web) + mainproc (CGI 消息队列) + start.sh
4. Init() 用 mprotect 设 heap 为 RWX → 堆上可执行 shellcode
5. dispatch_action 处理 6 个 message type: Set_WIFI/Add_MAC/Set_VPN/Edit_VPN_Custom/Apply_VPN
6. vpn_config_req 结构体含 apply_cb 函数指针 + custom_ptr
7. Set_VPN: malloc 0x100 块，strcpy 8 个字段 (action/name/proto/server/user/pass/cert)
8. Edit_VPN_Custom: 改 custom_ptr → 当 0x21 字符时触发 UAF 越界到 apply_cb 字段
9. Apply_VPN() 调 apply_cb(req) → 跳到攻击者控制的 shellcode
10. payload: shellcode = execve(''/bin/sh'', [''-c'', ''cat flag > ./www/flag.html''])

## 关键 payload

```
shellcode.ljust(0x7eb, b'\x90') + b'\x00'  → Edit_VPN_Custom b'\x21\x5c
```

## 经验教训

IoT 路由器架构是 web+daemon 消息队列；RWX heap 是低级 bug；apply_cb 是攻击热点

## 标签

IoT、router、HTTP-CGI、login-bypass、JSON-XSS、base64-decode、RWX-heap、UAF、function-pointer、shellcode、VPN-config、apply-callback

## 参考来源

- https://www.ctfiot.com/304030.html
- 原文件：SUCTF2026_Ez_Router.full.md

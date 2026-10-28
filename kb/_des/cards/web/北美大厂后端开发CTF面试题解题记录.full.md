---
title: "北美大厂后端开发CTF面试题解题记录"
category: web
tags: ["Fetch Backend CTF (北美大厂面试题)", "web", "北美大厂面试", "Fetch Backend CTF", "列目录漏洞", "NaCl secretbox"]
signals: ["Fetch Backend CTF (北美大厂面试题) 2025", "北美大厂面试", "Fetch Backend CTF", "列目录漏洞", "NaCl secretbox", "pynacl", "openapi", "gRPC", "connect+json", "web_unknown", "CTF", "token", "NaCl", "secretbox"]
difficulty: easy
source: "https://www.ctfiot.com/230796.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 北美大厂后端开发CTF面试题解题记录

> 赛事：Fetch Backend CTF (北美大厂面试题) 2025 | 方向：web | 难度：easy

## 一句话总结

北美大厂后端 CTF 5 token: 列目录 + NaCl secretbox 解密 + openapi.yaml 接口 + connect+json gRPC。

## 攻击链

1. 题目: Fetch Backend CTF (美国后端开发岗线上面试题)
2. 5 个 token 隐藏, 不需要找全
3. Token1: 列目录漏洞 → /pages/token.md 直接访问
4. Token2: /pages/secretbox.md NaCl secretbox 解密
5. pip install pynacl
6. base64_key = dGhpc2lzYWtleXdpdGgzMmxldHRlcnNpbml0ZmV0Y2g=
7. base64_nonce = usbsgmFzQNjwMEEZVqJ6Hdy8MOJwMOiq
8. 解密 1: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IkpXVF9UT0tFTiJ9.ghpSD18...
9. 解密 2: NA_CL_SECRET_TOKEN
10. Token3: /pages/openapi.yaml 找 /token.v1.TokenService/GetToken + StreamToken
11. POST application/json + Token2 Bearer 拿到第 3 个 token
12. Token4: /StreamToken 接受 application/connect+json (connect+proto/grpc)
13. HTTP/2 415 Unsupported Media Type → connect+json 重试
14. Token5: 未拿到 (作者放弃)

## 关键 payload

```
pynacl nacl.secret.SecretBox + openapi.yaml + connect+json
```

## 经验教训

列目录漏洞是 Web 入门常见; NaCl secretbox 需 pynacl nacl.secret.SecretBox; openapi.yaml 暴露 gRPC 端点; connect+json 是 gRPC-Web 协议。

## 标签

北美大厂面试、Fetch Backend CTF、列目录漏洞、NaCl secretbox、pynacl、openapi、gRPC、connect+json、JWT

## 参考来源

- https://www.ctfiot.com/230796.html
- 原文件：北美大厂后端开发CTF面试题解题记录.full.md

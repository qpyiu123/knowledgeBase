---
title: "2024 第四届\"网鼎杯\"青龙组 writeup"
category: web
tags: ["2024 第四届网鼎杯 青龙组", "web", "网鼎杯", "青龙组", "存储型XSS", "admin-bot"]
signals: ["2024 第四届网鼎杯 青龙组 2024", "网鼎杯", "青龙组", "存储型XSS", "admin-bot", "fetch-exfil", "栈迁移", "ret2libc", "i386", "xss", "reverse", "block_cipher", "XSS", "exfil"]
difficulty: hard
source: "https://www.ctfiot.com/212654.html"
tools: ["Dirsearch"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 第四届"网鼎杯"青龙组 writeup

> 赛事：2024 第四届网鼎杯 青龙组 2024 | 方向：web | 难度：hard | 工具：Dirsearch

## 一句话总结

网鼎杯 2024 青龙组：XSS admin-bot exfil + 栈迁移 pwn + SM4 加密

## 攻击链

1. WEB02: /content/hash 路由 + dirsearch 扫 /flag 路由，3 按钮（提交/刷新/更新）
2. 存储型 XSS：<script>fetch('/flag').then(r=>r.text()).then(d=>fetch('/content/...', {body:'content=123'+d}))</script>
3. submit 提交触发 boss 审核 → XSS 弹到攻击者平台
4. PWN02: login 绕过 admin\x00 + admin123\x00 → leak 栈地址
5. vuln 栈溢出 → 栈迁移到栈地址 - 4 → ret_address → system('/bin/sh')
6. REVERSE01: Android MainActivity → check 走 native 加密 → 解 apk 看 jni
7. 加密逻辑是 SM4 国密 → 找 key 解密 flag

## 关键 payload

```
<script>fetch('/flag').then(...).then(...)</script> + submit
```

## 经验教训

存储型 XSS 必须靠 admin 触发；栈迁移到泄露地址可绕小 buffer；SM4 是国产商用密码

## 标签

网鼎杯、青龙组、存储型XSS、admin-bot、fetch-exfil、栈迁移、ret2libc、i386、SM4-国密、Android-NDK、native-check、fenjing

## 参考来源

- https://www.ctfiot.com/212654.html
- 原文件：2024第四届“网鼎杯”青龙组_writeup.full.md

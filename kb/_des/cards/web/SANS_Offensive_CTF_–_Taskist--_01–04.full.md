---
title: "SANS Offensive CTF - Taskist 01-04"
category: web
tags: ["SANS Offensive CTF", "web", "idor", "privilege-escalation", "ssrf", "lfi"]
signals: ["SANS Offensive CTF 2025", "idor", "privilege-escalation", "ssrf", "lfi", "file-read", "proc-self-environ", "burp-intruder", "file-protocol", "SANS", "Offensive", "CTF", "Taskist", "IDOR"]
difficulty: medium
source: "https://www.ctfiot.com/166045.html"
tools: ["BurpSuite"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SANS Offensive CTF - Taskist 01-04

> 赛事：SANS Offensive CTF 2025 | 方向：web | 难度：medium | 工具：BurpSuite

## 一句话总结

SANS Offensive CTF Taskist 4 题：IDOR 遍历 tasks/64 拿 flag1 + 改 user_id 改 admin 密码 + SSRF 测 LFI 读源码 + file:///root/flag.txt 读根目录。

## 攻击链

1. Taskist::01 IDOR: /api/tasks/64 越权访问 admin task 拿到 flag-1
2. 攻击: Burp Intruder 遍历 1-100 数字 payload
3. Taskist::02 权限提升: update password 接口 user_id 参数可改
4. 改 user_id 为 admin 的 user_id → 改 admin 密码 → 拿 flag-2
5. Taskist::03 SSRF: site_config 导入功能 url 参数可改
6. 攻击: 上传 dummy 文件 + Burp 拦截 + 改 url=http://attacker.com → SSRF confirmed
7. 利用 /proc/self/environ + /app/index.js 读源码
8. 提示: admin 还有 2/3 task pending, 提示 /app 目录
9. Brute force LFI 常见 payloads → /proc/*/* 敏感端点
10. 拿到 flag-3
11. Taskist::04 SSRF 链根目录: 文件上传触发 file:///
12. file:///etc/* 测根目录 → file:///root/flag.txt 读 root flag
13. 拿到 flag-4
14. 全程工具: Burp Suite Intruder / Collaborator

## 关键 payload

```
file:///root/flag.txt
```

## 经验教训

IDOR + 权限提升 + SSRF + LFI 是 OWASP Top 10 经典 4 链；Burp Intruder 数字遍历是 IDOR 探查基础；/proc/self/environ 读环境变量是 SSRF 提权必经之路。

## 标签

idor、privilege-escalation、ssrf、lfi、file-read、proc-self-environ、burp-intruder、file-protocol、jwt

## 参考来源

- https://www.ctfiot.com/166045.html
- 原文件：SANS_Offensive_CTF_–_Taskist--_01–04.full.md

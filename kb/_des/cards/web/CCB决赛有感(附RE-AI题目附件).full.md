---
title: "CCB 决赛有感 (附 RE/AI 题目附件)"
category: web
tags: ["CCB", "web", "实网渗透", "schema.sql", "文件上传改后缀PHP", "find -perm -4000 提权"]
signals: ["CCB 2026", "实网渗透", "schema.sql", "文件上传改后缀PHP", "find -perm -4000 提权", "fscan扫描", "DokiLogic Renpy rpyc", "unrpyc解密", "1.exe XOR 35", "web_unknown", "CCB", "schema", "sql", "PHP"]
difficulty: medium
source: "https://www.ctfiot.com/306981.html"
tools: ["PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCB 决赛有感 (附 RE/AI 题目附件)

> 赛事：CCB 2026 | 方向：web | 难度：medium | 工具：PHP、Python

## 一句话总结

CCB 决赛有感 — 实网渗透 schema.sql + 后台 PHP 改后缀 + find SUID 提权 + DokiLogic Renpy 1.exe XOR 35 还原 flag。

## 攻击链

1. 实网渗透: 扫目录 → schema.sql → 账号密码 → 后台文件上传 → 改后缀 PHP
2. 上线 supershell → find SUID 提权
3. /usr/bin/find . -exec /bin/bash -p ; -quit
4. fscan 扫到 app.java + protokms 邮件网关 → 触及盲区
5. DokiLogic: Renpy 游戏, script.rpyc → unrpyc 解
6. 主程序释放 1.exe, 捕获其输出
7. 输入字符串 XOR 35 与 exe 输出比较
8. flag = 1.exe 输出 XOR 35

## 关键 payload

```
schema.sql / 后台 PHP 改后缀 / find SUID 提权 / unrpyc / 1.exe XOR 35 / protokms 邮件网关
```

## 经验教训

实网渗透 4 步曲:目录扫 → 凭据/源码 → 上传 RCE → SUID 提权;Renpy .rpyc 必用 unrpyc 解;1.exe 硬编码可在 rpy 中提取后 python 调执行再 XOR。

## 标签

实网渗透、schema.sql、文件上传改后缀PHP、find -perm -4000 提权、fscan扫描、DokiLogic Renpy rpyc、unrpyc解密、1.exe XOR 35、app.java邮件网关

## 参考来源

- https://www.ctfiot.com/306981.html
- 原文件：CCB决赛有感(附RE-AI题目附件).full.md

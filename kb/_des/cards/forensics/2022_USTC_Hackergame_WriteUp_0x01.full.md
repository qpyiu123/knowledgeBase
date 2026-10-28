---
title: "2022 USTC Hackergame WriteUp 0x01"
category: forensics
tags: ["2022 USTC Hackergame (中科大信安赛)", "forensics", "rclone.conf", "AES-CTR", "Obscure", "Reveal"]
signals: ["2022 USTC Hackergame (中科大信安赛) 2022", "rclone.conf", "AES-CTR", "Obscure", "Reveal", "Go-crypt", "heilang", "SHA256", "HTTP", "forensic_disk", "misc_math", "web_unknown", "reverse", "USTC"]
difficulty: medium
source: "https://www.ctfiot.com/71252.html"
tools: ["Go", "Python", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 USTC Hackergame WriteUp 0x01

> 赛事：2022 USTC Hackergame (中科大信安赛) 2022 | 方向：forensics | 难度：medium | 工具：Go、Python、curl

## 一句话总结

USTC Hackergame 多题混战：rclone密码还原+Go AES-CTR+heilang正则

## 攻击链

1. Q1 grep: grep ''flag{'' . -aR 找 flag
2. Q2 rclone: 从 .config/rclone/rclone.conf 找 obfuscated password
3. Q3 Go AES-CTR 还原: 拿 cryptKey 32 字节 + Obscure 源码 → 写 Reveal
4. Q4 heilang 数组: a[1225|2381|...]=978 写正则提取
5. Q5 HTTP 抓包: curl -v 看 Host 头
6. Q6 URL 编码绕过: 双重 URL 编码
7. Q7 Planet 物理题
8. Q8 XSS / 内网穿透
9. Q9 LFSR / 流密码
10. Q10 0day PDF 解析

## 关键 payload

```
flag{get_rclone_password_from_config!_2oi3dz1}
```

## 经验教训

通用工具 rclone/curl/wireshark/python 都能解

## 标签

rclone.conf、AES-CTR、Obscure、Reveal、Go-crypt、heilang、SHA256、HTTP、URL编码、抓包、Planet

## 参考来源

- https://www.ctfiot.com/71252.html
- 原文件：2022_USTC_Hackergame_WriteUp_0x01.full.md

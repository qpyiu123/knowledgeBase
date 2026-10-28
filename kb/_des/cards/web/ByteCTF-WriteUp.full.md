---
title: "ByteCTF WriteUp"
category: web
tags: ["ByteCTF", "web", "clickhouse SSRF", "/files..目录穿越", "URL()函数", "user_01提权"]
signals: ["ByteCTF 2022", "clickhouse SSRF", "/files..目录穿越", "URL()函数", "user_01提权", "DNS bit 编码", "汉信码", "RX-SSTV", "bytezoom UAF", "sqli", "ByteCTF", "clickhouse", "URL", "SSRF"]
difficulty: medium
source: "https://www.ctfiot.com/954.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ByteCTF WriteUp

> 赛事：ByteCTF 2022 | 方向：web | 难度：medium

## 一句话总结

ByteCTF 2022 综合 — clickhouse URL() SSRF 提权 + DNS bit 0/1 转 ASCII + 汉信码/RX-SSTV + bytezoom pwn 狗/猫类型混淆 UAF + change_age 改 strings 指针 + free_hook→system。

## 攻击链

1. Web double sqli: clickhouse SQL, /files.. 目录穿越找 access .sql
2. user_01 权限 > user_2, 用 URL("http://0.0.0.0:8123/?user=user_01&password=...&query=select+flag+from+ctf.flag", CSV)
3. Misc frequently: DNS o.bytedanec.top 0, i.bytedanec.top 1, 8位一组转 ASCII
4. 前半 ByteCTF{^_^enJ0y&y0ur, 后半 UDP 追踪 sse1f_wIth_m1sc^^}
5. HearingNotBelieving: 汉信码 + RX-SSTV, ByteCTF{m4yB3_U_kn0W_S57V}
6. Pwn bytezoom: create cat+dog, select2 dog(0) cat(0) 触发 UAF, create dog(0) 复用 cat(0) 块
7. change_age 改 age 字段 (覆盖 cat.strings 指针) → leak libc
8. 改 tcache_entry → 改 free_hook → system → /bin/sh

## 关键 payload

```
clickhouse URL() / 0.0.0.0:8123 / user_01 password / DNS 0/1 转 8 位 ASCII / 汉信码 + RX-SSTV / dog cat 类型混淆 UAF / change_age 改 cat.strings / free_hook→system
```

## 经验教训

clickhouse URL() 是 SSRF 提权经典;DNS o/i 域名后缀隐写 0/1 bit 是常见 misc trick;类型混淆 + UAF 改指针字段是堆题经典链。

## 标签

clickhouse SSRF、/files..目录穿越、URL()函数、user_01提权、DNS bit 编码、汉信码、RX-SSTV、bytezoom UAF、dog/cat 类型混淆、free_hook→system、libc-2.31

## 参考来源

- https://www.ctfiot.com/954.html
- 原文件：ByteCTF-WriteUp.full.md

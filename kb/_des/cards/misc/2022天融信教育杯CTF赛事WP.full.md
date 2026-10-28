---
title: "2022 天融信教育杯 CTF 赛事 WP"
category: misc
tags: ["天融信教育杯 2022", "misc", "steghide", "base64", "PHPCMS", "SQL注入"]
signals: ["天融信教育杯 2022 2022", "steghide", "base64", "PHPCMS", "SQL注入", "文件读取", "hexdump", "爆破", "misc_unknown", "SQL", "extract", "d05a274a4f864148d5b08c48b8c", "jpg", "flag"]
difficulty: easy
source: "https://www.ctfiot.com/59676.html"
tools: ["netcat", "steghide"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 天融信教育杯 CTF 赛事 WP

> 赛事：天融信教育杯 2022 2022 | 方向：misc | 难度：easy | 工具：netcat、steghide

## 一句话总结

杂烩：steghide 隐写 + base64 + PHPCMS 路径穿越 + SQL 注入 + 数组硬编码。

## 攻击链

1. steghide extract -sf 0073d05a274a4f864148d5b08c48b8c.jpg 提 flag
2. base64 嵌套 base64 解码得 flag
3. read start.txt 数字段拼成 zip 字节流
4. list.php?id=22 unIoN selECt 大小写混写注入
5. PHPCMS members_bind_info[temp_avatar] 路径穿越读 db.php
6. MD5(uid+timestamp) 爆破 avatar 路径
7. nc + echo Content-Length 过大触发堆叠
8. strings 8.raw | grep flag 取内存字符串
9. a1 数组硬编码 32 字节拼成 flag

## 关键 payload

```
flag{3661386562366162333565313332396130373363313239656230356332636566}
```

## 经验教训

PHPCMS 路径穿越要拼 timestamp 字典爆破 avatar 路径；steghide 隐写密码是入门考点。

## 标签

steghide、base64、PHPCMS、SQL注入、文件读取、hexdump、爆破

## 参考来源

- https://www.ctfiot.com/59676.html
- 原文件：2022天融信教育杯CTF赛事WP.full.md

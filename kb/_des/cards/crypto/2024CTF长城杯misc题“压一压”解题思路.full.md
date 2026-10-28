---
title: "2024 CTF 长城杯 misc 题 \"压一压\" 解题思路"
category: crypto
tags: ["长城杯", "crypto", "zip 套娃", "密码爆破", "WinRAR", "16 进制单字符"]
signals: ["长城杯 2024", "zip 套娃", "密码爆破", "WinRAR", "16 进制单字符", "pass.txt 链", "misc_math", "crypto_unknown", "zip", "pass", "txt"]
difficulty: medium
source: "https://www.ctfiot.com/170258.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 CTF 长城杯 misc 题 "压一压" 解题思路

> 赛事：长城杯 2024 | 方向：crypto | 难度：medium

## 一句话总结

16 进制密码 zip 套娃逐字符 WinRAR 爆破。

## 攻击链

1. 解压 压一压.zip 得 pass.txt 含 ? 通配符 → 脚本读 pass.txt 把 ? 替换为 a-f 0-9 共 16 字符逐一试 WinRAR → 成功解压的字符就是 flag 的一位 → 新 zip 里有新 pass.txt → 循环直到全部解出

## 关键 payload

```
WinRAR 命令 -ibck -y -p{password} ; replace '?' with a-f0-9 ; subprocess.run WinRAR.exe
```

## 经验教训

大量小 zip 套娃 + 单字符 16 进制密码时，单字符逐位爆破比全密码字典快 16 倍。

## 标签

zip 套娃、密码爆破、WinRAR、16 进制单字符、pass.txt 链

## 参考来源

- https://www.ctfiot.com/170258.html
- 原文件：2024CTF长城杯misc题“压一压”解题思路.full.md

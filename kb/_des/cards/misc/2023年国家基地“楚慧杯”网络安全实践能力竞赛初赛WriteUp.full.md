---
title: "2023 年国家基地\"楚慧杯\"网络安全实践能力竞赛初赛 WriteUp"
category: misc
tags: ["楚慧杯 2023", "misc", "哈希扩展攻击", "sqlmap盲注", "栈溢出", "TEA"]
signals: ["楚慧杯 2023 2023", "哈希扩展攻击", "sqlmap盲注", "栈溢出", "TEA", "zip套娃", "RSA_Boneh-Durfee", "天权信安", "misc_unknown", "sqlmap", "x28", "zip", "Boneh-Durfee", "RSA"]
difficulty: medium
source: "https://www.ctfiot.com/151842.html"
tools: ["Python", "sqlmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年国家基地"楚慧杯"网络安全实践能力竞赛初赛 WriteUp

> 赛事：楚慧杯 2023 2023 | 方向：misc | 难度：medium | 工具：Python、sqlmap

## 一句话总结

楚慧杯初赛：哈希扩展+sqlmap+栈溢出 0x28+TEA+zip 套娃+Boneh-Durfee 大 e RSA。

## 攻击链

1. WEB: 哈希扩展攻击伪造 password123 + 文件名 SQL 注入 + sqlmap 一把梭
2. PWN ez_base: shift+f12 找 flag.txt 字符串 + 0x28 字节溢出 + 0x404911 跳转后门
3. RE Babyre: 32 轮 TEA 加密 + delta=0x9E3779B9 + 4 个 key
4. MISC ez_zip: 压缩包套娃，Python 脚本循环解压
5. 8 位二进制 → 字符串 → DASCTF flag
6. CRYPTO so-large-e: Boneh-Durfee LLL 攻击大 e RSA
7. 用 RSA-and-LLL-attacks 库解 d

## 关键 payload

```
pay = b"a"*0x28 + p64(0x404911)
```

## 经验教训

大 e RSA 用 Boneh-Durfee LLL 攻击；TEA delta=0x9E3779B9 + sum>>11 取 key；栈溢出字节数要逐个试。

## 标签

哈希扩展攻击、sqlmap盲注、栈溢出、TEA、zip套娃、RSA_Boneh-Durfee、天权信安

## 参考来源

- https://www.ctfiot.com/151842.html
- 原文件：2023年国家基地“楚慧杯”网络安全实践能力竞赛初赛WriteUp.full.md

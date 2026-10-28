---
title: "【竞赛】2023 Dozer 新生赛考核 wp"
category: pwn
tags: ["Dozer", "pwn", "新生赛", "srand-rand", "ret2libc", "pyzipper-AES"]
signals: ["Dozer 2023", "新生赛", "srand-rand", "ret2libc", "pyzipper-AES", "RSA-enc-dec", "01248密码", "嵌套压缩包", "rop", "Dozer", "srand", "pyzipper", "AES", "RSA"]
difficulty: medium
source: "https://www.ctfiot.com/141483.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【竞赛】2023 Dozer 新生赛考核 wp

> 赛事：Dozer 2023 | 方向：pwn | 难度：medium

## 一句话总结

2023 Dozer 新生赛考核 5 题 WP，srand 随机数预测 + ret2libc + pyzipper AES 嵌套 + RSA + 01248 密码。

## 攻击链

1. 1. srand(0x22) rand()%3 恢复 12 个随机数 /2. srand(0x2a) rand()%3 恢复 51 个随机数 /3. ret2libc payload 0x78 padding + p64(0x4007e3) + p64(0x400808) + p64(0x40073B) /4. pyzipper AES 嵌套压缩包递归解压 /5. RSA p q 给定 e=65537 解密

## 关键 payload

```
srand(0x22)  srand(0x2a)  ret addr 0x4007e3  01248 密码
```

## 经验教训

srand 种子固定可预测；ret2libc 经典栈溢出 0x78 padding；pyzipper 是 AES 加密 zip；01248 密码用 1/2/4/8 加法表示 0-9。

## 标签

新生赛、srand-rand、ret2libc、pyzipper-AES、RSA-enc-dec、01248密码、嵌套压缩包

## 参考来源

- https://www.ctfiot.com/141483.html
- 原文件：【竞赛】2023Dozer新生赛考核wp.full.md

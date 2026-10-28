---
title: "DASCTF Apr.2023"
category: web
tags: ["DASCTF", "web", "ecc-key-recover", "coppersmith", "carmichael-lll", "file-overwrite"]
signals: ["DASCTF 2023", "ecc-key-recover", "coppersmith", "carmichael-lll", "file-overwrite", "canary", "pwn-stack", "crypto_rsa", "DASCTF", "EDI", "ECC", "Carmichael", "LLL", "file"]
difficulty: medium
source: "https://www.ctfiot.com/111939.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF Apr.2023

> 赛事：DASCTF 2023 | 方向：web | 难度：medium

## 一句话总结

DASCTF 2023 4 月 EDI 战队招新+4 题：ECC 还原/Carmichael LLL/file 覆盖 pwn。

## 攻击链

1. sign1n: RSA e=0x10001 + 特制 kphi 推导
2. ECC: 3 点曲线 y²=x³+ax+b 还原参数
3. babyhash: Carmichael 数 + LLL 矩阵
4. four: 文件菜单覆盖 flag
5. canary 栈溢出
6. ret2flag

## 关键 payload

```
ECC 曲线还原 + LLL 还原 Carmichael
```

## 经验教训

当 ECC 给出 3 个点 (x, y) 满足 y²=x³+ax+b mod n，可以列两个方程解 a, b mod n。

## 标签

ecc-key-recover、coppersmith、carmichael-lll、file-overwrite、canary、pwn-stack

## 参考来源

- https://www.ctfiot.com/111939.html
- 原文件：DASCTF_Apr.2023.full.md

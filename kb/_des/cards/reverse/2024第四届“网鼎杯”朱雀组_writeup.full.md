---
title: "2024 第四届\"网鼎杯\"朱雀组 writeup（SMC XOR 0x42 + base24 + VMP 壳）"
category: reverse
tags: ["2024 第四届网鼎杯", "reverse", "Re1 SMC XOR 0x42", "idapython PatchByte", "base24 自定义码表 24 字符", "decode_base24 libnum.n2s"]
signals: ["2024 第四届网鼎杯 2024", "Re1 SMC XOR 0x42", "idapython PatchByte", "base24 自定义码表 24 字符", "decode_base24 libnum.n2s", "Re2 VMP 壳", "svchost.exe 字符串大法", "异或解密 + 注入 svchost", "断点 check 先运行再瞬间断点绕过", "reverse", "misc_unknown", "crypto_unknown", "Reverse", "SMC"]
difficulty: medium
source: "https://www.ctfiot.com/213908.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 第四届"网鼎杯"朱雀组 writeup（SMC XOR 0x42 + base24 + VMP 壳）

> 赛事：2024 第四届网鼎杯 2024 | 方向：reverse | 难度：medium

## 一句话总结

第四届网鼎杯朱雀组 Reverse 三题：SMC XOR 0x42 + base24 自定义码表解码 + VMP 壳 svchost.exe 字符串大法。

## 攻击链

1. Re1: SMC 自解密 0x600 字节 XOR 0x42，idapython PatchByte
2. Re2: VMP 加壳，字符串搜 svchost.exe + 异或解密关键函数
3. base24 码表 "4836CR7F9TXGQVWYB2JPHKDM" 24 字符，密文 4FKMKYP497G87QXHBTRJKCGM63XXCC8CDQX39TQPYFY
4. libnum.n2s 转换 + 反转 [::-1]

## 关键 payload

```
PatchByte(start+i, (Byte(start+i)+0x42)&0xff)
```

## 经验教训

SMC 自解密常见手法是 idapython PatchByte 跑一遍；base24/36 等自定义码表要把密文每个字符先查表得索引再按位权累加；VMP 壳直接字符串大法 + 异或解密关键函数最快。

## 标签

Re1 SMC XOR 0x42、idapython PatchByte、base24 自定义码表 24 字符、decode_base24 libnum.n2s、Re2 VMP 壳、svchost.exe 字符串大法、异或解密 + 注入 svchost、断点 check 先运行再瞬间断点绕过

## 参考来源

- https://www.ctfiot.com/213908.html
- 原文件：2024第四届“网鼎杯”朱雀组_writeup.full.md

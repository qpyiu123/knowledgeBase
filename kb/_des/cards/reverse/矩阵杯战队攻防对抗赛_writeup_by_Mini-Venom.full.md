---
title: "矩阵杯战队攻防对抗赛 writeup by Mini-Venom"
category: reverse
tags: ["矩阵杯", "reverse", "Python字节码反编译", "RC4加密", "generate_key random.shuffle", "encrypt key[byte]^95"]
signals: ["矩阵杯 2024", "Python字节码反编译", "RC4加密", "generate_key random.shuffle", "encrypt key[byte]^95", "base58", "矩阵杯攻防", "reverse", "Mini-Venom", "Python", "RC4", "pwn", "shellcode", "AWD"]
difficulty: medium
source: "https://www.ctfiot.com/185208.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 矩阵杯战队攻防对抗赛 writeup by Mini-Venom

> 赛事：矩阵杯 2024 | 方向：reverse | 难度：medium | 工具：Python

## 一句话总结

矩阵杯攻防赛Mini-Venom WP：Python字节码RC4+矩阵杯reverse+pwn shellcode AWD

## 攻击链

1. 字节码反编译得Python run.py→generate_key random.shuffle 256字节→encrypt key[byte]^95→解密得到flag→其他AWD部分pwn shellcode爆破跳转地址

## 关键 payload

```
run.py字节码;generate_key: random.seed+shuffle(range(256))+bytes(key);encrypt: encrypted.append(key[byte]^95);int_80=0x5dde8fe0;push_eax=0x5b597483
```

## 经验教训

Python run.py可通过dis反编译得字节码再恢复；矩阵杯攻防赛综合

## 标签

Python字节码反编译、RC4加密、generate_key random.shuffle、encrypt key[byte]^95、base58、矩阵杯攻防

## 参考来源

- https://www.ctfiot.com/185208.html
- 原文件：矩阵杯战队攻防对抗赛_writeup_by_Mini-Venom.full.md

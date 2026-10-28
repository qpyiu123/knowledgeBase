---
title: "DASCTF 2023 7月 逆向题解"
category: reverse
tags: ["DASCTF", "reverse", "controlflow-flatten", "matrix-inverse", "rsa-128bit", "tea-decrypt"]
signals: ["DASCTF 2023", "controlflow-flatten", "matrix-inverse", "rsa-128bit", "tea-decrypt", "custom-vm", "idct", "reverse", "DASCTF", "RSA", "TEA", "controlflow", "swap", "mod"]
difficulty: medium
source: "https://www.ctfiot.com/134546.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2023 7月 逆向题解

> 赛事：DASCTF 2023 | 方向：reverse | 难度：medium | 工具：Python

## 一句话总结

DASCTF 2023 7 月逆向 3 题：控制流平坦化/矩阵求逆解密/128 位 RSA+TEA 自定义 VM。

## 攻击链

1. controlflow: 数组 swap 还原
2. mod 3 + 加 i + XOR i*(i+1)
3. 减 i*i + XOR 0x401
4. webserver: 4x10 矩阵 P * Q.inv mod 251
5. TCP: 128 bit RSA p,q 已知
6. 60 字节密文解 phi 后 pow(.,phi,n)
7. TEA 32 轮 delta=0x9e3779b9
8. 12 字节指令头解析
9. seg4-7 拼装 flag

## 关键 payload

```
控制流平坦化还原 + 矩阵求逆 + RSA+TEA
```

## 经验教训

控制流平坦化的逆向要点是把"被打散的 state 序列"用 Python 数组 ops 重新串起来执行。

## 标签

controlflow-flatten、matrix-inverse、rsa-128bit、tea-decrypt、custom-vm、idct

## 参考来源

- https://www.ctfiot.com/134546.html
- 原文件：DASCTF_2023_7月_逆向题解.full.md

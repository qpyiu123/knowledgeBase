---
title: "矩阵杯 2024 战队攻防对抗赛初赛 Writeup"
category: reverse
tags: ["矩阵杯", "reverse", "packpy", "UPX", "pyinstaller", "pycdc"]
signals: ["矩阵杯 2024", "packpy", "UPX", "pyinstaller", "pycdc", "base58", "zlib", "marshal", "IDEA", "reverse", "Reverse", "wtf", "pyc", "pyd"]
difficulty: medium
source: "https://www.ctfiot.com/185241.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 矩阵杯 2024 战队攻防对抗赛初赛 Writeup

> 赛事：矩阵杯 2024 | 方向：reverse | 难度：medium | 工具：Python

## 一句话总结

矩阵杯 2024 Reverse：UPX 修复脱壳 + pycdc 反编译 wtf.pyc + IDEA 算法 pyd 逆向复用开源实现。

## 攻击链

1. 1.1 packpy: UPX 加壳修复 (.upxrecoverytool.py) + pyinstaller 解包 + pycdc 反编译
2. 内部含 base58 + zlib + marshal 编码的 scrambled_code_string
3. zlib.decompress 后是缺文件头的 pyc，补 550D0D0A 头 → wtf.pyc
4. wtf.pyc 反编译: random.seed(len(flag)) + key[byte] ^ 95 加密
5. 写 decrypt: inv_key = {x: i for i, x in enumerate(key)} 还原
6. 256 seed 全部爆破（len(flag) <= 256）
7. 1.2 ccc: Python 3.10 pyd 逆向 + IDEA 算法 mod 0x10001
8. keyExpend 52 位，8 轮加密每轮 6 步 + 最后一轮 4 步
9. 函数 sub_3BA0 是 IDEA 加密核心
10. 复用开源 IDEA 实现 razvanalex/IDEA-encryption-algorithm 还原

## 关键 payload

```
wft.pyc 头部 550D0D0A000000000000000000000000 + 加密公式 key[byte]^95
```

## 经验教训

Python 字节码保护（base58+zlib+marshal 编码 + 缺文件头）是常见混淆；IDEA 是经典 mod 65537 块密码。

## 标签

packpy、UPX、pyinstaller、pycdc、base58、zlib、marshal、IDEA、mod-65537、keyExpend、pyd、Python-3.10

## 参考来源

- https://www.ctfiot.com/185241.html
- 原文件：矩阵杯_2024_战队攻防对抗赛初赛_Writeup.full.md

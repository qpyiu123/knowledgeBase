---
title: "山石CTF 2024 招新赛/REVERSE&WEB 篇"
category: reverse
tags: ["山石CTF", "reverse", "C++ 字符变换", "循环移位", "位交换", "保留符号未脱"]
signals: ["山石CTF 2024", "C++ 字符变换", "循环移位", "位交换", "保留符号未脱", "UPX 脱壳", "字符串常量比较", "招新赛", "reverse", "main", "easycpp2", "usr_input", "rand", "rotate_count"]
difficulty: easy
source: "https://www.ctfiot.com/199581.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 山石CTF 2024 招新赛/REVERSE&WEB 篇

> 赛事：山石CTF 2024 | 方向：reverse | 难度：easy | 工具：C

## 一句话总结

C++ 保留符号无脱 → 看 main 还原 循环右移 + 位交换 加密

## 攻击链

1. easycpp2: 程序未脱符号，直接看 main 函数
2. 读入 usr_input 字符串
3. rand() % 7 + 1 得到 rotate_count
4. func1 对每字符：func1_1 循环右移 rotate_count 位，func1_2 交换第 1 位和第 rotate_count 位
5. 跟 24 字节 data 数组逐字节比较，全等输出 "Correct!
6. 解密：swap_bits 还原 + circular_left_shift 解出 ayyctf{you_get_rand_num}
7. 后续题：UPX 脱壳 (l_info corrupted) → 改用 F8 手动步过 OEP 跳板 → dump 内存
8. 字符串比较：strlen 后 FUN_401830 变换后跟 "02CD290D5ACE1A83" 比较

## 关键 payload

```
def swap_bits(byte, n): bit1 = byte & 1; bitN = (byte >> (n-1)) & 1; if bit1 != bitN: byte ^= 1; byte ^= (1 << (n-1)); return byte
```

## 经验教训

招新赛题往往不脱符号；C++ 字符变换题常见循环移位+位操作复合；UPX l_info corrupted 时手脱 F8 步过 OEP

## 标签

C++ 字符变换、循环移位、位交换、保留符号未脱、UPX 脱壳、字符串常量比较、招新赛

## 参考来源

- https://www.ctfiot.com/199581.html
- 原文件：2024年第四届山石CTF招新赛WP_REVERSE&WEB篇.full.md

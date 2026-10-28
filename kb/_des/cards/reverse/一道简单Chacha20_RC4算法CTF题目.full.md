---
title: "一道简单 Chacha20 + RC4 算法 CTF 题目"
category: reverse
tags: ["CTF练习", "reverse", "Chacha20", "RC4", "flower-instructions", "anti-debug"]
signals: ["CTF练习 2022", "Chacha20", "RC4", "flower-instructions", "anti-debug", "IDA", "srand-time-pid", "time-brute-force", "newu", "reverse", "Reverse", "x40146A", "x40146F", "srand"]
difficulty: medium
source: "https://www.ctfiot.com/89178.html"
tools: ["C", "IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一道简单 Chacha20 + RC4 算法 CTF 题目

> 赛事：CTF练习 2022 | 方向：reverse | 难度：medium | 工具：C、IDA

## 一句话总结

Reverse 32 位题：花指令 0x40146A 跳 0x40146F + Chacha20 + RC4 + srand(time^pid) 爆破。

## 攻击链

1. 32 位 VC++ 程序，无壳
2. IDA F5 反编译 main 函数：读 flag → 3 个未识别函数 → 输出 flag.enc
3. 关键: sub_401450 是 Chacha20（特征字符串 "expand 32-byte k"）
4. 花指令: 0x401468~0x40146C 红色未识别，0x40146A 强制跳转到 0x40146F
5. 去花: 0x40146E 按 D 转数据 + 0x40146F 按 C 转代码 + 0x40146A~0x40146E 改 0x90 (NOP) + 0x401450~0x401566 按 P 重定义函数
6. loc_401940 和 loc_401AA0 同样处理
7. 三个函数：Chacha20 + RC4 + PRNG seed
8. sub_401610 是 PRNG seed 生成器，srand(time(0) ^ pid)
9. RC4 key = "Encrypted!!" (12 字节)
10. Chacha20 key 由 PRNG 生成 32 字节
11. 爆破: timestamp [1662909722, 1662973302] × pid [1, 9000]
12. 判定: 解密后前 3 字符 == "fla

## 关键 payload

```
time(0) ^ pid 爆破 + ChaCha20XOR + RC4 + hexData[0:3] == "fla
```

## 经验教训

花指令去花三步走 (D 转数据 + C 转代码 + NOP 填充)；Chacha20 特征 "expand 32-byte k"；srand(time) 爆破时间窗口。

## 标签

Chacha20、RC4、flower-instructions、anti-debug、IDA、srand-time-pid、time-brute-force、newu、看雪

## 参考来源

- https://www.ctfiot.com/89178.html
- 原文件：一道简单Chacha20_RC4算法CTF题目.full.md

---
title: "SunshineCTF pwn"
category: pwn
tags: ["SunshineCTF", "pwn", "libc-srand", "prng-prediction", "format-string-leak", "elden-ring-themed"]
signals: ["SunshineCTF 2022", "libc-srand", "prng-prediction", "format-string-leak", "elden-ring-themed", "fsop", "libc-2.27", "pwn_unknown", "SunshineCTF", "Pwn", "simulator", "libc", "srand", "chess"]
difficulty: medium
source: "https://www.ctfiot.com/84746.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SunshineCTF pwn

> 赛事：SunshineCTF 2022 | 方向：pwn | 难度：medium

## 一句话总结

SunshineCTF 2022 Pwn (3 题)：simulator libc srand 预测 + chess ANSI color PIE 泄漏 + Elden Ring 主题题。

## 攻击链

1. simulator 22000: 团队名 20 字节后 4 字节 seed
2. libc.srand(seed) + libc.rand()%i+1 预测后续
3. i=10,100,1000...999999999
4. 22001 (chess): payload=''r''+''8''*2+''r''*15+''r''*0x40+''b--''+str(4)+p8(0xc)+str(3000000000000)
5. 调 menu(3) 触发 print ANSI color (escape \x1B[30;...m) 泄露栈地址
6. color t + char_list.index 拼出 ans (PIE base + offset)
7. getflag = ans + 0x1349
8. 改 menu(1337) 输入 getflag
9. 22003 (Elden): 0x20 名字 + 0x10 taunt 写 got[''free''] 任意地址
10. 触发 Mergot dropped 拿到 libc
11. 第二次 NG+ p16(1)*8 + p64(freehook-8)*30 堆溢出
12. 写 /bin/sh + system → free 时触发
13. magic 22003 (MTG): menu(2) load(offset, ''aaa '', 1, puts_got, 0)
14. menu(4) show 拿 libc，menu(5) one_gadget 0xe3b34

## 关键 payload

```
libc.rand() % i + 1  # i = 10 * 10^n
```

## 经验教训

libc.srand 接受 4 字节 seed，team name 缓冲区紧接其后即可泄 seed；Elden 风格题的关键是找到 got 写入路径。

## 标签

libc-srand、prng-prediction、format-string-leak、elden-ring-themed、fsop、libc-2.27

## 参考来源

- https://www.ctfiot.com/84746.html
- 原文件：SunshineCTF_pwn.full.md

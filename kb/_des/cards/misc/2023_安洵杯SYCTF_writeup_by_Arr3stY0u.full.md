---
title: "2023 安洵杯 SYCTF WriteUp by Arr3stY0u"
category: misc
tags: ["安洵杯 SYCTF 2023", "misc", "数独游戏", "pwntools", "telnetlib", "贪吃蛇"]
signals: ["安洵杯 SYCTF 2023 2023", "数独游戏", "pwntools", "telnetlib", "贪吃蛇", "ARC4", "IDA", "claripy符号执行", "printfFSOP", "misc_unknown", "FSOP", "RSA-Coppersmith", "Sudoku", "WASD"]
difficulty: medium
source: "https://www.ctfiot.com/120089.html"
tools: ["IDA", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 安洵杯 SYCTF WriteUp by Arr3stY0u

> 赛事：安洵杯 SYCTF 2023 2023 | 方向：misc | 难度：medium | 工具：IDA、pwntools

## 一句话总结

综合 9 题：数独贪吃蛇符号执行 FSOP RSA-Coppersmith 全面覆盖。

## 攻击链

1. Sudoku 数独游戏用 pwntools 连远程 + 回溯算法 5 秒内解 9x9
2. telnetlib 收数独 + 算解 + WASD 模拟键盘操作提交
3. librosa 音频 2*audio1 - audio2 = 还原信号
4. ez_cpp3 用 exitcode 字符爆破每一位 flag
5. IDA ida_bytes.get_dword 读 6 个 10x10 地图找跳关路径
6. ARC4 + srand(0x94307F97) + 361 步贪吃蛇 RC4 加密
7. claripy BVS 符号执行 enc1/enc2/enc3 还原 flag
8. fin/mul 数组除法 + XOR + 半字节交换还原 flag
9. printf $p 泄漏 heap/libc/stack 配合 _IO_wfile_jumps 劫持 FSOP
10. libc 2.35 House of Apple 2 fake io + setcontext+61 ORW
11. RSA p-q 已知 256-bit 用连分数 + is_prime 验证分解
12. Coppersmith + m^p*Q*R 同余分解 pqr 三素数

## 关键 payload

```
SYC{I_h0pE_you_cAn_FInd_d4eam}
```

## 经验教训

数独用回溯；贪吃蛇 RC4 用 srand+ARC4；claripy BVS 做符号执行；libc2.35 House of Apple 2 是 IO 攻击标配。

## 标签

数独游戏、pwntools、telnetlib、贪吃蛇、ARC4、IDA、claripy符号执行、printfFSOP、House of Apple、RSA

## 参考来源

- https://www.ctfiot.com/120089.html
- 原文件：2023_安洵杯SYCTF_writeup_by_Arr3stY0u.full.md

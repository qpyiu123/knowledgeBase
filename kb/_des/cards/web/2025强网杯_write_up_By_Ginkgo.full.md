---
title: "2025 强网杯 write up By Ginkgo"
category: web
tags: ["强网杯", "web", "Connection注入", "X-User", "The_Interrogation_Room", "PoW暴力"]
signals: ["强网杯 2025", "Connection注入", "X-User", "The_Interrogation_Room", "PoW暴力", "汉明码d=5", "校验矩阵P", "GCD攻击", "AES-CBC", "web_unknown", "Web", "Connection", "Crypto", "GCD"]
difficulty: hard
source: "https://www.ctfiot.com/275226.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 强网杯 write up By Ginkgo

> 赛事：强网杯 2025 | 方向：web | 难度：hard | 工具：Java

## 一句话总结

强网杯 7 大题型混合集 — Web Connection 注入 + Crypto GCD/AES + MT19937 LLL + Pwn printf+House of XXX + Reverse MMX 编码 + ptrace VM 调度器。

## 攻击链

1. Web 题用 Connection: close,X-User 头部注入让服务端把 X-User 当 hop-by-hop
2. Java ProcessBuilder RCE 经 out0.setStringValue 弹结果
3. The_Interrogation_Room 25 轮，每轮 17 问（8位+9校验），暴力 4 位 PoW 后用汉明码 d=5 解码
4. Crypto 用 gcd(c,N) 拿 p,q 走 RSA-3 + AES-CBC(iv, key=long_to_bytes(c^d mod N)[:16])
5. MT19937 用 LLL 矩阵 (624 单 bit 状态) 还原 624*32 bit state
6. Pwn printf %hn 写 0x404090 改函数指针 + 二次 fmt 任意读
7. House of XXX 路径: 改 _IO_2_1_stdout_ 头 + setcontext+61 假 IO 触发 /bin/sh ORW (open/read/write flag)
8. Reverse: butterfly 二进制 MMX 编码 — XOR key8 → 16-bit 字内 swap → 64-bit ROL1 → 逐字节加 key8；解码逆向
9. Ptrace VM 调试器: int3→PEEKTEXT→int3_check→handler dispatch (RET/CALL/PUSH/JMP)

## 关键 payload

```
Connection: close,X-User / 汉明码 d=5 校验矩阵 P / MT19937 LLL 矩阵爆破 / _IO_wfile_jumps+setcontext+61 假 IO 链 / MMX 编码逆向 (XOR→swap→ROL1→add) / ptrace int3 VM 调度
```

## 经验教训

汉明码 d=5 校验矩阵 P 选满秩行可解码 2 个错；MT19937 单 bit 状态基底可建 GF(2) 上 LLL 还原；setcontext+61 配合 _IO_wfile_jumps-0x10 是 ORW RCE 经典链；MMX 编码是字节级流水线可完全逆向；ptrace int3 调度是 anti-RE 的 VM 形态。

## 标签

Connection注入、X-User、The_Interrogation_Room、PoW暴力、汉明码d=5、校验矩阵P、GCD攻击、AES-CBC、MT19937-LLL、printf格式化、_IO_wfile_jumps、setcontext+61、ptrace-VM调试器、XXTEA、MMX编码

## 参考来源

- https://www.ctfiot.com/275226.html
- 原文件：2025强网杯_write_up_By_Ginkgo.full.md

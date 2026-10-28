---
title: "CTF 逆向：基础 VM 的三大解法剖析"
category: reverse
tags: ["CTF Reverse", "reverse", "VM字节码", "opcode 0x01/0x04/0x05 add/sub/xor", "target+value 操作数", "IDA get_wide_byte 提取"]
signals: ["CTF Reverse 2024", "VM字节码", "opcode 0x01/0x04/0x05 add/sub/xor", "target+value 操作数", "IDA get_wide_byte 提取", "z3 BitVec 8位约束", "Frida hook onEnter 计数", "encode/decode 对称", "flag_enc 32字节密文", "reverse", "CTF", "x01", "x04", "x05"]
difficulty: medium
source: "https://www.ctfiot.com/235951.html"
tools: ["IDA", "Python", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 逆向：基础 VM 的三大解法剖析

> 赛事：CTF Reverse 2024 | 方向：reverse | 难度：medium | 工具：IDA、Python、Z3

## 一句话总结

CTF VM 基础 — VM 字节码 0x01/0x04/0x05 (add/sub/xor) + IDA get_wide_byte 提取 + z3 BitVec 8 位约束 + deopcode 倒序遍历 + Frida hook onEnter 计数。

## 攻击链

1. VM 字节码: opcode 0x01 加 / 0x04 减 / 0x05 异或
2. 操作数: (target, value) - flag[target] += value / -= value / ^= value
3. 解法 1: IDA Python idc.get_wide_byte(start+i) 提取 0x7A31D0 起 16*25 字节
4. 解法 2: deopcode 倒序遍历 (3字节一组) 还原 flag
5. 解法 3: z3 BitVec 8位 + solver 约束每字节 == flag_enc
6. 解法 4: Frida hook vm.exe + 0x197F onEnter 计数, send(number) 到 Python
7. flag_enc = [0x65, 0xE2, ..., 0xFD] 32 字节

## 关键 payload

```
VM opcode 0x01/0x04/0x05 / (target, value) 操作 / IDA get_wide_byte / z3 BitVec 8位 / deopcode 倒序 / Frida Interceptor.attach onEnter
```

## 经验教训

VM 逆向 3 大解法:① IDA 提取 opcode + 解释执行 / ② 倒序遍历反推 (因为加减异或操作可逆) / ③ z3 符号执行约束求解;VM 字节码通常 3 字节一组 (op, target, value)。

## 标签

VM字节码、opcode 0x01/0x04/0x05 add/sub/xor、target+value 操作数、IDA get_wide_byte 提取、z3 BitVec 8位约束、Frida hook onEnter 计数、encode/decode 对称、flag_enc 32字节密文

## 参考来源

- https://www.ctfiot.com/235951.html
- 原文件：CTF_逆向：基础_VM_的三大解法剖析.full.md

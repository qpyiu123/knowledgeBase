---
title: "UIUCTF 2023 Writeup"
category: reverse
tags: ["UIUCTF", "reverse", "custom-vm", "vmwhere", "stack-vm", "byte-swap-reverse"]
signals: ["UIUCTF 2023", "custom-vm", "vmwhere", "stack-vm", "byte-swap-reverse", "xorshift64", "gdb-scripting", "sfcta", "reverse", "UIUCTF", "REVERSE", "TOP", "key", "XOR"]
difficulty: medium
source: "https://www.ctfiot.com/123684.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UIUCTF 2023 Writeup

> 赛事：UIUCTF 2023 | 方向：reverse | 难度：medium | 工具：Python

## 一句话总结

UIUCTF 2023 vmwhere 2 题：自定义字节码 VM + REVERSE TOP N 反转 + 24/47 字节 key 链式 XOR。

## 攻击链

1. vmwhere1: 自定义 VM，22 个 opcode (ADD/SUB/AND/OR/XOR/SHL/SHR/READ/PUTCHAR/PUSH/JNEG/JZ/JMP/POP/DUP/REVERSE/SPLIT_BIT/POP_BITS/CALL/UNKNOWN/DEBUG)
2. opcode 0xa PUSH imm, 0x8 READ flag byte
3. 0x10 REVERSE TOP n 反转栈顶 n 字节
4. 0x11 SPLIT BYTE TO 8 BITS, 0x12 POP 8 重组字节
5. 24 字节 key XOR 链式: a = k ^ key[i+1]; flag[i] = (a>>4)^a
6. key[::-1] 模式找 pattern `\x05\x0f\x0a` 后字节
7. ciuctf{ar3_y0u_4_r3al_vm_wh3r3_(gpt_g3n3r4t3d_th1s_f14g)}
8. vmwhere2: 更复杂栈机 + 47 字节 key
9. 16 进制字符串 hash ('u', 'i', 'u', 'c', 't', 'f', '{') 调 mini-VM
10. 每字节 x 计算 SFCTA: result = 0; for bit in 7..0: if (x>>i)&1: result = (result+1)*3; else: result = result*3
11. 47 个 key 字符通过 table 反查
12. 输入 flag 任意字节返回 PUTCHAR 验证
13. gdb python gdb.parse_and_eval("$al") 单字符爆破

## 关键 payload

```
(a>>4) ^ a  # flag 字符链式 XOR
```

## 经验教训

自研 VM 逆向时先用 Python 写 interpreter 复现 opcode，再分析 flag 校验逻辑。

## 标签

custom-vm、vmwhere、stack-vm、byte-swap-reverse、xorshift64、gdb-scripting、sfcta

## 参考来源

- https://www.ctfiot.com/123684.html
- 原文件：UIUCTF_2023_Writeup.full.md

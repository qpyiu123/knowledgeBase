---
title: "解析2025强网拟态HyperJump"
category: reverse
tags: ["强网拟态 2025 HyperJump", "reverse", "custom-vm", "password-verify", "char-by-char", "r15-index"]
signals: ["强网拟态 2025 HyperJump 2025", "custom-vm", "password-verify", "char-by-char", "r15-index", "ROP-style-attack", "brute-force", "O-n-m-complexity", "SSE-instructions", "reverse", "HyperJump", "XOR", "ROL", "ROR"]
difficulty: hard
source: "https://www.ctfiot.com/276936.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态HyperJump

> 赛事：强网拟态 2025 HyperJump 2025 | 方向：reverse | 难度：hard | 工具：ROP

## 一句话总结

强网拟态2025 HyperJump自定义VM口令验证,24字符逐位+查找表+XOR/ROL/ROR+SSE指令+patch返回码为r15索引(3字节patch替代5字节mov eax, 0x1)+贪心爆破。

## 攻击链

1. 自定义VM程序,口令验证机制
2. 题目提示:"最复杂的迷宫也有它的规律
3. 64位ELF+PIE+stripped
4. 反反调试:修改ptrace返回值/Patch掉反调试代码
5. 关键特征:查找表访问+XOR/ROL/ROR位运算+SSE指令(movd/punpckldq)
6. 最终比较:计算结果与0x5420+r15处预期值比较
7. r15:验证到第几个字符的索引
8. 24字符逐位验证,某字符错误立即返回
9. 攻击:patch程序,让返回码=r15当前索引值
10. mov eax, 0x1" (5字节:b8 01 00 00 00) → "mov eax, r15d" (3字节:44 89 f8) + 2字节NOP
11. 枚举每位置所有可能字符(0-9 a-z A-Z符号),观察返回码
12. 返回码最大者=该位置正确字符
13. 复杂度:O(n*m)=24*95=2280次

## 关键 payload

```
mov eax, r15d (3字节patch)
```

## 经验教训

自定义VM口令验证的爆破关键:让程序返回"已验证字符数"作为侧信道;r15作为索引寄存器的patch技术(短指令+NOP)是密码学CTF常用技巧。

## 标签

custom-vm、password-verify、char-by-char、r15-index、ROP-style-attack、brute-force、O-n-m-complexity、SSE-instructions、movd、punpckldq、PIE-stripped

## 参考来源

- https://www.ctfiot.com/276936.html
- 原文件：解析2025强网拟态HyperJump.full.md

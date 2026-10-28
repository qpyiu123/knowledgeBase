---
title: "从零开始的工控固件逆向之旅 – VxWorks密码哈希破解实战"
category: crypto
tags: ["VxWorks 密码哈希 CTF", "crypto", "VxWorks", "PowerPC", "loginDefaultEncrypt", "魔数乘法"]
signals: ["VxWorks 密码哈希 CTF 2024", "VxWorks", "PowerPC", "loginDefaultEncrypt", "魔数乘法", "字符变换", "碰撞攻击", "施耐德Quantum", "弱哈希", "crypto_oracle", "FLAG", "key", "bin", "extracted"]
difficulty: medium
source: "https://www.ctfiot.com/283309.html"
tools: ["C", "IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从零开始的工控固件逆向之旅 – VxWorks密码哈希破解实战

> 赛事：VxWorks 密码哈希 CTF 2024 | 方向：crypto | 难度：medium | 工具：C、IDA

## 一句话总结

VxWorks loginDefaultEncrypt 加权求和+魔数+32 位掩码导致大量碰撞，FLAG+4 字符 0.07 秒爆破。

## 攻击链

1. key.bin 973KB 固件 + extracted 4.6MB → VxWorks 6.40 RTOS PowerPC 施耐德 Quantum PLC
2. file/hexdump 提取元数据 (140-NOE-771-01 设备型号)
3. strings 搜 loginDefaultEncrypt @ 0x22F124
4. IDA Pro 反编译 PowerPC 汇编还原 C 算法
5. 加权求和: passwdInt += ASCII(char[i]) * (i+2) ^ (i+1)
6. 乘魔数 31695317 (0x1E3A1D5) & 0xFFFFFFFF 掩码
7. 字符变换: <''3''+33 / <''7''+47 / <''9''+65
8. 字典攻击 + 智能暴力破解 (FLAG+4字符, A-Z+0-9 36^4=1,679,616)
9. 0.07 秒 / 403,259 次/秒 找到 FLAGAWYZ
10. 32 位掩码丢弃高 5 位 → 434 个碰撞密码

## 关键 payload

```
vx_hash(FLAGAWYZ) = cQwwddSRxS + 32 位掩码碰撞 434 个
```

## 经验教训

VxWorks CVE-2010-2965 弱密码哈希无盐值 + 32 位掩码 (丢失 5 位) = 大量碰撞；防御要用 bcrypt/Argon2 + 随机盐值 + 多迭代 + 2FA。

## 标签

VxWorks、PowerPC、loginDefaultEncrypt、魔数乘法、字符变换、碰撞攻击、施耐德Quantum、弱哈希

## 参考来源

- https://www.ctfiot.com/283309.html
- 原文件：从零开始的工控固件逆向之旅_–_VxWorks密码哈希破解实战.full.md

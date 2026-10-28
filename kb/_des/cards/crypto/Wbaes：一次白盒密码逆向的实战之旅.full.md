---
title: "Wbaes：一次白盒密码逆向的实战之旅 (WHCTF 2017)"
category: crypto
tags: ["WHCTF 2017 (Wani Hack)", "crypto", "white_box_aes", "movfuscation", "dfa_differential_fault_analysis", "deadpool"]
signals: ["WHCTF 2017 (Wani Hack) 2017", "white_box_aes", "movfuscation", "dfa_differential_fault_analysis", "deadpool", "phoenixaes", "look_up_table", "sigaction_anti_debug", "t_box_aes", "block_cipher", "WHCTF", "Wbaes", "MOV", "AES"]
difficulty: hard
source: "https://www.ctfiot.com/282908.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Wbaes：一次白盒密码逆向的实战之旅 (WHCTF 2017)

> 赛事：WHCTF 2017 (Wani Hack) 2017 | 方向：crypto | 难度：hard

## 一句话总结

WHCTF 2017 Wbaes 9.3 MB MOV 混淆白盒 AES，DFA 失败后改用"已知密钥 + 文件全字节扫描可解 16 字节块"绕过白盒保护，flag: Whc7f&Fl@ppyp1g!。

## 攻击链

1. file ELF 32 位 9.3 MB stripped + sigaction 反调试 + MOV 混淆 → DFA 注入尝试全部 NoFault（编译器优化防故障）→ 提取字符串 "Here is flag{%s}" → 已知 AES 实现（白盒 T-Box）→ 测试密钥 whctf&flappypig! 试解 16 字节密文块 → 遍历全文件 9770792 字节找 16 字节连续块可打印字符 ≥12 → 命中 0x003a8162 偏移解出 Whc7f&Fl@ppyp1g! → ./Wbaes "Whc7f&Fl@ppyp1g!" 输出 flag

## 关键 payload

```
key = b'whctf&flappypig!' / ciphertext = 13cb006c2994de6da1b81ba399206290 / plaintext = Whc7f&Fl@ppyp1g! / 全文件遍历 16 字节 AES-ECB 解密筛可打印字符
```

## 经验教训

白盒 AES 攻击中"密钥已知 + 文件全字节扫描"是最直接的捷径；MOVfuscation 让 DFA 难以注入时，应该转向"字符串+猜测+文件扫描"的混合策略。

## 标签

white_box_aes、movfuscation、dfa_differential_fault_analysis、deadpool、phoenixaes、look_up_table、sigaction_anti_debug、t_box_aes、sigaction_stripped_elf、hxp_dfa

## 参考来源

- https://www.ctfiot.com/282908.html
- 原文件：Wbaes：一次白盒密码逆向的实战之旅.full.md

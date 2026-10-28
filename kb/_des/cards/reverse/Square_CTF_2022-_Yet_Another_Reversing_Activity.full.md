---
title: "Square CTF 2022: Yet Another Reversing Activity"
category: reverse
tags: ["Square CTF", "reverse", "yara-rules", "yara-vm-debug", "opcode-trace", "op_bitwise_xor"]
signals: ["Square CTF 2022", "yara-rules", "yara-vm-debug", "opcode-trace", "op_bitwise_xor", "brute-char", "reverse", "Square", "CTF", "YARA", "yara", "with-debug-verbose", "OP_PUSH_8", "BITWISE_XOR"]
difficulty: medium
source: "https://www.ctfiot.com/77789.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Square CTF 2022: Yet Another Reversing Activity

> 赛事：Square CTF 2022 | 方向：reverse | 难度：medium | 工具：C

## 一句话总结

Square CTF 2022 YARA：自编译 yara --with-debug-verbose=8 跑规则，提取 OP_PUSH_8 + BITWISE_XOR trace 还原 flag。

## 攻击链

1. yara-4.2.3 源码 ./bootstrap.sh + ./configure --with-debug-verbose=8 + make
2. 写 flag.yarc 测试规则匹配 banker pattern
3. 跑 ./yara-4.2.3/yara -C flag.yarc test.txt 触发 OP_PUSH_8
4. 提取 yr_execute_code 调试日志中所有 PUSH_8 + BITWISE_XOR 对
5. chr(95^57)='f' chr(51^95)='l' chr(248^153)='a' chr(83^52)='g' chr(248^131)='{' chr(154^247)='m
6. 写 bruteforce.sh 自动化每次取最后 3 行
7. flag{m33t_me_1n_7h3_ar3n4} 渐进输出

## 关键 payload

```
yara-4.2.3/yara -C flag.yarc test.txt 2>&1 | grep -B2 OP_BITWISE_XOR
```

## 经验教训

给开源工具加 --with-debug-verbose 选项是 CTF 题目常用的"半源码"逆向入口。

## 标签

yara-rules、yara-vm-debug、opcode-trace、op_bitwise_xor、brute-char

## 参考来源

- https://www.ctfiot.com/77789.html
- 原文件：Square_CTF_2022-_Yet_Another_Reversing_Activity.full.md

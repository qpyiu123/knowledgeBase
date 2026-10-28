---
title: "Beginner picoMini 2022 writeup"
category: misc
tags: ["picoCTF", "misc", "picoCTF Beginner", "run_s4n1ty_run", "s4n1ty_c4t", "str_xor enkidu"]
signals: ["picoCTF 2022", "picoCTF Beginner", "run_s4n1ty_run", "s4n1ty_c4t", "str_xor enkidu", "4个level", "md5 hash", "691d密码", "4ec9密码", "misc_unknown", "picoCTF", "Beginner", "picoMini", "runme"]
difficulty: easy
source: "https://www.ctfiot.com/25449.html"
tools: ["Python", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Beginner picoMini 2022 writeup

> 赛事：picoCTF 2022 | 方向：misc | 难度：easy | 工具：Python、netcat

## 一句话总结

picoCTF Beginner picoMini 2022 全 12 题 — runme + nc + convertme + code + fixme1/2 + 4 个 level (str_xor + md5 + print_flag) + serpentine + 100 候选 md5 匹配。

## 攻击链

1. runme.py: 直接 print flag{picoCTF{run_s4n1ty_run}}
2. nc saturn.picoctf.net 57688: picoCTF{s4n1ty_c4t}
3. convertme.py: 十进制 → 二进制, XOR ''enkidu'' 解密
4. code.py: picoCTF{c0d3b00k_455157_8100c7c1}
5. fixme1.py: 缩进错误
6. fixme2.py: if flag = "" 应为 ==
7. level1.py: 密码 691d → str_xor 解密
8. level2.py: chr(0x34)+chr(0x65)+chr(0x63)+chr(0x39) = "4ec9
9. md5 多轮: Joan of Arc, Clint Eastwood, grave robbers
10. serpentine: 选 b 调 print_flag
11. level3.py: 密码 1ea2
12. level4.py: 100 个候选密码 md5 匹配

## 关键 payload

```
str_xor enkidu / md5 hash / 691d 4ec9 1ea2 密码 / print_flag / 100 候选 md5 匹配
```

## 经验教训

picoCTF 入门是综合小练习合集:Python 脚本分析、密码学 (XOR/md5)、代码修复 (缩进/语法)、二进制 (print_flag 函数)。

## 标签

picoCTF Beginner、run_s4n1ty_run、s4n1ty_c4t、str_xor enkidu、4个level、md5 hash、691d密码、4ec9密码、print_flag、serpentine、fixme缩进

## 参考来源

- https://www.ctfiot.com/25449.html
- 原文件：Beginner_picoMini_2022_writeup.full.md

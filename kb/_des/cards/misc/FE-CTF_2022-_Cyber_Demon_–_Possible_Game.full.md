---
title: "FE-CTF 2022: Cyber Demon – Possible Game"
category: misc
tags: ["FE-CTF 2022", "misc", "pwn", "secret-key", "urandom", "hlt"]
signals: ["FE-CTF 2022 2022", "pwn", "secret-key", "urandom", "hlt", "dev-urandom", "file-not-found", "asm", "misc_unknown", "FE-CTF", "Possible", "Game", "secret_key", "game"]
difficulty: medium
source: "https://www.ctfiot.com/82140.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# FE-CTF 2022: Cyber Demon – Possible Game

> 赛事：FE-CTF 2022 2022 | 方向：misc | 难度：medium

## 一句话总结

FE-CTF Possible Game：secret_key缺失+urandom初始化+汇编hlt

## 攻击链

1. ./game运行需要secret_key文件
2. 缺文件→open ENOENT→exit(1)
3. echo much secret > secret_key绕过
4. 反汇编main:
5. sub_4068DD初始化off_40D0C0/D140/D040三个1024字节
6. sub_405D9B打开/dev/urandom
7. sub_404D8C/sub_405BD2读urandom
8. 汇编hlt指令触发
9. pop rdi; mov rsi,rsp; push rdi; lea rdx,[rsi+rdi*8+8]
10. mov cs:qword_40D340, rdx; call sub_4060AA; call sub_408AA1; hlt

## 关键 payload

```
echo much secret > secret_key  # 绕过文件检查
```

## 经验教训

写secret_key文件绕过文件存在性检查

## 标签

pwn、secret-key、urandom、hlt、dev-urandom、file-not-found、asm

## 参考来源

- https://www.ctfiot.com/82140.html
- 原文件：FE-CTF_2022-_Cyber_Demon_–_Possible_Game.full.md

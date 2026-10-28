---
title: "2025 磐石行动 - 线下 AWD PWN"
category: pwn
tags: ["2025 磐石行动 (线下 AWD)", "pwn", "AWD", "磐石行动", "shellcode", "cat-flag"]
signals: ["2025 磐石行动 (线下 AWD) 2025", "AWD", "磐石行动", "shellcode", "cat-flag", "Halloween", "candy", "msg", "conn", "ret2libc", "heap_exploit", "pwn_unknown", "flag", "Prank"]
difficulty: hard
source: "https://www.ctfiot.com/274233.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 磐石行动 - 线下 AWD PWN

> 赛事：2025 磐石行动 (线下 AWD) 2025 | 方向：pwn | 难度：hard

## 一句话总结

AWD 多目标攻击：4 题 30 机器脚本化攻击 + flag 自动提交

## 攻击链

1. Q1 Halloween: 输入 shellcode 触发 Prank Time → push 0 + shellcraft.cat(''/flag/flag'')
2. 白名单字符过滤 (0-9, A-Z, a-z) → 纯 shellcode 不行，需 alphanumeric shellcode 或用过滤字符巧妙组合
3. Q2 candy treat(): readint() 选 candy → ''How many?'' 输入 -6 → 整数下溢减计数器
4. Q3 msg/conn 系统: 4 选项 send/receive/history/ConnectionManager
5. send 触发 readn() malloc 0x500 → buf 0x128 后 ret2csu → leak printf → system
6. Q4 connMngr: add/free/show/edit → tcache dup + chunk overlap + free_hook 改 system
7. flag 通过 POST /api/awd/batch_flag/ 提交拿 token+pk
8. hosts 10.103.x.3-30 30 台机器多目标攻击

## 关键 payload

```
payload = shellcraft.cat('/flag/flag') + push 0 (rsp 16 字节对齐)
```

## 经验教训

AWD 模式要脚本化批量打；seccomp 时 system 不可用要 ORW；整数下溢注意负数边界

## 标签

AWD、磐石行动、shellcode、cat-flag、Halloween、candy、msg、conn、addConn-removeConn-editConn-listConn、ret2csu、seccomp、system-then-ORW、flag-submission-API、multi-target

## 参考来源

- https://www.ctfiot.com/274233.html
- 原文件：2025_磐石行动-线下AWD-PWN.full.md

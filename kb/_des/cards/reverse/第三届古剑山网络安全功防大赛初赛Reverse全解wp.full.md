---
title: "第三届古剑山网络安全功防大赛初赛Reverse全解wp"
category: reverse
tags: ["第三届古剑山网络安全功防大赛初赛", "reverse", "古剑山RE全解", "base64+rc4+0x22222222异或", "HelloWorld字节码", "VM opcodes 0x101-0x504"]
signals: ["第三届古剑山网络安全功防大赛初赛 2025", "古剑山RE全解", "base64+rc4+0x22222222异或", "HelloWorld字节码", "VM opcodes 0x101-0x504", "sys_ptrace反调试", "RC4加密", "CVE-2010-2967 VxWorks固件", "reverse", "Reverse", "easyre", "RC4", "HelloWorld", "key"]
difficulty: hard
source: "https://www.ctfiot.com/284751.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届古剑山网络安全功防大赛初赛Reverse全解wp

> 赛事：第三届古剑山网络安全功防大赛初赛 2025 | 方向：reverse | 难度：hard

## 一句话总结

古剑山初赛Reverse全解5题：easyre RC4+异或+HelloWorld字节码+VM+RC4 key is_good}+VxWorks固件

## 攻击链

1. easyre(base64+rc4+0x22222222异或)→HelloWorld(字节码v3[idx]=v28[src_idx] op=3)→veryez(VM opcodes 0x101/0x102/0x103/0x201/0x202/0x203)→babyre(sys_ptrace反调试+RC4 key="is_good}")→final(VxWorks固件+CVE-2010-2967 loginDefaultEncrypt hash)

## 关键 payload

```
easyre:异或0x90504956+0x22222222+RC4+base64;HelloWorld字节码(v3[idx]=v28[src_idx] op=3);VM opcodes 0x101 add, 0x102 and, 0x201 sub;RC4 key='is_good}';VxWorks PowerPC + loginDefaultEncrypt CVE-2010-2967
```

## 经验教训

RE题常见组合：字节码VM+字符串异或+RC4；固件逆向CVE编号对应函数

## 标签

古剑山RE全解、base64+rc4+0x22222222异或、HelloWorld字节码、VM opcodes 0x101-0x504、sys_ptrace反调试、RC4加密、CVE-2010-2967 VxWorks固件

## 参考来源

- https://www.ctfiot.com/284751.html
- 原文件：第三届古剑山网络安全功防大赛初赛Reverse全解wp.full.md

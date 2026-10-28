---
title: "第十七届全国大学生信息安全竞赛创新实践能力赛初赛 Writeup"
category: pwn
tags: ["国赛信安", "pwn", "Golang-pwn", "Go-binary", "syscall-ROP", "libc-2.23"]
signals: ["国赛信安 2024", "Golang-pwn", "Go-binary", "syscall-ROP", "libc-2.23", "top-chunk-shrink", "tcache-UAF", "__malloc_hook", "one_gadget", "pwn_unknown", "PWN", "gostack", "syscall", "ROP"]
difficulty: hard
source: "https://www.ctfiot.com/182350.html"
tools: ["Go", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第十七届全国大学生信息安全竞赛创新实践能力赛初赛 Writeup

> 赛事：国赛信安 2024 | 方向：pwn | 难度：hard | 工具：Go、ROP

## 一句话总结

国赛信安 3 题 PWN：Go gostack syscall ROP 一血 + orange_cat_diary top chunk 缩 + __malloc_hook one_gadget + ezbuf protobuf 协议。

## 攻击链

1. PWN gostack (一血): Go 二进制 + 0x208 长度判断 + 填 0x00 绕过字符串检查
2. 利用: pop_rdi=0x4a18a5 + pop_rsi=0x42138a + pop_rdx=0x4944ec + pop_rax=0x40f984 + syscall=0x4616c9
3. read(0, 0x05978D8, 0x30) → /bin/sh → execve("/bin/sh", 0, 0)
4. PWN orange_cat_diary (二血): libc-2.23 + 堆溢出 8 字节 + 改 top chunk size=0xfc1
5. 申请 0xff0 让 top 进 unsorted bin + 申请 0x68 触发残留 bk 泄 libc
6. show 泄 libc, UAF 改 __malloc_hook = one_gadget 0xf03a4
7. PWN ezbuf: protobuf 协议 (whatcon/whatidx/whatsize/whatsthis/uint32 whatsthis)
8. 函数 0 解析 / 1 add 0x30 / 3 show / 2 UAF
9. 10 次释放限制 + tcache 填充 + fastbin double free + _IO_2_1_stdout 泄 stack

## 关键 payload

```
Go syscall ROP + libc-2.23 top chunk shrink 0xfc1 + UAF __malloc_hook one_gadget + protobuf whatcon/size
```

## 经验教训

Go 二进制 syscall ROP 是大题常见套路；top chunk shrink 触发 unsorted bin 是堆风水经典。

## 标签

Golang-pwn、Go-binary、syscall-ROP、libc-2.23、top-chunk-shrink、tcache-UAF、__malloc_hook、one_gadget、protobuf、ezybuf、struct-serialization

## 参考来源

- https://www.ctfiot.com/182350.html
- 原文件：第十七届全国大学生信息安全竞赛创新实践能力赛初赛Writeup.full.md

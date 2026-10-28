---
title: "解析强网拟态aaaheap"
category: pwn
tags: ["强网拟态 aaaheap", "pwn", "arm64", "aarch64", "tcache", "safe-linking"]
signals: ["强网拟态 aaaheap 2024", "arm64", "aarch64", "tcache", "safe-linking", "libc-leak", "environ-leak", "ROP", "mprotect", "heap_exploit", "aaaheap", "ARM64", "Safe-Linking", "GOT"]
difficulty: hard
source: "https://www.ctfiot.com/276993.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析强网拟态aaaheap

> 赛事：强网拟态 aaaheap 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

强网拟态aaaheap ARM64架构下的tcache堆利用详解,涵盖Safe-Linking保护绕过(右移12位异或)+GOT泄露libc+environ泄露栈+栈分配+ROP劫持全流程。

## 攻击链

1. ARM64架构ELF aarch64,Full RELRO+NX+PIE+stripped
2. tcache 7个块LIFO,fd指针单链表
3. Safe-Linking保护:fd = (next_addr >> 12) ^ real_next(右移12位异或)
4. 泄露堆地址→算加密值→修改fd指针为目标地址
5. 分配到目标地址(控制chunk0指针)
6. 读GOT表内容→计算libc base(atoi偏移)
7. 读environ变量→定位栈地址
8. 分配到栈,写入ROP链
9. 触发执行,获得shell
10. 关键寄存器:x0-x7参数/返回值,x8 syscall,x29 FP,x30 LR
11. 内存页4KB右移12位相当于取页号

## 关键 payload

```
aarch64 ROP + 栈劫持 + environ leak
```

## 经验教训

ARM64堆利用与x86差异在寄存器约定(x0-x7参数/x8 syscall/x30 LR);Safe-Linking是glibc 2.32+的保护,需右移12位异或绕过;environ是定位栈地址的稳定向量。

## 标签

arm64、aarch64、tcache、safe-linking、libc-leak、environ-leak、ROP、mprotect、malloc-hook、page-align-shift

## 参考来源

- https://www.ctfiot.com/276993.html
- 原文件：解析强网拟态aaaheap.full.md

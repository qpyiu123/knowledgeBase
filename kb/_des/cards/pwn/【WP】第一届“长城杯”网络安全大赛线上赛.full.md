---
title: "【WP】第一届\"长城杯\"网络安全大赛线上赛"
category: pwn
tags: ["长城杯", "pwn", "custom-VM", "INFO-breakpoint-leak", "mmap-0x200000+libc-ld-offset", "page-table-64bit-low-16-bits"]
signals: ["长城杯 2021", "custom-VM", "INFO-breakpoint-leak", "mmap-0x200000+libc-ld-offset", "page-table-64bit-low-16-bits", "LW-SW-arbitrary-RW", "one_gadget", "linkmap-text-base", "ROP-via-got", "rop", "easy_vm", "PWN", "x200000", "mmap"]
difficulty: hard
source: "https://www.ctfiot.com/19019.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第一届"长城杯"网络安全大赛线上赛

> 赛事：长城杯 2021 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

第一届长城杯网络安全大赛 easy_vm 高级 PWN，自定义 VM + 64 位页表检查漏洞 + LW/SW 任意地址读写。

## 攻击链

1. VM 申请内存 > 0x200000 触发 mmap 固定偏移/INFO 断点泄 ld 基址 + libc 基址/PAGE 指令初始化页表利用 64 位低 16 位检查漏洞填 ld 基址到页表/LW/SW 通过页框基址+24 位偏移任意地址读写/LD_PAGE 把 text 段基址放入页表/改 puts got = one_gadget 触发 EXIT 收 shell

## 关键 payload

```
page_table 64 位低 16 位检查  LW/SW 任意地址读写  one_gadget
```

## 经验教训

VM 申请内存 > 0x200000 触发 mmap 与 libc/ld 固定偏移是泄地址经典方法；64 位页表项只检查低 16 位是绕过页表检查的经典漏洞；LW + SW + 页框基址 + 24 位偏移实现任意地址读。

## 标签

custom-VM、INFO-breakpoint-leak、mmap-0x200000+libc-ld-offset、page-table-64bit-low-16-bits、LW-SW-arbitrary-RW、one_gadget、linkmap-text-base、ROP-via-got

## 参考来源

- https://www.ctfiot.com/19019.html
- 原文件：【WP】第一届“长城杯”网络安全大赛线上赛.full.md

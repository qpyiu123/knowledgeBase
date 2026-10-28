---
title: "天堂之门 (WoW64) 总结及CTF分析 - ctfshow月饼杯2 EasyTea"
category: reverse
tags: ["ctfshow 月饼杯2 + 看雪论坛", "reverse", "WoW64", "Heaven's_Gate, retf, CS段寄存器, 32位调用64位, XTEA, 魔改, 反调, AntiDebug, Wow64Cpu, syscall, IDA反编译"]
signals: ["ctfshow 月饼杯2 + 看雪论坛 2024", "WoW64", "Heaven's_Gate, retf, CS段寄存器, 32位调用64位, XTEA, 魔改, 反调, AntiDebug, Wow64Cpu, syscall, IDA反编译", "reverse", "Sh4d0w", "ctfshow", "EasyTea", "XXTEA", "x33", "xEA", "jmp", "far"]
difficulty: hard
source: "https://www.ctfiot.com/208119.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 天堂之门 (WoW64) 总结及CTF分析 - ctfshow月饼杯2 EasyTea

> 赛事：ctfshow 月饼杯2 + 看雪论坛 2024 | 方向：reverse | 难度：hard

## 一句话总结

看雪Sh4d0w详解WoW64天堂之门(32位程序调64位函数)技术+ctfshow月饼杯2 EasyTea实战魔改XXTEA。

## 攻击链

1. 32位PE切天堂之门(CS=0x33) → 0xEA jmp far ptr跳到64位函数 → unk_427A50处实际为64位XXTEA加密 → IDA手动分析 + IDApython patch 64位Hello World二进制 → P创建函数得魔改XTEA → 还原解密得flag

## 关键 payload

```
CS=0x33 + 0xEA jmp far ptr + 魔改XXTEA delta=0x77B7EEBB
```

## 经验教训

WoW64下32位进程用CS=0x33/0x23切换32/64位模式,retf是关键指令;32位IDA无法反编译64位指令,需手动分析机器码+IDApython patch到64位程序还原函数;天堂之门实战多为反调反沙箱(沙箱+火绒剑都识别),但CTF主要考反静态分析;动态天堂之门只能动调手撕。

## 标签

WoW64、Heaven's_Gate, retf, CS段寄存器, 32位调用64位, XTEA, 魔改, 反调, AntiDebug, Wow64Cpu, syscall, IDA反编译

## 参考来源

- https://www.ctfiot.com/208119.html
- 原文件：天堂之门(WoW64技术)总结及CTF中的分析.full.md

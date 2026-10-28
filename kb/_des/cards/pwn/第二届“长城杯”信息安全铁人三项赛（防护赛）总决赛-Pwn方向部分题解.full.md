---
title: "第二届\"长城杯\"信息安全铁人三项赛(防护赛)总决赛-Pwn方向部分题解"
category: pwn
tags: ["长城杯信息安全铁人三项赛", "pwn", "Pwn-Heap", "libc2.31", "Protobuf", "菜单题"]
signals: ["长城杯信息安全铁人三项赛 2024", "Pwn-Heap", "libc2.31", "Protobuf", "菜单题", "free_hook覆盖", "heap_exploit", "add", "delete", "show", "libc2", "x91", "chunk", "size"]
difficulty: medium
source: "https://www.ctfiot.com/259435.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届"长城杯"信息安全铁人三项赛(防护赛)总决赛-Pwn方向部分题解

> 赛事：长城杯信息安全铁人三项赛 2024 | 方向：pwn | 难度：medium

## 一句话总结

Protobuf格式字符串解析的菜单add/delete/show题,libc2.31通过0x91 chunk size边界溢出让show泄libc,然后多次add+rm控制chunk到__free_hook写入system,rm(2)触发

## 攻击链

1. 分析sub_12FD展示函数(循环16个qword)+sub_1141指令解析(空格/冒号分隔index字符串)→识别add/delete/show菜单→大量add堆块+rm触发free→off-by-null/0x91溢出→show Data#8泄libc_base(libc-0x3ebca0)→覆盖__free_hook→system('/bin/sh')→rm(2)触发

## 关键 payload

```
pay = b':\ntitle:\nAAAAAAAAA:\nsubtitle:A' + p32(0x601)|add(b'Y'*0x120 + p64(free_hook))|add(b'/bin/sh')|add(p64(system))|rm(2)
```

## 经验教训

1) ProtobufCFieldDescriptor结构体{name,id,label,type,quantifier_offset,offset,descriptor,default_value,flags}识别二进制协议格式; 2) 0x91 size chunk边界+off-by-null可破坏下一个chunk metadata; 3) libc_base = leak - 0x3ebca0(unsorted bin fd偏移); 4) __free_hook覆盖链:多次add(0x120)→rm→add(0x120-1)→rm→add(0x120-2)→rm→add(0x120-8)+p64(free_hook)逐步缩小对齐; 5) brva 0x0144F定位关键断点

## 标签

Pwn-Heap、libc2.31、Protobuf、菜单题、free_hook覆盖

## 参考来源

- https://www.ctfiot.com/259435.html
- 原文件：第二届“长城杯”信息安全铁人三项赛（防护赛）总决赛-Pwn方向部分题解.full.md

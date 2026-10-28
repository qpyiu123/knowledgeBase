---
title: "ciscn 国赛华东南分区赛 PWN 方向 WriteUp 分享"
category: pwn
tags: ["CISCN", "pwn", "ciscn", "glibc-2.35", "safe-linking", "uaf"]
signals: ["CISCN 2023", "ciscn", "glibc-2.35", "safe-linking", "uaf", "seccomp", "vm-escape", "srop", "pwn_unknown", "CISCN", "PWN", "UAF", "Seccomp", "SVM"]
difficulty: hard
source: "https://www.ctfiot.com/125454.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ciscn 国赛华东南分区赛 PWN 方向 WriteUp 分享

> 赛事：CISCN 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

CISCN 2023 华东南分区赛 7 道 PWN 复盘，覆盖栈劫持/UAF/Seccomp/SVM 多种高阶技巧。

## 攻击链

1. 栈劫持到 bss 段二次 ROP
2. 填满 tcache 触发 unsorted bin 残留
3. UAF 读 + XOR 解密还原 libc/heap
4. double-free + tcache fd 异或
5. _IO_list_all 劫持
6. SigreturnFrame 跳到 ORW

## 关键 payload

```
glibc 2.35 safe-linking 异或 + _IO_list_all 攻击 + ORW 链
```

## 经验教训

glibc 2.35 引入的 safe-linking 异或 + _rtld_global 攻击面让 house of banana 复活；栈劫持到 bss 段做二次 ROP 是有限溢出时唯一出路。

## 标签

ciscn、glibc-2.35、safe-linking、uaf、seccomp、vm-escape、srop

## 参考来源

- https://www.ctfiot.com/125454.html
- 原文件：ciscn国赛华东南分区赛PWN方向WriteUp分享.full.md

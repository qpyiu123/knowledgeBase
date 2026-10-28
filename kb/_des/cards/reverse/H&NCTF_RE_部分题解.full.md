---
title: "H&NCTF RE 部分题解"
category: reverse
tags: ["H&NCTF", "reverse", "rev", "enigma-virtual-box", "anti-vm", "anti-av"]
signals: ["H&NCTF 2024", "rev", "enigma-virtual-box", "anti-vm", "anti-av", "shellcode-injection", "kernel32-hash", "ldr-list", "reverse", "NCTF", "RWhackA", "Enigma", "shellcode", "enigma"]
difficulty: hard
source: "https://www.ctfiot.com/183150.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# H&NCTF RE 部分题解

> 赛事：H&NCTF 2024 | 方向：reverse | 难度：hard

## 一句话总结

H&NCTF RWhackA：Enigma打包+反VM+反杀软+shellcode注入

## 攻击链

1. enigma virtual box 打包exe+多个dll
2. main函数: 在C盘用户视频目录创建副本svchsst.exe
3. 副本启动: 删除txt+原文件+继续执行
4. 实体机跑: v48=16 走主逻辑
5. 检测VMware tools/VirtualBox Guest Additions
6. 进程快照遍历LDR双向链表
7. kernel32名字hash比对
8. 杀软检测: Process Snapshot遍历
9. sub_140001320 shellcode自解密+注入exp10rer.exe
10. shellcode自修改XOR+位运算

## 关键 payload

```
sub_140001320 解密shellcode → 注入 exp10rer.exe
```

## 经验教训

Enigma Virtual Box打包需用动态调试+反VM检测绕过

## 标签

rev、enigma-virtual-box、anti-vm、anti-av、shellcode-injection、kernel32-hash、ldr-list

## 参考来源

- https://www.ctfiot.com/183150.html
- 原文件：H&NCTF_RE_部分题解.full.md

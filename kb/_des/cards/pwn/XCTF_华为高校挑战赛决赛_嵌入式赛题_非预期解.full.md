---
title: "XCTF 华为高校挑战赛决赛/嵌入式非预期解"
category: pwn
tags: ["XCTF", "pwn", "嵌入式", "LiteOS", "Hi3518", "qemu-system-arm"]
signals: ["XCTF null", "嵌入式", "LiteOS", "Hi3518", "qemu-system-arm", "migrate exec", "ARM shellcode", "syscall 0x206", "readreg", "pwn_unknown", "reverse", "migrate", "exec", "ARM"]
difficulty: hard
source: "https://www.ctfiot.com/58222.html"
tools: ["ARM", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# XCTF 华为高校挑战赛决赛/嵌入式非预期解

> 赛事：XCTF null | 方向：pwn | 难度：hard | 工具：ARM、pwntools

## 一句话总结

qemu-system-arm LiteOS 模拟器 migrate exec 注入命令 + ARM shellcode readreg 系统调用

## 攻击链

1. 题目用 qemu-system-arm -M hi3518 模拟 LiteOS（HarmonyOS 内核）
2. 拿 qemu monitor 的 migrate "exec: cmd" 注入命令
3. 直接 strings /rootfs.img | grep flag 找 flag
4. 或 migrate "exec: base64 rootfs.img" 整盘 dump
5. 非预期：通过 qemu monitor 注入 ARM shellcode (svc 0 + readreg 系统调用) 读任意内存
6. 构造 shellcode：mov r7, 0x206; adr r0, "readreg"; adr r1, cmd_str; svc 0
7. 把 shellcode patch 进 camera_app 二进制
8. 通过串口发到 qemu，触发后读 flag 字符串内存
9. 提取 hex 字符串，反转拼接得 flag

## 关键 payload

```
io.sendlineafter(''finish'', shellcode.hex())  # ARM shellcode 注入 qemu
```

## 经验教训

qemu-monitor 的 migrate "exec: cmd" 可作为嵌入式题的非预期入口；LiteOS 系统调用 0x206 是 readreg 任意内存读

## 标签

嵌入式、LiteOS、Hi3518、qemu-system-arm、migrate exec、ARM shellcode、syscall 0x206、readreg、HarmonyOS、pwntools ARM

## 参考来源

- https://www.ctfiot.com/58222.html
- 原文件：XCTF_华为高校挑战赛决赛_嵌入式赛题_非预期解.full.md

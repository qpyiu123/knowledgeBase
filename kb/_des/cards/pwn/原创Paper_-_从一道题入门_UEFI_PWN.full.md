---
title: "原创Paper | 从一道题入门 UEFI PWN"
category: pwn
tags: ["n1ctf 2022 UEFI", "pwn", "UEFI", "OVMF", "uefi-firmware-parser", "UiApp"]
signals: ["n1ctf 2022 UEFI 2022", "UEFI", "OVMF", "uefi-firmware-parser", "UiApp", "gRT", "GetVariable", "Double GetVariable", "栈溢出", "iot", "PWN", "Double", "qemu", "gdb"]
difficulty: hard
source: "https://www.ctfiot.com/72677.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 原创Paper | 从一道题入门 UEFI PWN

> 赛事：n1ctf 2022 UEFI 2022 | 方向：pwn | 难度：hard | 工具：IDA

## 一句话总结

UEFI PWN 入门：OVMF 解包 + UiApp 反编译 + Double GetVariable 栈溢出 + qemu gdb 动态调试 + 劫持 Boot Manager 拿 root。

## 攻击链

1. OVMF.fd 解包: uefi-firmware-parser -ecO ./OVMF.fd
2. 定位 UiApp: volume-0/file-9e21fd93-9c72-4c15-8c4b-e77f1db2d792/section0
3. 找关键函数: file-462caa21-.../section0.pe
4. IDA 反编译 UiApp, 还原 gRT 结构体
5. gRT->SetVariable/GetVariable 键值对操作
6. 漏洞: Double GetVariable 栈溢出
7. qemu 启动 OVMF.fd + -s -S + gdb attach
8. 内存搜索 UiApp 加载基址
9. boot_offset=0x235A, uiapp_offset=0x1e009c0
10. 泄露 UiApp 基址: 256 字节 leak + Encode 算偏移
11. 栈溢出 payload = 'a'*0x18 + p32(boot_addr)
12. add("N1CTF_KEY1", payload) + add("N1CTF_KEY2", payload)
13. 劫持控制流到 Boot Manager → root shell

## 关键 payload

```
Double GetVariable 栈溢出 + boot_offset=0x235A + p32(boot_addr) ret 劫持
```

## 经验教训

UEFI 漏洞核心在 gRT (Runtime Services) SetVariable/GetVariable; Double GetVariable 是经典模式 (GetVariable 两次读到同一内存区域, 中间内存重分配造成 UAF/溢出); 加载基址靠内存指令序列搜索定位。

## 标签

UEFI、OVMF、uefi-firmware-parser、UiApp、gRT、GetVariable、Double GetVariable、栈溢出、BIOS劫持、qemu

## 参考来源

- https://www.ctfiot.com/72677.html
- 原文件：原创Paper_-_从一道题入门_UEFI_PWN.full.md

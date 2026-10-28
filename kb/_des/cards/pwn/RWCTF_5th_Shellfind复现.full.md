---
title: "RWCTF 5th Shellfind 复现"
category: pwn
tags: ["RWCTF 5th", "pwn", "iot", "mips", "udp-service", "ipfind"]
signals: ["RWCTF 5th 2022", "iot", "mips", "udp-service", "ipfind", "base64-decode", "stack-overflow", "ret2shellcode", "qemu", "rop", "RWCTF", "Shellfind", "malta", "tap0"]
difficulty: hard
source: "https://www.ctfiot.com/94114.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RWCTF 5th Shellfind 复现

> 赛事：RWCTF 5th 2022 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

RWCTF 5th Shellfind 复现 WP：qemu malta mips 模拟器 + tap0 网络 + ipfind UDP 62720 + base64 栈溢出 + dup2 busybox sh 回连。

## 攻击链

1. 复现 RealWorld CTF 5th IoT PWN 题目 - 基于真实设备固件改编
2. 拿到 .bin 固件包解压获得完整文件系统
3. 下载官方固件 + bindiff 比对找到被修改的 ipfind 二进制
4. MIPS 大端 + 无任何保护
5. 模拟: qemu-system-mips + malta + vmlinux-3.2.0-4-4kc-malta + tap0 网络
6. 启动 chroot squashfs-root + mount /proc + 切换 /etc/rc.d/rcS
7. 启动 ipfind eth0 & 替换默认 br0 (qemu 模拟器用 eth0)
8. 漏洞点: sub_400F50 base64 decode 到栈 → 栈溢出
9. checksec: No RELRO + No canary + NX disabled + No PIE + Has RWX
10. mipsrop 无输出 → 自构 ROP
11. 利用 UDP 协议: FIVI + cmd=2 (Shell) + base64(username:password) 触发
12. sub_4013F4 校验 + sub_400F50 触发 base64 decode 栈溢出
13. s_log_nothing 泄露栈地址 → 改 GOT → ret2shellcode
14. dup2 stdin/stdout/stderr + execve /bin/busybox sh
15. 利用 IPFIND UDP fd 复用作为 RCE

## 关键 payload

```
base64(b'a'*padding + rop + shellcode)
```

## 经验教训

qemu-system-mips + tap0 桥接 + chroot 启动是 IoT 复现基础；ipfind 启动时指定 eth0 (qemu 模拟器) 而非 br0 (真实设备) 才能 gdbserver 调试；base64 decode 写入栈是经典溢出模式。

## 标签

iot、mips、udp-service、ipfind、base64-decode、stack-overflow、ret2shellcode、qemu、firmadyne、pwn

## 参考来源

- https://www.ctfiot.com/94114.html
- 原文件：RWCTF_5th_Shellfind复现.full.md

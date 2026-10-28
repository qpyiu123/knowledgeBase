---
title: "2022 USTC Hackergame WriteUp 0x03 (Linux VM pwn)"
category: pwn
tags: ["2022 USTC Hackergame", "pwn", "USTC-Hackergame", "iPXE", "SeaBIOS", "qemu-VM"]
signals: ["2022 USTC Hackergame 2022", "USTC-Hackergame", "iPXE", "SeaBIOS", "qemu-VM", "busybox", "init", "suid-setuid", "flag2-uid-1337", "pwn_unknown", "auth_bypass", "reverse", "web_unknown", "USTC"]
difficulty: hard
source: "https://www.ctfiot.com/71369.html"
tools: ["GDB", "ROPgadget", "netcat", "objdump", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 USTC Hackergame WriteUp 0x03 (Linux VM pwn)

> 赛事：2022 USTC Hackergame 2022 | 方向：pwn | 难度：hard | 工具：GDB、ROPgadget、netcat、objdump、x86/x64

## 一句话总结

USTC Hackergame 真机 Linux VM pwn：iPXE 启动 → busybox shell → SUID 提权链

## 攻击链

1. nc 202.38.93.111 10338 → iPXE → SeaBIOS → Linux 5.19.9 启动
2. /challenge 是 setuid 0 → 普通用户跑
3. cat /flag2 权限 -r-------- 1 1337 1337 → 只有 uid 1337 能读
4. env 收集：kernel cmdline / uname / mount / df / ps
5. /tmp 共享可写（tmpfs）
6. chall 有 SUID 标志 + 路径 + 大小 20352 → static-linked
7. pwndbg / ROPgadget / objdump 分析 chall 找漏洞
8. exploit: 提权到 uid 1337 读 flag2 / 继续提权到 root 读 /flag

## 关键 payload

```
/challenge setuid 0 + uid 1337 owner of /flag2
```

## 经验教训

iPXE + SeaBIOS 模拟远程固件启动是 CTF 高端考法；多层提权是 Linux pwn 实战

## 标签

USTC-Hackergame、iPXE、SeaBIOS、qemu-VM、busybox、init、suid-setuid、flag2-uid-1337、kernel-pwn、qemu、x86、container-escape

## 参考来源

- https://www.ctfiot.com/71369.html
- 原文件：2022_USTC_Hackergame_WriteUp_0x03.full.md

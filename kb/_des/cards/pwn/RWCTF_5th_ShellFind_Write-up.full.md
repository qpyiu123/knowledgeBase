---
title: "RWCTF 5th ShellFind Write-up"
category: pwn
tags: ["RWCTF 5th", "pwn", "iot", "mips", "udp-service", "ipfind"]
signals: ["RWCTF 5th 2022", "iot", "mips", "udp-service", "ipfind", "base64-decode", "stack-overflow", "ret2shellcode", "qemu", "rop", "RWCTF", "ShellFind", "IoT", "UDP"]
difficulty: hard
source: "https://www.ctfiot.com/91517.html"
tools: ["ROP", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RWCTF 5th ShellFind Write-up

> 赛事：RWCTF 5th 2022 | 方向：pwn | 难度：hard | 工具：ROP、netcat

## 一句话总结

RWCTF 5th ShellFind 长亭科技官方 WP：IoT 固件模拟 + UDP ipfind base64 解码栈溢出 + mips 无防护 ROP 改 GOT + dup2 busybox sh 回连。

## 攻击链

1. 出题背景：IoT 安全 (Pink 僵尸网络) - 模拟 IoT 设备调试接口
2. 题目类型 PWN (Normal) - Hello Hacker 提示 only one UDP service to shell
3. FIRMADYNE 仿真 + FIRMae 自动化 + TAP 虚拟网络
4. netstat 发现 ddp 62976 + ipfind 62720 + tcp 31338 + http 80
5. ipfind 监听 UDP 0xF580 (62720) - 目标服务
6. UDP 协议 27 字节：4 magic "FIVI" + 4 pad + 1 type=10 + 2 cmd + ...
7. sub_4013F4 进入 sub_400F50 base64 decode 到栈上 → 栈溢出
8. checksec: No RELRO + No canary + NX disabled + No PIE + Has RWX
9. qemu 中开启 ASLR, mipsrop 无输出需自构造
10. 漏洞点: s_log_nothing addiu $v0,$sp,0x10+arg_4 → 栈地址 leak
11. 改 GOT: 0x00400c9c lw $gp, 0x10($sp) ; lw $ra, 0x1c($sp) ; jr $ra ; addiu $sp, $sp, 0x20
12. 单命令受限 (几百字符)，busybox nc 被改 nx 不能反弹 shell
13. 多次利用: rm /var/run/ipfind-br0.pid; ipfind br0 & 重启服务
14. ret2shellcode: dup2 → busybox sh → connect back to attacker
15. 利用 dup2(2) + execve /bin/busybox sh sys 0xfdf/0xfab
16. 出题总结: 固件模拟 (QEMU+FIRMADYNE) + 网络服务发现 + 漏洞挖掘 + 利用

## 关键 payload

```
rop_chain = 0x3C1C0042 (lui $gp) + 0x279CB030 (addiu $gp) + lw $v0 server_sockfd + lw $a0 (fd) + dup2 loop + execve /bin/busybox sh
```

## 经验教训

IoT 攻防人员需掌握 FIRMADYNE/FIRMae 自动化仿真；mips 自构 ROP 关键是找 jr $ra + lw $gp gadget；UDP 服务复用 fd 是反连 RCE 唯一路径；s_log_nothing 类函数常常会泄露栈地址。

## 标签

iot、mips、udp-service、ipfind、base64-decode、stack-overflow、ret2shellcode、qemu、firmadyne、pwn、f5-bigip

## 参考来源

- https://www.ctfiot.com/91517.html
- 原文件：RWCTF_5th_ShellFind_Write-up.full.md

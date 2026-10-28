---
title: "RWCTF 5th ShellFind 复现"
category: pwn
tags: ["RWCTF 5th", "pwn", "iot", "mips", "udp-service", "ipfind"]
signals: ["RWCTF 5th 2023", "iot", "mips", "udp-service", "ipfind", "base64-decode", "stack-overflow", "ret2shellcode", "qemu", "rop", "RWCTF", "IoT", "ShellFind", "UDP"]
difficulty: hard
source: "https://www.ctfiot.com/151160.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RWCTF 5th ShellFind 复现

> 赛事：RWCTF 5th 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

RWCTF 5th IoT ShellFind：UDP ipfind 服务 + base64 解码栈溢出 + mips 无 canary ROP 改 GOT + 重启服务复用 shellcode dup2 + busybox sh 回连。

## 攻击链

1. RWCTF 5th IoT PWN 题目 - Docker 1arry/shellfind UDP 4444
2. 模拟 D-Link DIR-815 等 IoT 设备固件 FIRMADYNE
3. netstat 发现 ipfind 监听 UDP 62720 (0xF580)
4. 协议头 FIVI + 字节序转换 + 协议类型 (1=Discovery / 2=Shell)
5. 第一个请求 Discovery 拿 MAC 地址 (sub_40172C)
6. 第二个请求 Shell 携带 base64 username+password 触发 sub_4013F4
7. sub_400F50: Base64decs 解码到栈 v7[256] 触发栈溢出
8. checksec: No RELRO + No canary + NX disabled + No PIE + RWX 段
9. ASLR 开启但 mipsrop 无效需自构造 ROP
10. 改 GOT: $sp 出栈 + $v0 任意地址写 + jr $ra gadget
11. 重启漏洞服务 rm /var/run/ipfind-br0.pid; ipfind br0 &
12. ret2shellcode: dup2 stdin/stdout/stderr → busybox sh → sys_connect 回连
13. 利用 dup2(2) + execve /bin/busybox sh 复用 UDP fd
14. 完整 shellcode: lui $gp + la $v0 server_sockfd + lw $a0 + dup2 sys 0xfdf + execve 0xfab

## 关键 payload

```
data=b'FIVI\x00\x00\x00\x00\x0a\x02\x00\x00\x00\x00\x00\x00\xff'*6 + b64('admin:0\r\n'+padding+rop) + b64('admin:'+shellcode)
```

## 经验教训

IoT 固件模拟 (QEMU + FIRMADYNE) 是入门技能；mipsrop 无效时需手工寻找 jr $ra + lw $gp gadget；UDP 服务复用 fd 是内网出网的 RCE 入口；ASLR 开启但 mips32 base 12-bit 滑动可爆破。

## 标签

iot、mips、udp-service、ipfind、base64-decode、stack-overflow、ret2shellcode、qemu、firmadyne、ghidra、pwn

## 参考来源

- https://www.ctfiot.com/151160.html
- 原文件：RWCTF5TH_shellfind.full.md

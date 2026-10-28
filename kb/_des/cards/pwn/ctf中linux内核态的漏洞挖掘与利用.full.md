---
title: "ctf 中 linux 内核态的漏洞挖掘与利用"
category: pwn
tags: ["ctf-share", "pwn", "kernel-pwn", "stack-overflow", "smep-bypass", "smap-bypass"]
signals: ["ctf-share 2018", "kernel-pwn", "stack-overflow", "smep-bypass", "smap-bypass", "kallsyms-leak", "rop", "iretq", "kernel-fs", "pwn_unknown", "V-lab", "CTF", "core", "zerofs"]
difficulty: hard
source: "https://www.ctfiot.com/57334.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ctf 中 linux 内核态的漏洞挖掘与利用

> 赛事：ctf-share 2018 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

V-lab 实验室 CTF 内核漏洞挖掘教程，覆盖 core.ko 栈溢出 + zerofs 内核文件系统越界读写两套思路。

## 攻击链

1. core.ko ioctl 0x6677889C 设置 off 全局变量
2. ioctl 0x6677889B 触发 core_read 泄 canary + ret_addr
3. 写入 0x100 字节到 name
4. ioctl 0x6677889A 传 -0xa000...8 绕过有符号长度检查
5. core_copy_func 栈溢出 0x58 字节
6. 内核 shellcode: commit_creds(prepare_kernel_cred(0))
7. SMEP/SMAP 开启时改 ROP 链
8. swapgs + iretq 返回用户态
9. zerofs 内核文件系统 OOB 读 cred

## 关键 payload

```
内核栈溢出 ROP + kallsyms 提权函数
```

## 经验教训

内核栈溢出要点：先泄 canary/ret_addr，再 ROP 走 prepare_kernel_cred(0) → commit_creds 提权，最后 iretq 返用户态；SMEP/SMAP 开启必须 ROP。

## 标签

kernel-pwn、stack-overflow、smep-bypass、smap-bypass、kallsyms-leak、rop、iretq、kernel-fs、randstruct

## 参考来源

- https://www.ctfiot.com/57334.html
- 原文件：ctf中linux内核态的漏洞挖掘与利用.full.md

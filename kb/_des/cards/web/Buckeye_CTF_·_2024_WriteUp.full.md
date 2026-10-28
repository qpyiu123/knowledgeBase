---
title: "Buckeye CTF · 2024 WriteUp (狼组版)"
category: web
tags: ["BuckeyeCTF", "web", "pwnoh.io", "uuid文件存储", "目录穿越flag.txt", "runway0/1/2栈溢出"]
signals: ["BuckeyeCTF 2024", "pwnoh.io", "uuid文件存储", "目录穿越flag.txt", "runway0/1/2栈溢出", "calc canary leak", "color regex回显", "L33t", "30+题多方向", "web_unknown", "BuckeyeCTF", "Web", "SSFS", "uuid"]
difficulty: medium
source: "https://www.ctfiot.com/207473.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Buckeye CTF · 2024 WriteUp (狼组版)

> 赛事：BuckeyeCTF 2024 | 方向：web | 难度：medium

## 一句话总结

BuckeyeCTF 2024 狼组复盘 — Web SSFS uuid 目录穿越 + Pwn runway0/1/2 栈溢出 + calc canary 泄 + color 字符串回显 + 4 个 flag 涵盖 web/pwn/reverse。

## 攻击链

1. Web fu: SSFS 文件服务, uuid 存储, 目录穿越读 flag.txt → bctf{4lw4y5_35c4p3_ur_p4th5}
2. Pwn runway0: sh 一行 exec 1>&2 + cat flag.txt
3. Pwn runway1: 0x4c padding + p32(win) 覆盖返回
4. Pwn color: 字符串回显, 输入含 "ctf{1_d0n7_c4r3_571ll_4_m1d_c010r}!?!?
5. Pwn runway2: 0x14 * 0x09 + p32(0x804A025+0x1fdb) + ''aaaa'' + p32(0x8049253)
6. Pwn calc: input ''pi'' + ''10014'' 触发 canary 泄 + 0x28 + canary + rbp + ret
7. 多 flag: 0v3rfl0w_the_M00n0ry, I_34t_fl4GS, 1_d0n7_c4r3_571ll_4_m1d_c010r, I_m1sS_4r1thm3t1c_qu1ZZ3s

## 关键 payload

```
uuid 文件存储 / 目录穿越 flag.txt / 0x4c padding + p32(win) / 0x14*0x09 + p32(0x804A025+0x1fdb) + p32(0x8049253) / canary 泄 + 0x28 + canary + rbp + ret
```

## 经验教训

入门级赛事风格:目录穿越/栈溢出/canary 泄 全覆盖;uuid 文件服务常见目录穿越;calc 类题目 'pi' 触发 canary 泄是经典 trick。

## 标签

pwnoh.io、uuid文件存储、目录穿越flag.txt、runway0/1/2栈溢出、calc canary leak、color regex回显、L33t、30+题多方向

## 参考来源

- https://www.ctfiot.com/207473.html
- 原文件：Buckeye_CTF_·_2024_WriteUp.full.md

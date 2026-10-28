---
title: "web选手入门pwn(30) 鹏城杯VM 自定义指令集栈迁移"
category: pwn
tags: ["鹏城杯", "pwn", "custom-vm", "link_s-underflow", "u32-overflow", "memcpy-OOB"]
signals: ["鹏城杯 2024", "custom-vm", "link_s-underflow", "u32-overflow", "memcpy-OOB", "ret2libc", "stack-pivot", "rop", "set_s", "link_s", "copy_s", "memcpy", "ROP", "mov_r"]
difficulty: hard
source: "https://www.ctfiot.com/288074.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(30) 鹏城杯VM 自定义指令集栈迁移

> 赛事：鹏城杯 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

鹏城杯 VM 逆向 + 整数下溢 set_s 触发 link_s+copy_s 越界 memcpy 实现栈迁移打 ROP。

## 攻击链

1. 解析 6 条自定义 VM 指令(mov_r/add_r/store_r/load_r_s/link_s/copy_s) → set_s(1,0x200)+set_s(3,u32_wrap-0x108)=0xFFFFFFE8 → link_s(1,3) 让 s1.idx_b 变成 s3.idx_b - 0x108=0xFFFFFFE0 → copy_s(1,0x100) 触发 memcpy(vm_mem+0x200, vm_mem+0xFFFFFFE0, 0x100) 把栈拷到 vm_mem+0x200 / 但 0x200 是 vm_mem 内偏移，因此实际是 vm_mem 内 0x200 处被填充为栈内容 / 多次 add_r+store_r 写 ROP 链

## 关键 payload

```
set_s(3, 0x100000000 - 0x108)  # u32 下溢让 idx_b = 0xFFFFFFE8  link_s(1,3)  copy_s(1, fake_stack=0x2000)
```

## 经验教训

自定义 VM 题逆向重点在寄存器/段寄存器字段长度；u32 wrap 减法是绕过长度检查的标准手段；copy_s(1, offset) 中 offset 是 vm_mem 内偏移，但 src (link_s 后的 idx_b) 是用户控制的任意 32 位值，组合触发任意地址 memcpy。

## 标签

custom-vm、link_s-underflow、u32-overflow、memcpy-OOB、ret2libc、stack-pivot

## 参考来源

- https://www.ctfiot.com/288074.html
- 原文件：web选手入门pwn(30)——鹏城杯VM.full.md

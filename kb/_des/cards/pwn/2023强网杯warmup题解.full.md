---
title: "2023 强网杯 warmup 题解"
category: pwn
tags: ["强网杯 2023", "pwn", "off_by_null", "House_of_apple2", "_IO_wfile_jumps", "高版本绕过"]
signals: ["强网杯 2023 2023", "off_by_null", "House_of_apple2", "_IO_wfile_jumps", "高版本绕过", "栈迁移", "tcache_dup", "_IO_wfile_overflow", "堆重叠", "heap_exploit", "warmup", "off", "null", "House"]
difficulty: hard
source: "https://www.ctfiot.com/165317.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 强网杯 warmup 题解

> 赛事：强网杯 2023 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

强网杯 warmup：off by null + House of apple2 + _IO_wfile_overflow + 栈迁移 ORW。

## 攻击链

1. 漏洞点：add 函数 off by null 漏洞
2. 利用链：off by null + chunk overlap + 改 tcache fd 指向 stdout
3. 申请到 stdout 区域写 fake IO_FILE_plus_struct
4. 走 House of apple2 _IO_wfile_overflow 链
5. vtable 设置 _IO_wfile_jumps - 0x20，触发 _IO_wfile_overflow
6. _wide_data 指向 stdout - 0x48
7. _wide_data->_wide_vtable->_doallocate = leave_ret
8. 栈迁移到 stdout + 8 区域
9. pop_rbp + leave_ret 二次栈迁移到 ROP 链
10. 走 syscall open + read + write 完成 ORW

## 关键 payload

```
file1.vtable = libc.sym[_IO_wfile_jumps] + libc_base - 0x20
```

## 经验教训

高版本 off by null 需绕 bck->fd==P 检查；House of apple2 用 _IO_wfile_jumps - 0x20 直接劫持；栈迁移需要 leave; ret 二次迁移。

## 标签

off_by_null、House_of_apple2、_IO_wfile_jumps、高版本绕过、栈迁移、tcache_dup、_IO_wfile_overflow、堆重叠、详细exp注释、pwncli

## 参考来源

- https://www.ctfiot.com/165317.html
- 原文件：2023强网杯warmup题解.full.md

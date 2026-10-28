---
title: "seccon 2022 quals – pwn simplemod by gallileo"
category: pwn
tags: ["SECCON", "pwn", "limited-write", "naked-attribute", "sys-exit", "glibc-32"]
signals: ["SECCON 2022", "limited-write", "naked-attribute", "sys-exit", "glibc-32", "ofs-bound", "alarm-30", "pwn_unknown", "SECCON", "quals", "simplemod", "naked", "syscall", "alarm"]
difficulty: medium
source: "https://www.ctfiot.com/78936.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# seccon 2022 quals – pwn simplemod by gallileo

> 赛事：SECCON 2022 | 方向：pwn | 难度：medium

## 一句话总结

SECCON 2022 quals simplemod 复盘，30 次单字节写 + naked syscall。

## 攻击链

1. alarm(30) 限时 30 秒
2. modify() 单字节写 gbuf[0..0x2000]
3. 30 次操作限制
4. 改 exit_imm 写入 syscall
5. 触发 fini() 调 exit_imm(0)
6. 修改 syscall 号触发其他系统调用

## 关键 payload

```
单字节写 gbuf 任意位置 + naked syscall
```

## 经验教训

有限次数的 1 字节写可以拼凑出任意 syscall gadget。

## 标签

limited-write、naked-attribute、sys-exit、glibc-32、ofs-bound、alarm-30

## 参考来源

- https://www.ctfiot.com/78936.html
- 原文件：seccon_2022_quals_–_pwn_simplemod_by_gallileo.full.md

---
title: "华为杯研究生国赛 adv_lua"
category: pwn
tags: ["华为杯研究生国赛 adv_lua", "pwn", "Lua逆向", "自定义bytes结构", "move UAF", "get_int64/set_int64读写原语"]
signals: ["华为杯研究生国赛 adv_lua 2023", "Lua逆向", "自定义bytes结构", "move UAF", "get_int64/set_int64读写原语", "堆头address劫持", "函数指针system", "/readflag", "rdi控制", "reverse", "adv_lua", "bytes", "move", "UAF"]
difficulty: hard
source: "https://www.ctfiot.com/151498.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 华为杯研究生国赛 adv_lua

> 赛事：华为杯研究生国赛 adv_lua 2023 | 方向：pwn | 难度：hard | 工具：C

## 一句话总结

华为杯 adv_lua：bytes 自定义结构 move 同地址 UAF + 堆头 address 劫持 + 函数指针改 system 执行 /readflag。

## 攻击链

1. 题目: 华为杯研究生国赛 adv_lua (Lua 字节码逆向)
2. 自定义 bytes 数据结构: new(size) 0x30 头部 (size+address) + move(dst,src)
3. 漏洞: move(barr, barr) 同样地址 → free 后再指向 → UAF
4. 任意读写原语: get_int64/set_int64 8 字节读写
5. libc 泄露: a=bytes.new(0x430) + b=bytes.new(0x20) + a.move(a,b) + c=bytes.new(0x20)
6. libcbase = get_int64(c,0) - 0x219ce0
7. heap 泄露: c.move(c,a) + c=bytes.new(0x20) + heapbase = get_int64(c,0)<<12 - 0x600
8. UAF 申请到函数表上, 改 size+address 字段
9. 系统检查 v2>>40-85 < 2 即 (87<<40) 防止申请到 libc
10. 构造 0xb8 堆头 chunk + UAF 改 address 字段
11. 改函数指针为 system
12. 控制 rdi: 改 target=heapbase+0x2a0, 写 /readflag

## 关键 payload

```
bytes.new(0x430) move UAF + set_int64(heap_head+0x28, target) + system("/readflag")
```

## 经验教训

Lua 自定义 C 数据结构逆向要找 move(dst,src) 同样地址漏洞；堆头 size+address 字段是 UAF 利用金矿，劫持 address 实现任意地址读写。

## 标签

Lua逆向、自定义bytes结构、move UAF、get_int64/set_int64读写原语、堆头address劫持、函数指针system、/readflag、rdi控制

## 参考来源

- https://www.ctfiot.com/151498.html
- 原文件：华为杯研究生国赛_adv_lua.full.md

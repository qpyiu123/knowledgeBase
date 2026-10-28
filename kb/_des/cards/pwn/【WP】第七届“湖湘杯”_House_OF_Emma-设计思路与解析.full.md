---
title: "【WP】第七届\"湖湘杯\" House OF Emma 设计思路与解析"
category: pwn
tags: ["湖湘杯", "pwn", "House-of-Emma", "_IO_cookie_jumps", "_IO_cookie_file", "cookie_read_function"]
signals: ["湖湘杯 2021", "House-of-Emma", "_IO_cookie_jumps", "_IO_cookie_file", "cookie_read_function", "cookie_write_function", "PTR_DEMANGLE", "large-bin-attack", "glibc-2.35", "rce", "House", "Emma", "IO_cookie_jumps", "vtable"]
difficulty: hard
source: "https://www.ctfiot.com/12959.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第七届"湖湘杯" House OF Emma 设计思路与解析

> 赛事：湖湘杯 2021 | 方向：pwn | 难度：hard

## 一句话总结

第七届湖湘杯 House of Emma 高级 IO 攻击，利用 _IO_cookie_jumps vtable + large bin attack 绕 vtable 检查。

## 攻击链

1. large bin attack 写 _IO_list_all + 触发 _IO_flush_all_lockp → 调 __doallocate/伪造 _IO_FILE + vtable = _IO_cookie_jumps（不被检查）/cookie_read_function = system 触发 RCE

## 关键 payload

```
_IO_cookie_jumps vtable 不在检查表 +  large bin attack
```

## 经验教训

_IO_cookie_jumps 是 _IO_FILE_plus vtable 检查白名单外的合法 vtable；_IO_cookie_file 结构体含 cookie_read_function 指针可被劫持；large bin attack 写 _IO_list_all 是触发 _IO_flush_all_lockp 的经典手法。

## 标签

House-of-Emma、_IO_cookie_jumps、_IO_cookie_file、cookie_read_function、cookie_write_function、PTR_DEMANGLE、large-bin-attack、glibc-2.35

## 参考来源

- https://www.ctfiot.com/12959.html
- 原文件：【WP】第七届“湖湘杯”_House_OF_Emma-设计思路与解析.full.md

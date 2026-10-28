---
title: "数据安全积分争夺赛西区WP - 2.31 UAF+RC4魔改+表替换"
category: misc
tags: ["数据安全积分争夺赛西区", "misc", "libc-2.31_UAF", "__free_hook+one_gadget", "0x508+0x38", "RC4魔改"]
signals: ["数据安全积分争夺赛西区 2024", "libc-2.31_UAF", "__free_hook+one_gadget", "0x508+0x38", "RC4魔改", "0xd3异或", "自解密shellcode", "mprotect_RWX", "表替换208EC37FD94165AB", "heap_exploit", "libc-2", "UAF", "RC4", "phtml"]
difficulty: medium
source: "https://www.ctfiot.com/240445.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 数据安全积分争夺赛西区WP - 2.31 UAF+RC4魔改+表替换

> 赛事：数据安全积分争夺赛西区 2024 | 方向：misc | 难度：medium

## 一句话总结

数据安全积分争夺赛西区WP:libc-2.31 UAF+RC4魔改+表替换。

## 攻击链

1. 数据安全3:phtml上传绕过后翻文件 → 数据安全5:libc-2.31 UAF 0x508泄露libc + 0x38 tcache编辑__free_hook=one_gadget 0xe3b01 → 数据安全7:自解密shellcode(XOR 0xd3)+魔改RC4(key="103906d6c9429372"+init+4常数+t=box[i]+box[j]+15)+字典208EC37FD94165AB表替换得原文

## 关键 payload

```
libc-2.31 UAF + __free_hook+one_gadget 0xe3b01 + RC4魔改+4常数+15 + 表替换
```

## 经验教训

libc-2.31 UAF经典:0x508 chunk进unsorted bin+0x38 tcache+__free_hook劫持;one_gadget 0xe3b01;自解密shellcode用XOR+RC4特征调试;RC4魔改init+4常数+exchange t=box[i]+box[j]+15;表替换208EC37FD94165AB→0123456789abcdef字典逆替换。

## 标签

libc-2.31_UAF、__free_hook+one_gadget、0x508+0x38、RC4魔改、0xd3异或、自解密shellcode、mprotect_RWX、表替换208EC37FD94165AB、libc-2.31、phtml上传、数据安全、数据加密

## 参考来源

- https://www.ctfiot.com/240445.html
- 原文件：数据安全积分争夺赛西区wp.full.md

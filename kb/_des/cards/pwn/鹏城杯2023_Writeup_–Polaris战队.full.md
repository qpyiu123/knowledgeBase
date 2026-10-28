---
title: "鹏城杯2023 Writeup –Polaris战队"
category: pwn
tags: ["鹏城杯 2023", "pwn", "6502-cpu-emu", "custom-vm", "tcache-dup", "FSOP"]
signals: ["鹏城杯 2023 2023", "6502-cpu-emu", "custom-vm", "tcache-dup", "FSOP", "off-by-one", "heap-overlap", "rust-reverse", "rc4-decrypt", "shellcode", "Polaris", "PWN4", "silent", "babyheap"]
difficulty: hard
source: "https://www.ctfiot.com/143115.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 鹏城杯2023 Writeup –Polaris战队

> 赛事：鹏城杯 2023 2023 | 方向：pwn | 难度：hard

## 一句话总结

鹏城杯2023 Polaris战队WP,PWN4题(6502模拟器+silent栈迁移+babyheap FSOP+咖啡机)+RE2题(Rust猜数字+RC4 PE节区)+WEB3题(反序列化+glob爆破+tera SSTI)。

## 攻击链

1. 6502 CPU模拟器: get_mem/write_mem+IZX寻址模式,LDX/LDA/STA/ADC指令组合写shellcode
2. silent: read溢出0x100字节+栈迁移到bss+爆破write+_start重复执行+汇编shellcode open/read/write
3. babyheap: readn off-by-one构造chunk overlap+tcache劫持stdout泄露栈+栈劫持ROP
4. Auto_Coffee_machine: re(idx)密码bypass后edit越界改stdout+libc泄露+__free_hook劫持
5. Bad PE: RC4 th3k3y! 解密节区释放可执行程序
6. web1: PHP反序列化Hacker+__get+finish->hacker()链触发
7. web2: glob://backdoor_*.php爆破32字符后门+title[]=.php/data[]=<?php system("cat /f*")双参数覆盖
8. Tera: tera模板引擎{%%}块标签绕表达式注入+__tera_context查看上下文

## 关键 payload

```
6502 LDX/LDA/ADC/STA字节码组合
```

## 经验教训

6502/ARM等异构CPU模拟器PWN题的关键是识别寻址模式(IZX)+指令集,栈迁移爆破write是2023年新热点,Rust逆向需要从unsafe块开始跟,tera模板{%%}块是常见SSTI绕表达式方式。

## 标签

6502-cpu-emu、custom-vm、tcache-dup、FSOP、off-by-one、heap-overlap、rust-reverse、rc4-decrypt、glob-fuzz、tera-ssti、php-deserialize

## 参考来源

- https://www.ctfiot.com/143115.html
- 原文件：鹏城杯2023_Writeup_–Polaris战队.full.md

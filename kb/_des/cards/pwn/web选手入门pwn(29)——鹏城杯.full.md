---
title: "web选手入门pwn(29) 鹏城杯"
category: pwn
tags: ["鹏城杯", "pwn", "ret2libc", "struct-func-ptr", "leave-ret-pivot", "format-string-leak"]
signals: ["鹏城杯 2024", "ret2libc", "struct-func-ptr", "leave-ret-pivot", "format-string-leak", "gets-overflow", "rop", "ROP", "leave", "bank", "send", "sendlineafter", "you"]
difficulty: medium
source: "https://www.ctfiot.com/287505.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(29) 鹏城杯

> 赛事：鹏城杯 2024 | 方向：pwn | 难度：medium | 工具：ROP

## 一句话总结

鹏城杯两题：银行系统栈溢出 + ROP/leave 跳板 + 函数指针伪造调用。

## 攻击链

1. 题目1(bank) send A*20 触发栈溢出 → sendlineafter(you?) sendlineafter(withdraw?) 走业务/finish payload = p64(got_write)+A*0x50+p64(0x4010D0) 让 ROP 回到 start 重入/finish payload = p64(got_write)+ret+pop_rdi(binsh)+system+...+p64(stack_addr-360)+leave/题目2(animals) ptr_obj.state+name+attr+desc+func/写3个动物ptr: bird.func=start让其执行start泄露canary(%23$p)/写bird.func=system+cat.name=/bin/sh+dog call func调用

## 关键 payload

```
题目1 leave; ret 让 rsp 跳到 0x55555555b700 (即栈上我们布置的 ROP 区)  题目2 bird.func=system + cat.name="/bin/sh\x00" + dog 触发 func
```

## 经验教训

leave; ret 跳板把 rsp 跳到已知地址（提前布置 ROP 的位置）；结构体 func 字段是经典的"伪函数指针"目标，先把 name 写成 "/bin/sh" 再改 func=system 即可 shell。

## 标签

ret2libc、struct-func-ptr、leave-ret-pivot、format-string-leak、gets-overflow

## 参考来源

- https://www.ctfiot.com/287505.html
- 原文件：web选手入门pwn(29)——鹏城杯.full.md

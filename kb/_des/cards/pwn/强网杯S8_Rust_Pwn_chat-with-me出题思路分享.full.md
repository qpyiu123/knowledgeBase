---
title: "强网杯 S8 Rust Pwn chat-with-me 出题思路分享"
category: pwn
tags: ["强网杯", "pwn", "Rust", "lifetime-extension", "Vec", "dangling-reference"]
signals: ["强网杯 2024", "Rust", "lifetime-extension", "Vec", "dangling-reference", "UAF", "ChatBox", "get_ptr", "static-mut", "pwn_unknown", "Pwn", "static", "mut", "Msg"]
difficulty: hard
source: "https://www.ctfiot.com/219681.html"
tools: ["Rust", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯 S8 Rust Pwn chat-with-me 出题思路分享

> 赛事：强网杯 2024 | 方向：pwn | 难度：hard | 工具：Rust、pwntools

## 一句话总结

强网杯 S8 Rust Pwn：Vec<&'static mut Msg> 借用扩展为 'static lifetime 导致悬垂指针，edit 触发 UAF。

## 攻击链

1. Rust 聊天框: 1=add, 2=show, 3=edit, 4=delete, 5=exit
2. 结构: struct ChatBox { msg_list: Vec<&''static mut Msg> }
3. 漏洞: get_ptr() 通过 fn ident<''a,''b>(val_b: &''b mut T) -> &''a mut T 把栈上 msg 借用成 ''static lifetime
4. push 进 Vec 后, msg 出作用域被释放, Vec 仍持有 'static 引用 → 悬垂指针
5. 利用: add → add → delete index 0 → edit index 0 (触发 UAF 写已释放栈)
6. 由于栈帧被覆盖, edit 写入可被后续 read 读到
7. libc-2.39-0ubuntu8.3, 用 pwntools + ret2libc/one_gadget
8. 难点: Rust 符号名 mangling + inline(never) 函数边界

## 关键 payload

```
Vec<&'static mut Msg> + 栈 msg 悬垂 + edit 写 UAF + 后续调用覆盖栈
```

## 经验教训

Rust 借用检查器不能防止所有生命周期误用，unsafe fn ident() 提升 lifetime 是经典反模式。

## 标签

Rust、lifetime-extension、Vec、dangling-reference、UAF、ChatBox、get_ptr、static-mut、libc-2.39、GeekCmore

## 参考来源

- https://www.ctfiot.com/219681.html
- 原文件：强网杯S8_Rust_Pwn_chat-with-me出题思路分享.full.md

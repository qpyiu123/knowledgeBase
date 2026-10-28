---
title: "Buuctf 刷题记录 - ZJCTF 2019 EasyHeap"
category: pwn
tags: ["ZJCTF", "pwn", "heap 菜单 1/2/3/4/4869", "magic 全局", "0x6020c0", "free 没清指针"]
signals: ["ZJCTF 2019", "heap 菜单 1/2/3/4/4869", "magic 全局", "0x6020c0", "free 没清指针", "0x71 fake chunk", "heaparray 0x6020e0", "got 表覆写", "fill 改 free.got → system", "heap", "ZJCTF", "EasyHeap", "free", "x71"]
difficulty: medium
source: "https://www.ctfiot.com/286402.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Buuctf 刷题记录 - ZJCTF 2019 EasyHeap

> 赛事：ZJCTF 2019 | 方向：pwn | 难度：medium

## 一句话总结

ZJCTF 2019 EasyHeap — 堆菜单 free 没清指针 + 0x71 fake chunk + 0x6020ad fd 偏 0x23 字节对齐 + heaparray 落 free.got + fill 改 free.got→system 触发 system("/bin/sh")。

## 攻击链

1. 菜单 1: create_heap, size 0x60 + content ''aaa
2. 菜单 2: edit_heap, 改 index 0 内容 0x68 ''a'' + p64(0x71) + p64(0x6020ad)
3. free index 1 → 0x71 fastbin → 0x6020ad (unsorted bin fd 偏 0x23)
4. 菜单 1: ''/bin/sh\x00'' 占 index 1 → content 是 /bin/sh 字符串
5. 菜单 1: 0x23 ''a'' + p64(free.got) 占 index 2 → heaparray 落 free.got
6. 菜单 2: fill index 2 → 写 p64(system.plt) 到 free.got
7. free index 1 → 触发 system("/bin/sh")

## 关键 payload

```
free 没清指针 / 0x71 fake chunk / 0x6020ad 偏 0x23 / 0x23 字节对齐 + p64(free.got) / fill 改 free.got → system / free("/bin/sh")
```

## 经验教训

堆菜单 free 不清指针 + 利用 unsorted bin fd 偏 0x23 字节对齐 0x6020XX 是经典 trick;fill 改 got 表 (free→system) 是最终利用。

## 标签

heap 菜单 1/2/3/4/4869、magic 全局、0x6020c0、free 没清指针、0x71 fake chunk、heaparray 0x6020e0、got 表覆写、fill 改 free.got → system、0x6020ad fd 链

## 参考来源

- https://www.ctfiot.com/286402.html
- 原文件：Buuctf刷题记录-ZJCTF_2019_EasyHeap.full.md

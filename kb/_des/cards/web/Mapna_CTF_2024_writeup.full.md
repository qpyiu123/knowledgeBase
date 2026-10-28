---
title: "Mapna CTF 2024 writeup (purify - Puppeteer + WebAssembly DOMPurify bypass)"
category: web
tags: ["Mapna CTF", "web", "Puppeteer bot", "WebAssembly DOMPurify", "postMessage", "buf 溢出"]
signals: ["Mapna CTF 2024", "Puppeteer bot", "WebAssembly DOMPurify", "postMessage", "buf 溢出", "XSS", "escape_tag", "web_unknown", "Mapna", "CTF", "purify", "Puppeteer", "bot", "WebAssembly"]
difficulty: hard
source: "https://www.ctfiot.com/158808.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Mapna CTF 2024 writeup (purify - Puppeteer + WebAssembly DOMPurify bypass)

> 赛事：Mapna CTF 2024 | 方向：web | 难度：hard

## 一句话总结

Mapna CTF 2024 purify: Puppeteer bot + WebAssembly DOMPurify (purify.c) 字节级 sanitize，buf 0x1000 满后 OOB 写覆盖 is_dangerous 指针。

## 攻击链

1. |

## 关键 payload

```
|
```

## 经验教训

|

## 标签

Puppeteer bot、WebAssembly DOMPurify、postMessage、buf 溢出、XSS、escape_tag

## 参考来源

- https://www.ctfiot.com/158808.html
- 原文件：Mapna_CTF_2024_writeup.full.md

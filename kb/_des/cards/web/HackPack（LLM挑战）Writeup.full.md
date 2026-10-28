---
title: "HackPack（LLM挑战）Writeup"
category: web
tags: ["HackPack CTF (LLM挑战)", "web", "llm", "prompt-injection", "yellowdog", "pixel-bot"]
signals: ["HackPack CTF (LLM挑战) 2024", "llm", "prompt-injection", "yellowdog", "pixel-bot", "ssti", "jinja2", "ssrf", "google-store", "web_unknown", "HackPack", "LLM", "YellowDog", "prompt"]
difficulty: medium
source: "https://www.ctfiot.com/173678.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackPack（LLM挑战）Writeup

> 赛事：HackPack CTF (LLM挑战) 2024 | 方向：web | 难度：medium

## 一句话总结

HackPack LLM挑战：YellowDog编号枚举+pixel-bot prompt injection

## 攻击链

1. YellowDog-1: 描述黄狗LLM服务
2. carolina89 编号不可点击
3. 修改数据包编号为carolina89获flag
4. pixel-bot: 概括Google商店
5. 限制google域名
6. bot访问+分析返回结果
7. SSRF或LLM prompt injection
8. YellowDog LLM安全问题

## 关键 payload

```
改carolina89编号; prompt injection绕过google限制
```

## 经验教训

LLM应用安全常结合prompt injection+IDOR+SSRF

## 标签

llm、prompt-injection、yellowdog、pixel-bot、ssti、jinja2、ssrf、google-store

## 参考来源

- https://www.ctfiot.com/173678.html
- 原文件：HackPack（LLM挑战）Writeup.full.md

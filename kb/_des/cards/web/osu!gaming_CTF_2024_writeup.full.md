---
title: "osu!gaming CTF 2024 writeup"
category: web
tags: ["osu!gaming", "web", "express", "purify", "xss-bypass", "youtube-bbcode"]
signals: ["osu!gaming 2024", "express", "purify", "xss-bypass", "youtube-bbcode", "image-lfi", "websocket", "rhythm-game", "bpmspoof", "file_read", "osu", "gaming", "CTF", "writeup"]
difficulty: hard
source: "https://www.ctfiot.com/165876.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# osu!gaming CTF 2024 writeup

> 赛事：osu!gaming 2024 | 方向：web | 难度：hard

## 一句话总结

osu!gaming CTF 2024 writeup：Express 路径遍历 + purify 后 XSS + WebSocket BPM 伪造。

## 攻击链

1. /image?path=file.png' LFI 限制 png/jpg
2. ?path=foo.png/../../../etc/passwd' 绕
3. renderBio purify.sanitize 后 replaceAll [youtube]...[/youtube]
4. 净化后再注入 → XSS
5. dummy=" onload="fetch(...document.cookie)
6. 管理员 admin cookie 截取
7. /api/update POST csrf + bio
8. websocket 模拟点击伪造 BPM
9. /score 高分

## 关键 payload

```
purify 后处理 + youtube BBCode XSS + BPM 伪造
```

## 经验教训

purify.sanitize 后再做字符串处理是经典 XSS 绕过模式。

## 标签

express、purify、xss-bypass、youtube-bbcode、image-lfi、websocket、rhythm-game、bpmspoof

## 参考来源

- https://www.ctfiot.com/165876.html
- 原文件：osu!gaming_CTF_2024_writeup.full.md

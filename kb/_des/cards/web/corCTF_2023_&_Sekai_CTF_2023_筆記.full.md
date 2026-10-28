---
title: "corCTF 2023 & Sekai CTF 2023 筆記"
category: web
tags: ["corCTF+Sekai", "web", "xs-leak", "xs-search", "rtc-stun", "font-face-oracle"]
signals: ["corCTF+Sekai 2023", "xs-leak", "xs-search", "rtc-stun", "font-face-oracle", "file-leak", "http-smuggling", "nmap", "nse", "web_unknown", "corCTF", "Sekai", "CTF", "XS-Leak"]
difficulty: hard
source: "https://www.ctfiot.com/133112.html"
tools: ["nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# corCTF 2023 & Sekai CTF 2023 筆記

> 赛事：corCTF+Sekai 2023 | 方向：web | 难度：hard | 工具：nmap

## 一句话总结

corCTF 2023 + Sekai CTF 2023 跨比赛笔记合集，XS-Leak + RCE 双重攻击面。

## 攻击链

1. WebRTC STUN 泄漏 flag 子域
2. font-face 10000 次 search 触发后端延迟
3. SVG foreignObject + iframe sandbox
4. HTTP Request Smuggling (CL/TE)
5. Nmap NSE 脚本执行
6. nginx proxy_pass IP 限制绕过
7. 缓存探测 + leakless note oracle

## 关键 payload

```
WebRTC STUN 子域 / font-face 字符时延 / HTTP smuggling CL.TE
```

## 经验教训

现代 WEB 难度的天花板在 corCTF/Sekai 级别——纯前端 XS-Leak + 协议层 RCE + 信息泄漏组合拳。

## 标签

xs-leak、xs-search、rtc-stun、font-face-oracle、file-leak、http-smuggling、nmap、nse、rce

## 参考来源

- https://www.ctfiot.com/133112.html
- 原文件：corCTF_2023_&_Sekai_CTF_2023_筆記.full.md

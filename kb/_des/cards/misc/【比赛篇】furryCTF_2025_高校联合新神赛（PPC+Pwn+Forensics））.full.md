---
title: "【比赛篇】furryCTF 2025 高校联合新神赛（PPC+Pwn+Forensics）"
category: misc
tags: ["furryCTF", "misc", "PPC编程题", "爬虫-base16", "多页拼接", "fmt-string"]
signals: ["furryCTF 2025", "PPC编程题", "爬虫-base16", "多页拼接", "fmt-string", "栈溢出", "vol内存取证", "misc_unknown", "furryCTF", "PPC", "Pwn", "Forensics", "flagReader", "base16"]
difficulty: medium
source: "https://www.ctfiot.com/298529.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【比赛篇】furryCTF 2025 高校联合新神赛（PPC+Pwn+Forensics）

> 赛事：furryCTF 2025 | 方向：misc | 难度：medium

## 一句话总结

furryCTF 2025 高校联合新神赛 WP，PPC 爬虫 + Pwn 基础 + Forensics 内存取证三大方向。

## 攻击链

1. 1. PPC flagReader 爬 480 页 base16 字符拼字符串 /2. Pwn 经典 fmt-string 偏移爆破 /3. Forensics vol 内存镜像

## 关键 payload

```
/api/flag/char/{i}  480 页  base64 + hex 拼接
```

## 经验教训

PPC 题目多用爬虫脚本自动化；fmt-string + 栈溢出是 PWN 入门；vol 是 Windows 内存取证标准。

## 标签

PPC编程题、爬虫-base16、多页拼接、fmt-string、栈溢出、vol内存取证

## 参考来源

- https://www.ctfiot.com/298529.html
- 原文件：【比赛篇】furryCTF_2025_高校联合新神赛（PPC+Pwn+Forensics））.full.md

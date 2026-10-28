---
title: "湖南省第二届职工数字化应用技术技能大赛-数据安全管理员赛项选拔赛-科目二-wp"
category: web
tags: ["湖南省第二届职工数字化应用技术技能大赛", "web", "base16解码", "RSA+LCG", "数据脱敏逆向", "dirsearch扫描"]
signals: ["湖南省第二届职工数字化应用技术技能大赛 2025", "base16解码", "RSA+LCG", "数据脱敏逆向", "dirsearch扫描", "JS前端加密绕过", "身份证号", "web_unknown", "base16", "RSA", "LCG", "dirsearch", "poem"]
difficulty: easy
source: "https://www.ctfiot.com/272179.html"
tools: ["Dirsearch"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 湖南省第二届职工数字化应用技术技能大赛-数据安全管理员赛项选拔赛-科目二-wp

> 赛事：湖南省第二届职工数字化应用技术技能大赛 2025 | 方向：web | 难度：easy | 工具：Dirsearch

## 一句话总结

湖南省第二届职工数安赛D2：base16+RSA+LCG+数据脱敏+dirsearch+JS前端加密绕过

## 攻击链

1. 题目1 base16解码身份证号→题目2 RSA+LCG（AI解）→题目3 缺失（poem.png）→题目4 ds_re5 IDA逆向→题目5 dirsearch扫描robots.txt发现/tjhack/→题目6 JS前端加密请求体构造+两个账号登录+查询接口

## 关键 payload

```
base16解码;RSA+LCG;dirsearch robots.txt;JS加密timestamp+user_id+data
```

## 经验教训

数据安全管理员赛题偏简单基础+AI辅助解题（DeepSeek比qwen本地0.6b强）

## 标签

base16解码、RSA+LCG、数据脱敏逆向、dirsearch扫描、JS前端加密绕过、身份证号

## 参考来源

- https://www.ctfiot.com/272179.html
- 原文件：湖南省第二届职工数字化应用技术技能大赛-数据安全管理员赛项选拔赛-科目二-wp.full.md

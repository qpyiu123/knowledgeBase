---
title: "2023 D^3CTF writeup by 万年三等奖"
category: web
tags: ["2023 D^3CTF (AntCTF x D^3CTF)", "web", "D3CTF", "阿里", "蚂蚁", "Escape-Plan"]
signals: ["2023 D^3CTF (AntCTF x D^3CTF) 2023", "D3CTF", "阿里", "蚂蚁", "Escape-Plan", "Python-sandbox", "list-dict-substitution", "d3cloud", "d3node", "rce", "sqli", "web_unknown", "reverse", "CTF"]
difficulty: hard
source: "https://www.ctfiot.com/113179.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 D^3CTF writeup by 万年三等奖

> 赛事：2023 D^3CTF (AntCTF x D^3CTF) 2023 | 方向：web | 难度：hard | 工具：Python

## 一句话总结

2023 D^3CTF：Python list(dict()) 沙箱逃逸 + FilesystemAdapter zip 命令注入 + d3sky XOR ring

## 攻击链

1. WEB Escape Plan: list(dict(...))[] 切片拿 ''_'' 字符 + base64 payload, RCE 拿 flag
2. d3cloud: admin/admin → FilesystemAdapter putFileAs → 上传 zip 自动 unzip → 文件名命令注入: 1;echo Y2F0...|base64 -d|bash;.zip
3. d3node: MongoDB NoSQL regex 注入 password[$regex]=''^xxx'' 逐字符爆破
4. PackDependencies 改 package.json prepack 命令 → 触发 npm pack
5. filename[href]=[a] filename[origin]=[1] filename[protocol]=file: ... 任意文件读绕过
6. REVERSE d3sky: 浮点除零异常反调试, attach 绕过, input XOR ring 还原

## 关键 payload

```
ᵉval(vars(ᵉval(list(dict(_a_aiamapaoarata_a_=()))[len([])][::len(list(dict(aa=()))[len([])])])(...))
```

## 经验教训

Python list(dict()) 取空字符串是经典沙箱逃逸；zip 自动解压是 RCE 经典；XOR ring 方程组是 reverse 入门

## 标签

D3CTF、阿里、蚂蚁、Escape-Plan、Python-sandbox、list-dict-substitution、d3cloud、d3node、FilesystemAdapter、zip-slip、prepack-npm、d3sky、浮点反调试、除零异常、XOR-ring

## 参考来源

- https://www.ctfiot.com/113179.html
- 原文件：2023_D^3CTF_writeup_by_万年三等奖.full.md

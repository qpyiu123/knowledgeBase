---
title: "D3CTF 2023 Writeup - Polaris 战队"
category: web
tags: ["D3CTF", "web", "unicode-bypass", "base64", "casino", "vanity"]
signals: ["D3CTF 2023", "unicode-bypass", "base64", "casino", "vanity", "solidity", "locatedb", "gif-pixel", "rc4-prime", "web_unknown", "D3CTF", "Polaris", "Web", "Misc"]
difficulty: medium
source: "https://www.ctfiot.com/114689.html"
tools: ["Python", "Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# D3CTF 2023 Writeup - Polaris 战队

> 赛事：D3CTF 2023 | 方向：web | 难度：medium | 工具：Python、Solidity

## 一句话总结

D3CTF 2023 Polaris 战队 WP，Web/Misc/RE 三大块，含 Casino/Base64 绕过/gif 像素解。

## 攻击链

1. Escape Plan: unicode 数字替代 + base64
2. d3casino: vanity 生成 0x00 地址
3. 部署 91 字节合约 fallback
4. 调用 D3Casino.bet 累计 scores>=10
5. d3readfile: locatedb 搜 flag_in_here
6. d3gif: 像素 (x,y,bin) 还原图
7. d3rc4: is_prime 加 key 字节
8. d3sky: NAND VM 还原

## 关键 payload

```
unicode 旁路关键字 + 91 字节合约 + prime 拓展 key
```

## 经验教训

CTF 越来越像"全栈工程"——Solidity 合约/字节码优化/python 图像/RC4 数学全都要会。

## 标签

unicode-bypass、base64、casino、vanity、solidity、locatedb、gif-pixel、rc4-prime

## 参考来源

- https://www.ctfiot.com/114689.html
- 原文件：D3CTF_2023_Writeup-_Polaris战队.full.md

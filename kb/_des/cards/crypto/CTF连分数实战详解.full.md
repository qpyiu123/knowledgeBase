---
title: "CTF连分数实战详解"
category: crypto
tags: ["公众号文章", "crypto", "crypto", "rsa", "连分数", "wiener"]
signals: ["公众号文章 2022", "crypto", "rsa", "连分数", "wiener", "pell", "渐进分数", "crypto_rsa", "RSA", "Wiener", "Verheul-Tilborg", "Pell", "e-1"]
difficulty: medium
source: "https://www.ctfiot.com/97599.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF连分数实战详解

> 赛事：公众号文章 2022 | 方向：crypto | 难度：medium

## 一句话总结

连分数攻击小d RSA，含Wiener扩展+Verheul-Tilborg+Pell方程

## 攻击链

1. 连分数展开e/N得到渐进分数列表
2. 遍历每个收敛k/d验证k*e-1能否被d整除
3. 若能则得到私钥d分解N=p*q
4. 扩展攻击d<N^0.25用2t+8bits搜索
5. Pell方程x^2-Dy^2=1连分数求最小特解

## 关键 payload

```
def transform(x,y): res=[]; while y: res.append(x//y); x,y=y,x%y
```

## 经验教训

小解密指数RSA用连分数逼近k/d，d<N^0.292时仍可破

## 标签

crypto、rsa、连分数、wiener、pell、渐进分数

## 参考来源

- https://www.ctfiot.com/97599.html
- 原文件：CTF连分数实战详解.full.md

---
title: "解析2025LitCTF-math"
category: crypto
tags: ["LitCTF 2025", "crypto", "RSA", "hint-leak", "noise-factor", "p-plus-q"]
signals: ["LitCTF 2025 2025", "RSA", "hint-leak", "noise-factor", "p-plus-q", "Vieta", "Pollard-Rho", "Miller-Rabin", "isqrt", "crypto_rsa", "LitCTF", "math", "hint", "noise"]
difficulty: medium
source: "https://www.ctfiot.com/278447.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025LitCTF-math

> 赛事：LitCTF 2025 2025 | 方向：crypto | 难度：medium

## 一句话总结

LitCTF 2025 math方向RSA带噪声hint泄露攻击链,标准hint = n + noise*(p+q+noise)形式,40位小素数Pollard-Rho分解+韦达定理还原p,q。

## 攻击链

1. 识别hint异常:hint=p*q+noise*p+noise*q+noise² = n + noise*(p+q+noise)
2. 计算hint_minus_n = hint - n,寻找40位左右素因子noise
3. Pollard-Rho因数分解,验证(noise, d//noise)是否满足isqrt判别式为完全平方
4. 命中noise=942430120937
5. 由hint-n = noise*(p+q+noise)推导S = (hint-n)//noise,p+q = S - noise
6. (p-q)² = (p+q)² - 4n,p-q = isqrt(...)求得
7. p = ((p+q) + (p-q))/2,q = ((p+q) - (p-q))/2
8. 验证p*q == n,计算phi=(p-1)(q-1),d=e⁻¹ mod phi
9. m=c^d mod n,long_to_bytes得flag

## 关键 payload

```
LitCTF{db6f52b9265971910b306754b9df8b76}
```

## 经验教训

任何hint都要先转成数学表达式: hint = n + noise*(p+q+noise) 是关键;小素数因子必用Pollard-Rho;已知p+q和pq用韦达定理。

## 标签

RSA、hint-leak、noise-factor、p-plus-q、Vieta、Pollard-Rho、Miller-Rabin、isqrt、wiener-attack、math-model

## 参考来源

- https://www.ctfiot.com/278447.html
- 原文件：解析2025LitCTF-math.full.md

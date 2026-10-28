---
title: "春秋杯WP｜2023春秋杯春季赛之crypto篇"
category: crypto
tags: ["春秋杯2023春季赛", "crypto", "Pell方程", "连分数", "二项式定理", "恶意ECDH"]
signals: ["春秋杯2023春季赛 2023", "Pell方程", "连分数", "二项式定理", "恶意ECDH", "超椭圆曲线", "双线性对", "离散对数", "crypto_rsa", "crypto", "Pell", "ECDH", "Jacobian", "flag1"]
difficulty: hard
source: "https://www.ctfiot.com/120388.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋杯WP｜2023春秋杯春季赛之crypto篇

> 赛事：春秋杯2023春季赛 2023 | 方向：crypto | 难度：hard

## 一句话总结

春秋杯2023春季赛crypto三题：Pell方程+恶意ECDH+超椭圆曲线Jacobian

## 攻击链

1. 佩尔Pell方程连分数求特解→二项式定理逆推离散对数flag1→ECDHE参数w/a/b/x已知+线性组合z=k1*G-a*k1*Y-wt*G-bY逆推k2→AES-ECB解密flag2→超椭圆曲线Jacobian离散对数求r→AES-ECB解密flag3

## 关键 payload

```
continued_fraction(sqrt(1117));flag1=(enc1-1)//n^2*inverse(233,n)%n;z = M1 - w*t*G - a*x*M1 - b*x*G;k2 = sha256(str(z[0]).encode()).digest()[:6];D2=r*D1;J(HC((sx,sy)))
```

## 经验教训

Pell方程连分数+ECDHE参数已知时逆推k2+超椭圆曲线Jacobian是近年crypto难点

## 标签

Pell方程、连分数、二项式定理、恶意ECDH、超椭圆曲线、双线性对、离散对数

## 参考来源

- https://www.ctfiot.com/120388.html
- 原文件：春秋杯WP｜2023春秋杯春季赛之crypto篇.full.md

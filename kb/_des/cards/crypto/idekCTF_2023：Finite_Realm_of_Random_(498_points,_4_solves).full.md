---
title: "idekCTF 2023: Finite Realm of Random (498 points, 4 solves)"
category: crypto
tags: ["idekCTF", "crypto", "galois-field", "finite-field", "frobenius", "f127"]
signals: ["idekCTF 2023", "galois-field", "finite-field", "frobenius", "f127", "gf32", "conjugates", "freshmen-dream", "sage", "crypto_rsa", "idekCTF", "Galois", "Freshman", "Dream"]
difficulty: hard
source: "https://www.ctfiot.com/92878.html"
tools: ["Radare2", "Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# idekCTF 2023: Finite Realm of Random (498 points, 4 solves)

> 赛事：idekCTF 2023 | 方向：crypto | 难度：hard | 工具：Radare2、Sage

## 一句话总结

idekCTF 2023 高分密码学题，Galois 域上多项式共轭变换 + Freshman's Dream 还原。

## 攻击链

1. L = F_127^32 (Galois 域)
2. 32 字符分块编码为多项式系数
3. 5 次伽罗瓦共轭变换 f → f^(127^k)
4. 利用 Freshman's Dream 公式 φ(r2) = φ(r1)^(p^k)
5. 32 个共轭尝试还原
6. ASCII 范围验证
7. 找到 4 个相容块拼成 flag

## 关键 payload

```
Frobenius 幂 + Freshman's Dream + 32 共轭爆破
```

## 经验教训

有限域上 (a+b)^p = a^p + b^p 的 Freshman's Dream 是处理 Frobenius 幂的关键。

## 标签

galois-field、finite-field、frobenius、f127、gf32、conjugates、freshmen-dream、sage

## 参考来源

- https://www.ctfiot.com/92878.html
- 原文件：idekCTF_2023：Finite_Realm_of_Random_(498_points,_4_solves).full.md

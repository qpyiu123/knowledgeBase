---
title: "HKCERT CTF 2022 Postmortem (I): Easier Crypto Challenges"
category: crypto
tags: ["HKCERT CTF 2022", "crypto", "crypto", "dlp", "cookie-flipping", "cbc"]
signals: ["HKCERT CTF 2022 2022", "crypto", "dlp", "cookie-flipping", "cbc", "base64", "negative-e", "gcd", "mystiz", "crypto_rsa", "HKCERT", "Easy", "Crypto", "DLP"]
difficulty: medium
source: "https://www.ctfiot.com/87576.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HKCERT CTF 2022 Postmortem (I): Easier Crypto Challenges

> 赛事：HKCERT CTF 2022 2022 | 方向：crypto | 难度：medium

## 一句话总结

HKCERT 2022 Easy Crypto：DLP+Cookie翻转+负指数RSA恢复N

## 攻击链

1. DLP: p=1444...g=2 h=679...求 x
2. Cookie flipping: JSON {"username":"mystiz","x":13,"y":5}
3. 改为"mystiz_
4. flag: hkcert22{cu7_4nd_p45t3_1ik3_4_3ng1n3er}
5. CBC bit flipping attack
6. Negative e RSA: e=-1/-2/-3
7. m0="The secret token is "+padding+" and it is encrypted with e = N.
8. gcd(n1, n2, n3) 还原N
9. pow(256, -33, n) * (pow(c1, -1, n) - m1) % n 还原secret

## 关键 payload

```
gcd(c2*(m2*c1+1-m1*c1)^2 - c1^2, c3*(m3*c1+1-m1*c1)^3 - c1^3)  # 求N
```

## 经验教训

负指数e=-1/-2/-3加密可构造已知消息恢复模数N

## 标签

crypto、dlp、cookie-flipping、cbc、base64、negative-e、gcd、mystiz

## 参考来源

- https://www.ctfiot.com/87576.html
- 原文件：HKCERT_CTF_2022_Postmortem_(I)-_Easier_Crypto_Challenges.full.md

---
title: "2022 美团 MTCTF 初赛 writeup by Arr3stY0u"
category: crypto
tags: ["2022 美团 MTCTF 初赛", "crypto", "美团", "CTF", "最小公倍数", "gcd"]
signals: ["2022 美团 MTCTF 初赛 2022", "美团", "CTF", "最小公倍数", "gcd", "RealField", "gift", "p2-approx", "iroot", "misc_math", "crypto_rsa", "web_unknown", "pwn_unknown", "MTCTF"]
difficulty: medium
source: "https://www.ctfiot.com/57358.html"
tools: ["Java", "Spring", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 美团 MTCTF 初赛 writeup by Arr3stY0u

> 赛事：2022 美团 MTCTF 初赛 2022 | 方向：crypto | 难度：medium | 工具：Java、Spring、pwntools

## 一句话总结

美团 MTCTF 6 大类：math + RSA + web + pwn + reverse + misc

## 攻击链

1. CyberSpace: b=[32,38,27,...] flag += chr(b[i]+70) = ''flag{different_xor}
2. strange_rsa1: gift 是 0.9878... 高精度小数，n/gift ≈ q² → iroot 拿 p
3. n 2048 位，gift 1024 位，p ≈ iroot(n/gift, 2) ± 偏移爆破
4. strange_rsa2: 多 e 共享 n，CRT 攻击 e1*e2*...
5. strange_rsa3: 已知 p 高位 + 私钥泄露
6. web: Java 反序列化 / Spring 全家桶
7. pwn: pwncli 库简化 EXP

## 关键 payload

```
p = iroot(n/gift, 2) 爆破 1000 个候选
```

## 经验教训

gift = 高精度小数 → RealField 还原精确 n/gift → iroot 开方爆破 p

## 标签

美团、CTF、最小公倍数、gcd、RealField、gift、p2-approx、iroot、CRT、pwncli、pwntools、整数爆破、RSA

## 参考来源

- https://www.ctfiot.com/57358.html
- 原文件：2022_美团MTCTF初赛_writeup_by_Arr3stY0u.full.md

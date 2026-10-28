---
title: "【WP】第四届 SQCTF 网络安全及信息对抗大赛 Crypto 方向题目全解"
category: crypto
tags: ["SQCTF", "crypto", "Fermat-attack", "RSA-close-prime", "CRT", "ECC-discrete-log"]
signals: ["SQCTF 2025", "Fermat-attack", "RSA-close-prime", "CRT", "ECC-discrete-log", "dp-dp1-leak", "gcd-iroot", "side-channel-template-attack", "RSA-common-modulus", "crypto_rsa", "SQCTF", "Crypto", "RSA", "ECC"]
difficulty: medium
source: "https://www.ctfiot.com/241122.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第四届 SQCTF 网络安全及信息对抗大赛 Crypto 方向题目全解

> 赛事：SQCTF 2025 | 方向：crypto | 难度：medium

## 一句话总结

第四届 SQCTF Crypto 方向 8 大题全解，覆盖 RSA/ECC/侧信道/经典密码学全栈。

## 攻击链

1. 1. RSA Fermat 攻击 (p-q 接近) /2. RSA CRT 多个 (n, c) 组合 /3. e 小 + iroot 求明文 /4. ECC 离散对数 + c1*k - c2 还原 /5. dp + e 爆破求 p q /6. 侧信道模板攻击 euclidean 距离 /7. RSA 公模攻击 gcdext(e1, e2) 求逆 /8. 14 转子密码机爆破

## 关键 payload

```
Fermat attack + CRT + ECC + dp leak + side channel + common modulus + 转子密码机
```

## 经验教训

Fermat 攻击适用 p q 接近；CRT 适用多组 (n, c)；ECC 加法公式；dp 泄漏 + e 爆破；侧信道模板用欧氏距离分类；RSA 公模攻击用扩展欧几里得；14 转子密码机 + 密文定位爆破。

## 标签

Fermat-attack、RSA-close-prime、CRT、ECC-discrete-log、dp-dp1-leak、gcd-iroot、side-channel-template-attack、RSA-common-modulus、rotor-machine

## 参考来源

- https://www.ctfiot.com/241122.html
- 原文件：【WP】第四届SQCTF网络安全及信息对抗大赛Crypto方向题目全解.full.md

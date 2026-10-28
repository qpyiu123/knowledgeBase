---
title: "解析2025LitCTF leak"
category: crypto
tags: ["LitCTF 2025", "crypto", "RSA-dp-leak", "partial-key-exposure", "Coppersmith", "LLL"]
signals: ["LitCTF 2025 2025", "RSA-dp-leak", "partial-key-exposure", "Coppersmith", "LLL", "lattice-attack", "bivariate", "small-root", "CRT-RSA", "crypto_rsa", "LitCTF", "leak", "RSA", "hint"]
difficulty: hard
source: "https://www.ctfiot.com/279542.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025LitCTF leak

> 赛事：LitCTF 2025 2025 | 方向：crypto | 难度：hard

## 一句话总结

LitCTF 2025 leak方向RSA dp高位泄露攻击深度解析,180位dp低位+LLL/Coppersmith寻找小根恢复完整dp,侧信道+实现漏洞双重视角。

## 攻击链

1. 题目生成2048位RSA,e=101位素数,泄露dp的高841位,hint=dp>>180
2. 未知部分:0≤x<2^180 (约1.5×10^54种可能),1≤k<e (约10^30种可能)
3. 数学建模:F(x,k) = A + e*x + k能被p整除,x≪p,k≪p
4. 构造bivariate多项式F(x,k)=A+e*x+k,使用Coppersmith寻找小根
5. LLL算法寻找格中的短向量
6. 从短向量中恢复x和k,得完整dp
7. 验证dp*p在[p+1,p+0x100]范围,反推p,q
8. 标准RSA解密得m

## 关键 payload

```
LitCTF{...}
```

## 经验教训

RSA-CRT实现中泄露dp高位是致命的;Coppersmith小根攻击对(x≪n)的多项式F(x)有效;实际部署中应避免计算和存储dp。

## 标签

RSA-dp-leak、partial-key-exposure、Coppersmith、LLL、lattice-attack、bivariate、small-root、CRT-RSA、side-channel

## 参考来源

- https://www.ctfiot.com/279542.html
- 原文件：解析2025LitCTF_leak.full.md

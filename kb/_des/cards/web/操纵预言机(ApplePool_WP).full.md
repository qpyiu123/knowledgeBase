---
title: "操纵预言机(ApplePool WP) - DeFi UniswapV2预言机价格操纵"
category: web
tags: ["区块链DeFi", "web", "DeFi", "UniswapV2", "预言机", "价格操纵"]
signals: ["区块链DeFi 2023", "DeFi", "UniswapV2", "预言机", "价格操纵", "AppleToken", "AppleRewardPool", "Ownable", "IUniswapV2Pair", "web_unknown", "ApplePool", "token3", "isSolved", "UniswapV2Factory"]
difficulty: hard
source: "https://www.ctfiot.com/107182.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 操纵预言机(ApplePool WP) - DeFi UniswapV2预言机价格操纵

> 赛事：区块链DeFi 2023 | 方向：web | 难度：hard

## 一句话总结

操纵预言机(ApplePool):DeFi UniswapV2预言机价格操纵套利token3耗尽isSolved。

## 攻击链

1. 部署4个AppleToken+UniswapV2Factory+2个pair(token0/token1+token1/token2)+AppleRewardPool → 攻击者通过UniswapV2大量swap token1操纵pair1预言机价格(rate()=amount0*1e18/amount1) → 低价claim/高价deposit+withdraw套利token3 → token3耗尽isSolved

## 关键 payload

```
UniswapV2预言机价格操纵 + token3耗尽isSolved + safemath整数溢出防护
```

## 经验教训

DeFi预言机操纵经典攻击:UniswapV2的getReserves()或balanceOf()直接作为价格源易被大量swap操纵;AppleRewardPool用token3作为奖励,token3耗尽isSolved;use safemath防整数溢出;通过addPool/deposit/withdraw逻辑利用预言机错误价格套利;Ownable限定owner=check合约,普通用户无法直接setApplePertime。

## 标签

DeFi、UniswapV2、预言机、价格操纵、AppleToken、AppleRewardPool、Ownable、IUniswapV2Pair、getReserves、balanceOf、accApplePerShare、token3耗尽、0.5.16、IERCLike、safemath、deposit/withdraw

## 参考来源

- https://www.ctfiot.com/107182.html
- 原文件：操纵预言机(ApplePool_WP).full.md

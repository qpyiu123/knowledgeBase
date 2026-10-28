---
title: "paradigm 2022 ctf — Rescue"
category: web
tags: ["paradigm", "web", "blockchain", "solidity", "uniswap-v2", "sushiswap"]
signals: ["paradigm 2022", "blockchain", "solidity", "uniswap-v2", "sushiswap", "masterchef", "addliquidity", "slipstream", "web_unknown", "paradigm", "Rescue", "SushiSwap", "MasterChefHelper", "poolInfo"]
difficulty: hard
source: "https://www.ctfiot.com/147781.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# paradigm 2022 ctf — Rescue

> 赛事：paradigm 2022 | 方向：web | 难度：hard

## 一句话总结

paradigm 2022 Rescue 区块链题，SushiSwap LP 池重入。

## 攻击链

1. MasterChefHelper 调 masterchef.poolInfo
2. UniswapV2RouterLike 调 swapExactTokensForTokens
3. addLiquidity 拿 LP
4. 漏洞：addLiquidity 不检查 amountOut
5. 用 0 minAmountOut 调 addLiquidity
6. 实际拿 token1 调 addLiquidity
7. 重入 swapTokenForPoolToken
8. 提空 Setup

## 关键 payload

```
addLiquidity 不检查 amountOut + 重入
```

## 经验教训

addLiquidity 的 minAmountOut 不检查 = 任何人都能抽干 LP 池。

## 标签

blockchain、solidity、uniswap-v2、sushiswap、masterchef、addliquidity、slipstream

## 参考来源

- https://www.ctfiot.com/147781.html
- 原文件：paradigm_2022_ctf_——Rescue.full.md

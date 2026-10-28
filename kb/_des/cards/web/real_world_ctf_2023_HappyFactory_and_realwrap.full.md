---
title: "real world ctf 2023 HappyFactory and realwrap"
category: web
tags: ["RWCTF", "web", "blockchain", "solidity", "uniswap-v2-fork", "kp3r"]
signals: ["RWCTF 2023", "blockchain", "solidity", "uniswap-v2-fork", "kp3r", "reward-distribution", "flashloan", "impermanent-loss", "web_unknown", "RWCTF", "HappyFactory", "UniswapV2", "KonohaFactory", "KonohaPair"]
difficulty: hard
source: "https://www.ctfiot.com/90963.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# real world ctf 2023 HappyFactory and realwrap

> 赛事：RWCTF 2023 | 方向：web | 难度：hard

## 一句话总结

RWCTF 2023 HappyFactory 区块链题，自定义 UniswapV2 复刻的 LP 攻击。

## 攻击链

1. 自定义 KonohaFactory/KonohaPair
2. 复刻 UniswapV2 接口
3. 提供 WETH/KP3R 流动性
4. 大量 addLiquidity 累积 LP
5. flashloan 借 KP3R 提流动性
6. swap 操纵价格
7. removeLiquidity 提 ETH + KP3R
8. repay flashloan

## 关键 payload

```
自定义 UniswapV2 复刻 + LP 累积攻击
```

## 经验教训

当 DEX 是 UniswapV2 复刻时，要特别留意 feeTo / feeToSetter 等管理函数是否可调用。

## 标签

blockchain、solidity、uniswap-v2-fork、kp3r、reward-distribution、flashloan、impermanent-loss

## 参考来源

- https://www.ctfiot.com/90963.html
- 原文件：real_world_ctf_2023_HappyFactory_and_realwrap.full.md

---
title: "PARADIGM CTF 2022/Hint Finance"
category: web
tags: ["PARADIGM CTF", "web", "以太坊", "Solidity", "ERC777 重入", "ERC1820Registry 钩子"]
signals: ["PARADIGM CTF 2022", "以太坊", "Solidity", "ERC777 重入", "ERC1820Registry 钩子", "闪电贷", "函数签名碰撞", "0xcae9ca51", "approveAndCall", "logic", "ERC777", "vault", "factory", "token"]
difficulty: hard
source: "https://www.ctfiot.com/80234.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PARADIGM CTF 2022/Hint Finance

> 赛事：PARADIGM CTF 2022 | 方向：web | 难度：hard | 工具：Solidity

## 一句话总结

ERC777 重入 + 函数签名碰撞嵌套 approveAndCall 转走 vault 全部代币

## 攻击链

1. 题目给 vault + factory + 3 个 token 合约（token1/3 是 ERC777，token2 是魔改 ERC20）
2. 目标：让每个 vault 余额 < 初始 1%
3. ERC777 通过 ERC1820Registry 注册 tokensReceived 钩子 → 跟经典重入一样
4. withdraw 时已转账但 totalSupply 未更新 → 重新进入 deposit 增大份额占比
5. 多次 withdraw+deposit 占据大部分份额后提走 → token1/3 解决
6. token2（魔改 ERC20）有 approveAndCall 函数签名 (0xcae9ca51) 跟 flashloan 回调同签名
7. 构造 data 双重满足 onHintFinanceFlashloan 和 approveAndCall
8. 嵌套 approveAndCall → flashloan → approveAndCall 实现 vault 给攻击合约 approve
9. 再 transferFrom 转走 token2
10. 3 个 token 都被盗空 → 满足 vault < 1% 初始 → 拿 flag

## 关键 payload

```
register ERC1820 hook for from/to → withdraw → reenter deposit → loop
```

## 经验教训

任何外部回调（不只是 ETH transfer）都可能造成重入；函数签名碰撞可用于跨合约调用伪装

## 标签

以太坊、Solidity、ERC777 重入、ERC1820Registry 钩子、闪电贷、函数签名碰撞、0xcae9ca51、approveAndCall、嵌套调用

## 参考来源

- https://www.ctfiot.com/80234.html
- 原文件：PARADIGM_CTF_2022题目分析(6)-_Hint_Finance.full.md

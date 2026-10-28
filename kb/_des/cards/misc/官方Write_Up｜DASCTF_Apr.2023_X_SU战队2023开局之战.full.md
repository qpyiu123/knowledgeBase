---
title: "DASCTF Apr.2023 X SU战队2023开局之战官方WP"
category: misc
tags: ["DASCTF Apr.2023 X SU战队2023开局之战", "misc", "区块链", "Solidity", "闪电贷", "ERC3156"]
signals: ["DASCTF Apr.2023 X SU战队2023开局之战 2023", "区块链", "Solidity", "闪电贷", "ERC3156", "FlashLoan", "Vault", "预言机操纵", "Intention签名", "blockchain", "DASCTF", "Apr", "BLOCKCHAIN", "Conflux"]
difficulty: hard
source: "https://www.ctfiot.com/111908.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF Apr.2023 X SU战队2023开局之战官方WP

> 赛事：DASCTF Apr.2023 X SU战队2023开局之战 2023 | 方向：misc | 难度：hard | 工具：Solidity

## 一句话总结

DASCTF Apr.2023 X SU战队开局之战BLOCKCHAIN 4题:闪电贷操纵预言机/Conflux eSpace签名/UnCrackableGame delegatecall/Guess Range重入。

## 攻击链

1. 这必不可能是预言机:Hacker合约构造Intention+签名+闪电贷借999WETH → 兑换比1:1000 → 存1WETH换1000FLAG → 转给Challenge合约 → 链上Poseidon.Blockchain交互;到国链之光一游:Conflux eSpace Testnet水龙头领gas → block.timestamp+keccak256猜key → getFlag触发CaptureTheFlag事件;easyCoin:delegatecall存owner可改;Guess:Range+重入

## 关键 payload

```
闪电贷999WETH + Intention签名(Intention+r/s/v) + TrashOracle + Poseidon.Blockchain框架
```

## 经验教训

闪电贷借出大量代币操纵预言机兑换比例(1:1→1000:1)是经典DeFi攻击;构造特殊Intention结构+链下ECDSA签名(v,r,s)绕过_verifyIntention;Conflux eSpace Testnet需先领gas;block.timestamp+keccak256作key可预测;Solidity 0.8.19+IERC3156FlashBorrower接口;UnCrackableGame经典delegatecall+storage覆盖;Guess猜数字用Range约束+回退检查防重入。

## 标签

区块链、Solidity、闪电贷、ERC3156、FlashLoan、Vault、预言机操纵、Intention签名、Conflux_eSpace、eSpace、tx.origin、block.timestamp、UnCrackableGame、委托调用delegatecall、重入

## 参考来源

- https://www.ctfiot.com/111908.html
- 原文件：官方Write_Up｜DASCTF_Apr.2023_X_SU战队2023开局之战.full.md

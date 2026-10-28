---
title: "【智能合约】D3CTF2019-bet2loss"
category: misc
tags: ["D3CTF", "misc", "智能合约-Solidity", "bet2loss", "croupier-leaked-key", "AirdropCheck-1000-balance"]
signals: ["D3CTF 2019", "智能合约-Solidity", "bet2loss", "croupier-leaked-key", "AirdropCheck-1000-balance", "settleBet-private-sendFunds", "keccak256-entropy", "block.number-赌博", "EIP-191-signature", "misc_unknown", "D3CTF", "croupier", "AirdropCheck", "keccak256"]
difficulty: hard
source: "https://www.ctfiot.com/59608.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【智能合约】D3CTF2019-bet2loss

> 赛事：D3CTF 2019 | 方向：misc | 难度：hard | 工具：Solidity

## 一句话总结

D3CTF 2019 bet2loss 智能合约赌博 + croupier 私钥泄露 + AirdropCheck 薅羊毛 + keccak256 赌博熵预测。

## 攻击链

1. 1. croupier 私钥泄露 0xACB7a6Dc0215cFE38e7e22e3F06121D2a1C42f6C /2. AirdropCheck() 薅羊毛 1000 balance /3. settleBet -> settleBetCommon -> sendFunds 调链 /4. 构造 reveal + block.number 让 betnumber 命中 (uint(keccak256(reveal, placeBlockNumber)) % 100) /5. croupier 签名 commitLastBlock/r/s/v 满足 require

## 关键 payload

```
croupier 0xACB7a6Dc0215cFE38e7e22e3F06121D2a1C42f6C  balance > 300000
```

## 经验教训

bet2loss 类赌博合约 require balance > 阈值；AirdropCheck 给新用户 1000 是薅羊毛入口；croupier 私钥泄露可任意签名；keccak256(reveal, block.number) 在合约中可预测。

## 标签

智能合约-Solidity、bet2loss、croupier-leaked-key、AirdropCheck-1000-balance、settleBet-private-sendFunds、keccak256-entropy、block.number-赌博、EIP-191-signature

## 参考来源

- https://www.ctfiot.com/59608.html
- 原文件：【智能合约】D3CTF2019-bet2loss.full.md

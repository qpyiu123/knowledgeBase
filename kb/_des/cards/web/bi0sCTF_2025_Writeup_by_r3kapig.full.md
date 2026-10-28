---
title: "bi0sCTF 2025 Writeup by r3kapig"
category: web
tags: ["bi0sCTF", "web", "blockchain", "solidity", "transient-storage", "oracle-manipulation"]
signals: ["bi0sCTF 2025", "blockchain", "solidity", "transient-storage", "oracle-manipulation", "dex", "amm", "batchTransfer-overflow", "evade-create2", "web_unknown", "bi0sCTF", "r3kapig", "vault", "DEX"]
difficulty: hard
source: "https://www.ctfiot.com/256546.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# bi0sCTF 2025 Writeup by r3kapig

> 赛事：bi0sCTF 2025 | 方向：web | 难度：hard

## 一句话总结

bi0sCTF 2025 r3kapig 战队 WP 4 道区块链：瞬态存储偷窃/vault 溢出/时间旅行 DEX。

## 攻击链

1. Transient Heist: 借鉴 SIR.trading 瞬态存储漏洞
2. swapCallback 绕过 msg.sender 检查
3. 创建恶意代币 + SwapPair
4. Transient Heist Revenge: ERADICATE2 暴力 create2 salt
5. Empty Vessel: ERC4626 vault + INR batchTransfer 溢出
6. 兑换金额小 → 乘积溢出
7. The Time Travellers DEX: snapshot 漏洞价格操纵
8. 1 ETH 借 INR flashloan 压价
9. mint INR 拉价
10. 50000 ETH bonus 2

## 关键 payload

```
瞬态存储漏洞 + ERADICATE2 + vault 溢出 + DEX 价格操纵
```

## 经验教训

现代区块链 CTF 越来越像真实 DeFi 攻击复现（SIR.trading/Venus 等真实事件）。

## 标签

blockchain、solidity、transient-storage、oracle-manipulation、dex、amm、batchTransfer-overflow、evade-create2、eradicate2

## 参考来源

- https://www.ctfiot.com/256546.html
- 原文件：bi0sCTF_2025_Writeup_by_r3kapig.full.md

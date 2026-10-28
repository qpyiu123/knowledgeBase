---
title: "0CTF/TCTF 2022 NFT Market (Solidity 0.8.15 calldata bug)"
category: web
tags: ["0CTF/TCTF 2022", "web", "Solidity", "0.8.15", "calldata-tuple-head-overflow", "ERC721"]
signals: ["0CTF/TCTF 2022 2022", "Solidity", "0.8.15", "calldata-tuple-head-overflow", "ERC721", "ERC20", "reentrancy", "view-function", "ABI-reencoding", "logic", "web_unknown", "calldata", "tuple", "head"]
difficulty: hard
source: "https://www.ctfiot.com/58223.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 0CTF/TCTF 2022 NFT Market (Solidity 0.8.15 calldata bug)

> 赛事：0CTF/TCTF 2022 2022 | 方向：web | 难度：hard | 工具：Solidity

## 一句话总结

Solidity 0.8.15 calldata tuple head overflow + 数组 swap 删除 + approve 钩子

## 攻击链

1. 目标：拿到 3 个 NFT（id=1, 2, 3）触发 win() emit SendFlag()
2. Part 1: purchaseTest + approve 钩子 — 注册 FakeNFT，在 approve 回调里把 NFT 转给 USER，让 purchaseOrder 给 USER 转账
3. Part 2: Solidity 0.8.15 calldata tuple head overflow bug — abi.encode 转发 SignedCoupon 时 orderId 被覆盖
4. 攻击者构造 orderId=1 的 coupon，但 verifyCoupon 内取 order[0]（自己控制的）
5. Part 3: 综合：airdrop 5 → purchaseTest 拿 1337 → buy #2 → mint FakeNFT 上架 → buy #1 把 own 单变 order[0] → coupon 买 #3

## 关键 payload

```
I, the issuer\
```

## 经验教训

Solidity 编译器 bug 是 web3 CTF 高级考点；upgradeable 数组 swap 删除要小心 order 变化被利用

## 标签

Solidity、0.8.15、calldata-tuple-head-overflow、ERC721、ERC20、reentrancy、view-function、ABI-reencoding、Foundry

## 参考来源

- https://www.ctfiot.com/58223.html
- 原文件：0CTF_2022_TCTF_NFT_Market.full.md

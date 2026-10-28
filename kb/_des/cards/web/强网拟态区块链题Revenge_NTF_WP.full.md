---
title: "强网拟态区块链 Revenge NTF - NFT Market CouponVerifierBeta ECDSA签名"
category: web
tags: ["第五届强网拟态防御国际精英挑战赛", "web", "Solidity", "NFT_Market", "ERC721", "ERC20"]
signals: ["第五届强网拟态防御国际精英挑战赛 2022", "Solidity", "NFT_Market", "ERC721", "ERC20", "OpenZeppelin", "CouponVerifierBeta", "ECDSA", "ecrecover", "web_unknown", "NFT", "Market", "Revenge", "ownerOf"]
difficulty: hard
source: "https://www.ctfiot.com/81173.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网拟态区块链 Revenge NTF - NFT Market CouponVerifierBeta ECDSA签名

> 赛事：第五届强网拟态防御国际精英挑战赛 2022 | 方向：web | 难度：hard | 工具：Solidity

## 一句话总结

强网拟态NFT Market Revenge:伪造NFT合约ownerOf返回market+purchaseTest绕过+CouponVerifierBeta ECDSA签名。

## 攻击链

1. 部署CtfMarket+3个NFT(1/2/3)+CtfToken+CouponVerifierBeta → airdrop领5 token → 部署FakeNFT合约实现ownerOf返回market地址(绕过) → 部署Attacker合约实现onERC721Received返回正确selector → purchaseTest绕过:tested=true + createOrder(nftAddress,tokenId,price) + approve + purchaseOrder → purchaseWithCoupon:伪造SignedCoupon(orderId=0,newprice=1,issuer=market,user=attacker,reason) + ECDSA签名"because"+abi.encode("I, the issuer"+issuer+offer+user+order+at+newprice+because+reason) → win:要求ctfNFT.ownerOf(1/2/3)==msg.sender

## 关键 payload

```
FakeNFT.ownerOf返回market地址 + purchaseTest+tested复用 + CouponVerifierBeta ECDSA ecrecover
```

## 经验教训

NFT Market常见漏洞:FakeNFT合约实现ownerOf返回指定地址绕过isNFTApprovedOrOwner;tested标志一次写入后可绕过purchaseTest复用;CtfMarket.deleted=orders[orderId]=orders[last]+pop但index 0被删后newOrderId=0;CouponVerifierBeta的abi.encode含"because"+reason字段可ECDSA签名伪造。

## 标签

Solidity、NFT_Market、ERC721、ERC20、OpenZeppelin、CouponVerifierBeta、ECDSA、ecrecover、abi.encode、signed_coupon、fakeNFT、orderId_reuse、Airdrop、0.8.16

## 参考来源

- https://www.ctfiot.com/81173.html
- 原文件：强网拟态区块链题Revenge_NTF_WP.full.md

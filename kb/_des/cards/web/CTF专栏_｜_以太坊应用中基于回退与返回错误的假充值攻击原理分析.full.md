---
title: "CTF 专栏｜以太坊应用中基于回退与返回错误的假充值攻击原理分析"
category: web
tags: ["Blockchain CTF", "web", "Solidity 0.8.0", "ERC-20", "transfer 返回 false", "transferFrom 不检查返回值"]
signals: ["Blockchain CTF 2022", "Solidity 0.8.0", "ERC-20", "transfer 返回 false", "transferFrom 不检查返回值", "Exchange enter/exit", "假充值", "balanceOf 虚增", "IERC20 继承", "blockchain", "Solidity", "transfer", "transferFrom", "false"]
difficulty: medium
source: "https://www.ctfiot.com/109229.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 专栏｜以太坊应用中基于回退与返回错误的假充值攻击原理分析

> 赛事：Blockchain CTF 2022 | 方向：web | 难度：medium | 工具：Solidity

## 一句话总结

以太坊假充值攻击 — Solidity ERC-20 transfer/transferFrom 返回 false 不回退 + Exchange enter() 不检查 transferFrom 返回值 + balances 虚增 + exit() 提款。

## 攻击链

1. Solidity 0.8.0 写 StokenERC20 继承 IERC20
2. transfer/transferFrom 余额不足时 return false (不 revert)
3. Exchange enter(): token.transferFrom(msg.sender, this, amount) 不检查返回值
4. balances[msg.sender] += amount 继续执行 → 假充值
5. 攻击: 调用 enter(100 ether) 即使 ERC20 余额 0
6. Exchange 余额虚增, 调 exit() 提款
7. require(amount >= 10 ether) 最低门槛
8. 防御: 用 SafeERC20 或 require(token.transferFrom()) 包装

## 关键 payload

```
transfer return false / transferFrom 不检查 / balances 虚增 / OpenZeppelin SafeERC20 / require token.transferFrom / 10 ether 最低
```

## 经验教训

Solidity 0.8.0 之前 transfer 不回退是经典假充值漏洞;防御: SafeERC20.safeTransferFrom() + require(token.transferFrom());msg.value=10 ether 是常见门槛。

## 标签

Solidity 0.8.0、ERC-20、transfer 返回 false、transferFrom 不检查返回值、Exchange enter/exit、假充值、balanceOf 虚增、IERC20 继承、OpenZeppelin、msg.value 10 ether、onlyOwner

## 参考来源

- https://www.ctfiot.com/109229.html
- 原文件：CTF专栏_｜_以太坊应用中基于回退与返回错误的假充值攻击原理分析.full.md

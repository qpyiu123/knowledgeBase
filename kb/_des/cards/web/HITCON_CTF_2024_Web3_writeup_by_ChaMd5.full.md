---
title: "HITCON CTF 2024 Web3 writeup by ChaMd5"
category: web
tags: ["HITCON CTF 2024", "web", "blockchain", "solidity", "0.8.0", "exp-contract"]
signals: ["HITCON CTF 2024 2024", "blockchain", "solidity", "0.8.0", "exp-contract", "lus-interface", "gem", "merge", "attack", "web_unknown", "HITCON", "CTF", "Web3", "Ilus"]
difficulty: hard
source: "https://www.ctfiot.com/193775.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON CTF 2024 Web3 writeup by ChaMd5

> 赛事：HITCON CTF 2024 2024 | 方向：web | 难度：hard | 工具：Solidity

## 一句话总结

HITCON CTF 2024 Web3：Ilus接口+多Gem合成+stage通关

## 攻击链

1. interface Ilus: register_master/create_gem/merge_gems/stage/gems/assign_gem
2. 0x16012b5ee75F4bd4F917eb6395F945EdBBb365Aa 部署地址
3. MAX_ROUNDS0/1/2 = 100/200/300
4. actions0/1/2 = uint8[] 操作序列
5. GemStatus: ACTIVE/INACTIVE/DESTROYED
6. struct Gem: health/max_health/attack/hardness/...
7. 攻击构造Exp合约: 多次create_gem + merge + assign_gem
8. Fail event + Set event
9. 关键: stage()=某值触发flag

## 关键 payload

```
lus.create_gem() payable + merge_gems() + assign_gem(uint32)
```

## 经验教训

Solidity 0.8+接口题常需读懂Game/Attack/Verify三合约关系

## 标签

blockchain、solidity、0.8.0、exp-contract、lus-interface、gem、merge、attack、enum

## 参考来源

- https://www.ctfiot.com/193775.html
- 原文件：HITCON_CTF_2024_Web3_writeup_by_ChaMd5.full.md

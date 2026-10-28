---
title: "封神台CTF blockchain 美梦成真"
category: misc
tags: ["封神台CTF", "misc", "blockchain", "Solidity", "EVM", "cold-warm-access"]
signals: ["封神台CTF 2025", "blockchain", "Solidity", "EVM", "cold-warm-access", "gas-measurement", "wish_making", "foundry", "view-function", "misc_unknown", "gas", "view", "msg", "sender"]
difficulty: medium
source: "https://www.ctfiot.com/222685.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 封神台CTF blockchain 美梦成真

> 赛事：封神台CTF 2025 | 方向：misc | 难度：medium | 工具：Solidity

## 一句话总结

EVM 冷读/热读 gas 差异作为侧信道让 view 函数在不同调用返回不同值，绕过 wish_making 校验。

## 攻击链

1. 目标合约 wish_making 调用 msg.sender.wish_amount()（view 函数）决定 wishes[tx.origin] 是赋值还是 -1
2. is_solved 要求 wishes[tx.origin] > 1
3. 第一次 wish_amount < 1 → is_less_than=true → wishes = wish_amount
4. 第二次 wish_amount >= 1 → is_less_than=false → wishes = wishes - 1
5. 关键：view 函数无法修改状态，但 EVM 冷读/热读 gas 差异可被测信道利用
6. 攻击合约 wish_amount 用 startGas - gasleft() 测自身消耗 gas
7. 访问 address(0x100).balance 触发冷读消耗 2600 gas（vs 热读 100）
8. 第二次访问时已变热读，消耗仅 100，usedGas < 1000 → 返回 2
9. wish_making 调用：wish_amount=2 → is_less_than=false → wishes = wishes-1
10. 但这是"第一次调用 wish_amount"，所以 is_less_than 判断用 wish_amount=2 → 实际执行 wishes = wish_amount
11. 等等，逻辑是 if(2 < 1) is_less_than=true; else wishes = wishes-1
12. 实际是 wishes[tx.origin] = wish_amount()，即 wishes = 2
13. is_solved 验证 wishes[tx.origin] > 1 = 2 > 1 = true

## 关键 payload

```
wish_amount() { uint256 start = gasleft(); address(0x100).balance; if (start - gasleft() < 1000) return 2; return 0; }
```

## 经验教训

Solidity view 函数虽不能修改状态，但 gasleft() + cold/warm access 是隐蔽的"状态"维度，可作为侧信道被滥用。

## 标签

blockchain、Solidity、EVM、cold-warm-access、gas-measurement、wish_making、foundry、view-function、ChaMd5

## 参考来源

- https://www.ctfiot.com/222685.html
- 原文件：封神台CTF_blockchain_美梦成真.full.md

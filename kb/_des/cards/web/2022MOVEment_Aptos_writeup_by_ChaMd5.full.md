---
title: "2022 MOVEment Aptos writeup by ChaMd5"
category: web
tags: ["2022 MOVEment CTF (Aptos / Move 语言)", "web", "Move", "Aptos", "blockchain", "Web3"]
signals: ["2022 MOVEment CTF (Aptos / Move 语言) 2022", "Move", "Aptos", "blockchain", "Web3", "signer", "event", "account", "init_challenge", "logic", "web_unknown", "checkin", "hello_move", "get_flag"]
difficulty: medium
source: "https://www.ctfiot.com/86671.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 MOVEment Aptos writeup by ChaMd5

> 赛事：2022 MOVEment CTF (Aptos / Move 语言) 2022 | 方向：web | 难度：medium

## 一句话总结

Aptos Move 智能合约 checkin + 三关 hello_move

## 攻击链

1. Q1 checkin: 调 get_flag entry 函数即得 flag
2. aptos move run --function-id 0x3dd3f092...::checkin::get_flag
3. Q2 hello_move: 三关
4. (1) init_challenge 拿 Challenge 资源
5. (2) hash 提交 [103,111,111,100] = 'good
6. (3) discrete_log: 计算 3123592912467026955 的对数
7. (4) add(2u8, 0u8) 让 res.balance < Initialize_balance
8. (5) get_flag 拿 flag
9. Move script 调 init_challenge（不是 entry 需 script 包装）

## 关键 payload

```
discrete_log(3123592912467026955u128) 需解
```

## 经验教训

Move 资源 + 入口函数 + script 调 entry-less 函数是 Web3 入门

## 标签

Move、Aptos、blockchain、Web3、signer、event、account、init_challenge、discrete_log、hash、add、resource

## 参考来源

- https://www.ctfiot.com/86671.html
- 原文件：2022MOVEment_Aptos_writeup_by_ChaMd5.full.md

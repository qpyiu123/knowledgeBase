---
title: "idek 2022: Web && Crypto Writeup by r3kapig"
category: web
tags: ["idekCTF", "web", "golang", "validator-context", "orders", "password-leak"]
signals: ["idekCTF 2022", "golang", "validator-context", "orders", "password-leak", "context-with", "read-order", "seed-1337", "web_unknown", "idekCTF", "r3kapig", "Web", "Crypto", "just-read-it"]
difficulty: hard
source: "https://www.ctfiot.com/93433.html"
tools: ["Go"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# idek 2022: Web && Crypto Writeup by r3kapig

> 赛事：idekCTF 2022 | 方向：web | 难度：hard | 工具：Go

## 一句话总结

idekCTF 2022 r3kapig 战队 Web + Crypto：Go 验证器顺序读 + 固定种子。

## 攻击链

1. /just-read-it POST Orders 数组
2. 每次 WithValidatorCtx 传 reader + o(int)
3. 限制 MaxOrders = 10
4. CheckReadOrder(o) 校验 0 < o <= 100
5. 顺序读 0-99 位置
6. 泄 password 字段
7. initRandomData 用 rand.Seed(1337) 复现
8. 解 flag

## 关键 payload

```
Go validator context 链 + 随机种子 1337
```

## 经验教训

Go rand.Seed(1337) + 24576 字节随机数 + 已知 password 偏移是经典的"复现随机序列"题目。

## 标签

golang、validator-context、orders、password-leak、context-with、read-order、seed-1337

## 参考来源

- https://www.ctfiot.com/93433.html
- 原文件：idek_2022-_Web_&&_Crypto_Writeup_by_r3kapig.full.md

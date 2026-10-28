---
title: "2022 巅峰极客 WriteUp By EDISEC"
category: crypto
tags: ["2022 巅峰极客", "crypto", "Padding-Oracle", "padbuster", "feedback.php", "ban.php"]
signals: ["2022 巅峰极客 2022", "Padding-Oracle", "padbuster", "feedback.php", "ban.php", "file://", "ECC", "point-addition", "add-points", "crypto_oracle", "web_unknown", "lattice", "heap_exploit", "Padding"]
difficulty: hard
source: "https://www.ctfiot.com/53840.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 巅峰极客 WriteUp By EDISEC

> 赛事：2022 巅峰极客 2022 | 方向：crypto | 难度：hard

## 一句话总结

巅峰极客 2022 6 大题：Padding Oracle + Web + ECC + 三道 pwn

## 攻击链

1. Web babyweb: Padding Oracle + padbuster → 密码 0f90844e-f214-4f0b-aaa3-687a8098b896
2. Web ezWeb: /readf/feedback.php 注入 startid=0*, ban.php url=file:///etc/passwd* 任意文件读
3. Crypto point-power: ECC 加法公式 y²=x³+ax+b，联立解方程 a,b → flag bytes
4. Crypto strange curve: long_to_bytes(x) → flag 字节
5. Pwn Gift: libc-2.27 tcache dup → __free_hook = system → /bin/sh
6. Pwn smallcontainer: large bin / unsorted bin 残留指针 leak + UAF
7. Pwn happy_note: libc-2.31 PROTECT_PTR 绕过 (xor = heap_base>>12) + tcache stash unlink
8. StrangeTempreture / nodesystem: 决赛 node 节点题目

## 关键 payload

```
y² = x³ + a*x + b 联立解出 a,b
```

## 经验教训

Padding Oracle 永远可破；ECC 加法公式代数化是基础；PROTECT_PTR 用 xor 绕过

## 标签

Padding-Oracle、padbuster、feedback.php、ban.php、file://、ECC、point-addition、add-points、SageMath、libc-2.27、one_gadget、tcache、SROP、ORW、strangeTempreture

## 参考来源

- https://www.ctfiot.com/53840.html
- 原文件：2022巅峰极客WriteUp_By_EDISEC.full.md

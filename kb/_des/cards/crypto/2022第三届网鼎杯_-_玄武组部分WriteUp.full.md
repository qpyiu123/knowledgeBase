---
title: "2022 第三届网鼎杯 - 玄武组部分 WriteUp"
category: crypto
tags: ["2022 第三届网鼎杯 玄武组", "crypto", "网鼎杯", "玄武", "base62", "自定义字符表"]
signals: ["2022 第三届网鼎杯 玄武组 2022", "网鼎杯", "玄武", "base62", "自定义字符表", "Goldwasser-Micali", "二次剩余", "kernel-pwn", "msg_msg", "crypto_oracle", "kernel_exploit", "web_unknown", "pwn_unknown", "pwn"]
difficulty: hard
source: "https://www.ctfiot.com/56442.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 第三届网鼎杯 - 玄武组部分 WriteUp

> 赛事：2022 第三届网鼎杯 玄武组 2022 | 方向：crypto | 难度：hard | 工具：ROP

## 一句话总结

网鼎杯 2022 玄武：base62 换表 + Goldwasser-Micali 二次剩余 + 内核 pwn UAF

## 攻击链

1. misc999 base62 换表: CHARSET=''9876543210qwertyuiopasdfghjklzxcvbnmMNBVCXZLKJHGFDSAPOIUYTREWQ
2. decode 7dFRjPItGFkeXAALp6GMKE9Y4R4BuNtIUK1RECFlU4f3PomCzGnfemFvO → flag{cf492422-13cb-4123-8bc5-5495f0349494}
3. crypto 二次剩余 (Goldwasser-Micali): x=quadratic_residue 50%, x^r 也是 50%; flag bit=1→x^r (QR), bit=0→r (QR 50%)
4. 13 组数据, flag 错误概率 1/2^13
5. pwn557 内核 UAF: 分配 0x20 opcode 1024 大小, 释放 0x30 不置零, 4 步利用
6. Step 1: 堆喷 msg_msg 主从消息队列
7. Step 2: 构造 UAF, 堆喷 sk_buff 定位 victim
8. Step 3: 堆喷 sk_buff 伪造辅助消息, 泄露 UAF obj 地址
9. Step 4: 堆喷 pipe_buffer, 泄露内核基址
10. Step 5: 伪造 pipe_buffer, 构造 ROP, 劫持 RIP, 提权

## 关键 payload

```
base62.decode('7dFRjPItGFkeXAALp6GMKE9Y4R4BuNtIUK1RECFlU4f3PomCzGnfemFvO')
```

## 经验教训

Goldwasser-Micali 加密是 QR 加密经典；内核 pwn 用 msg_msg/sk_buff/pipe_buffer 是 2022 热点

## 标签

网鼎杯、玄武、base62、自定义字符表、Goldwasser-Micali、二次剩余、kernel-pwn、msg_msg、sk_buff、pipe_buffer、ROP、UAF、slub

## 参考来源

- https://www.ctfiot.com/56442.html
- 原文件：2022第三届网鼎杯_-_玄武组部分WriteUp.full.md

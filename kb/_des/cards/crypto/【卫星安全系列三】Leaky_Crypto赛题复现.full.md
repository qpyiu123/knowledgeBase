---
title: "【卫星安全系列三】Leaky Crypto赛题复现"
category: crypto
tags: ["Hack-A-Sat / Leaky Crypto", "crypto", "AES侧信道", "T-表Cache碰撞", "时间差分析", "密钥链还原"]
signals: ["Hack-A-Sat / Leaky Crypto 2023", "AES侧信道", "T-表Cache碰撞", "时间差分析", "密钥链还原", "AES-128-ECB", "卫星载荷", "THRESHOLD", "crypto_oracle", "AES", "Cache", "hex", "ca6080f575", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/151037.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【卫星安全系列三】Leaky Crypto赛题复现

> 赛事：Hack-A-Sat / Leaky Crypto 2023 | 方向：crypto | 难度：hard

## 一句话总结

AES T-表 Cache 侧信道攻击：100000 (明文, 时间) 数据 + 链式密钥字节还原 + AES 解密。

## 攻击链

1. 题目：100000 个 (明文 hex, 加密时间 ns) 数据
2. AES-128-ECB + 密钥前 6 字节 97ca6080f575 已知
3. 密文 96 字节 flag 加密结果
4. AES T-表查表触发 Cache Hit/Miss
5. Cache Miss 慢 (10776), Cache Hit 快 (10704)
6. 公式: p[i] ^ key[i] == p[j] ^ key[j] (T-表同索引)
7. 链: 0→4→8 / 12→5→9→13 / 1→10→14→2 / 6→15→3→7 / 11
8. THRESHOLD=10 过滤弱信号
9. 已知 key[0..5] = 97ca6080f575 推 key[6..15]
10. key[6]={0xe4,0xe5,0xe6,0xe7} 4 候选
11. itertools.product 笛卡尔积 (4^10 = 1048576)
12. AES 解密 + unpad + 'flag' 验证

## 关键 payload

```
97ca6080f575e646e557f755bf15685e + flag{uniform54349juliet:...}
```

## 经验教训

AES 软件实现 T-表 (SubBytes+ShiftRows+MixColumns 合并) 会因输入命中同一表项触发 Cache Hit 加速；T-表索引 p[i] ^ key[i] 同值 → Cache Hit → 加密时间短；构造 16 字节链 + THRESHOLD 过滤。

## 标签

AES侧信道、T-表Cache碰撞、时间差分析、密钥链还原、AES-128-ECB、卫星载荷、THRESHOLD

## 参考来源

- https://www.ctfiot.com/151037.html
- 原文件：【卫星安全系列三】Leaky_Crypto赛题复现.full.md

---
title: "2025 强网杯 ezran - MT19937 状态恢复攻击"
category: crypto
tags: ["强网杯", "crypto", "MT19937", "PRNG-state-recovery", "GF-2-linear", "shuffle-reverse"]
signals: ["强网杯 2025", "MT19937", "PRNG-state-recovery", "GF-2-linear", "shuffle-reverse", "Fisher-Yates", "gf2bv", "Mersenne-Twister", "gaussian-elimination", "crypto_rsa", "ezran", "PRNG", "getrandbits", "pow"]
difficulty: hard
source: "https://www.ctfiot.com/275603.html"
tools: ["Python", "Radare2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 强网杯 ezran - MT19937 状态恢复攻击

> 赛事：强网杯 2025 | 方向：crypto | 难度：hard | 工具：Python、Radare2

## 一句话总结

2025 强网杯 ezran：MT19937 624 状态 GF(2) 线性方程组恢复 + Fisher-Yates 洗牌逆向。

## 攻击链

1. 题目: MT19937 PRNG 生成 3108 次 (r1, r2)
2. r1 = getrandbits(8), r2 = getrandbits(16)
3. x = (pow(r1, 2*i, 257) & 0xff) ^ r2 → 2 字节大端 gift
4. 总输出 3108 × 2 = 6216 字节
5. flag 用 Python shuffle() 打乱 2025 次
6. 关键: r2 高 8 位 ^ observed = (pow(r1, 2*i, 257) & 0xff) = 0-255
7. 约束: (r2 >> 8) ^ observed ∈ [0, 255]
8. 内部状态 624 个 32 位整数 (19968 bit)
9. 用 gf2bv 库构造线性系统 lin = LinearSystem([32] * 624)
10. 高斯消元法 GF(2) 求解多个解
11. 第一个状态最高位为 1: mt[0] ^ 0x80000000
12. Fisher-Yates 逆: 记录每次交换 (i, j), 反向应用
13. 验证: gg == gift → flag

## 关键 payload

```
getrandbits(8) + getrandbits(16) + gift[2i:2i+2][0] + LinearSystem(624) + Fisher-Yates 逆
```

## 经验教训

MT19937 内部状态 19968 bit 可通过足够样本 (3108) 恢复；GF(2) 线性代数 + 高斯消元是标准攻击。

## 标签

MT19937、PRNG-state-recovery、GF-2-linear、shuffle-reverse、Fisher-Yates、gf2bv、Mersenne-Twister、gaussian-elimination、getrandbits

## 参考来源

- https://www.ctfiot.com/275603.html
- 原文件：解析2025强网杯ezran.full.md

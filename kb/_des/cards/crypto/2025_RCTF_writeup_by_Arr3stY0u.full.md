---
title: "2025 RCTF writeup by Arr3stY0u（GMP MT19937 LSB 格攻击 + seed2 缩放）"
category: crypto
tags: ["2025 RCTF", "crypto", "RCTF GMP MT19937", "gmp_urandomb_ui 取低 31 位", "WARM_UP = 2000 twist", "mti = 2000 % 624 = 128"]
signals: ["2025 RCTF 2025", "RCTF GMP MT19937", "gmp_urandomb_ui 取低 31 位", "WARM_UP = 2000 twist", "mti = 2000 % 624 = 128", "LSB 观测", "twist 线性递推", "temper 移位+按位与/异或", "LSB 取出 1 位", "crypto_unknown", "lattice", "mt19937", "RCTF", "crypto"]
difficulty: hard
source: "https://www.ctfiot.com/282850.html"
tools: ["gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 RCTF writeup by Arr3stY0u（GMP MT19937 LSB 格攻击 + seed2 缩放）

> 赛事：2025 RCTF 2025 | 方向：crypto | 难度：hard | 工具：gmpy2

## 一句话总结

2025 RCTF 高级 crypto：GMP MT19937 自实现 + WARM_UP 2000 + 二次幂模映射 + LSB 1 比特输出，624 LSB 完整观测后用 F2 上 LLL 反推 seed2 → 还原 secret。

## 攻击链

1. 用户 secret=int.from_bytes(secret, 'big') 缩放成 seed
2. 二次幂模映射 seed2 = seed^2 mod N
3. seed2 位填入 MT mt[] 状态：bit31 是 mt[0] 最高位
4. WARM_UP=2000 调用 __gmp_mt_recalc_buffer (twist)
5. mti = 2000 % 624 = 128
6. 标准 MT19937 twist+temper（32 位）取 gmp_urandomb_ui(self.gmp_state, 31) 低 31 位
7. 取最低 1 位 LSB 作为 1 比特随机整数返回
8. 624 LSB 完整观测 → 矩阵 F2 上 LLL → 还原 seed2 → 还原 secret

## 关键 payload

```
mti = 2000 % 624 = 128; gmp_urandomb_ui 取低 31 位
```

## 经验教训

GMP 内置 MT19937 是 gmpy2 / pycryptodome 测试向量的常见来源；自定义 WARM_UP + temper 后取 LSB 是抗直接 MT crack 套路，但只要能取 624 个连续 LSB，F2 上 LLL 仍可还原。

## 标签

RCTF GMP MT19937、gmp_urandomb_ui 取低 31 位、WARM_UP = 2000 twist、mti = 2000 % 624 = 128、LSB 观测、twist 线性递推、temper 移位+按位与/异或、LSB 取出 1 位、矩阵元素数=624 LSB 完整观测、模数 LLL 还原 seed、用户 secret 字节缩放、二次幂模映射

## 参考来源

- https://www.ctfiot.com/282850.html
- 原文件：2025_RCTF_writeup_by_Arr3stY0u.full.md

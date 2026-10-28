---
title: "Beating the kCTF PoW with AVX-512 IFMA for $51k"
category: misc
tags: ["kCTF", "misc", "kCTF PoW", "Mersenne 2^1279-1", "1277平方", "7337迭代"]
signals: ["kCTF 2024", "kCTF PoW", "Mersenne 2^1279-1", "1277平方", "7337迭代", "GMP", "mpz_mul + mpz_mod_2exp", "AVX-512 IFMA", "vpmadd52luq", "stego", "kCTF", "PoW", "Mersenne", "AVX-512"]
difficulty: hard
source: "https://www.ctfiot.com/255114.html"
tools: ["C", "Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Beating the kCTF PoW with AVX-512 IFMA for $51k

> 赛事：kCTF 2024 | 方向：misc | 难度：hard | 工具：C、Rust

## 一句话总结

kCTF PoW 51k 美元奖金 — Mersenne 2^1279-1 模 + 1277 平方 + 7337 迭代 + AVX-512 IFMA vpmadd52luq + 25 个 52-bit limbs + 7 个 zmm accumulators 滑动窗口爆破。

## 攻击链

1. sloth_root: 1277 次 x^2 % (2^1279-1) + 翻转 LSB, difficulty=7337
2. Mersenne 模运算: (x & p) + (x >> 1279), if r >= p: r -= p
3. GMP 实现: mpz_mul + mpz_mod_2exp(low) + mpz_fdiv_q_2exp(high) + mpz_add
4. GMP Rust 2.4 秒 vs C++ 略快
5. AVX-512 IFMA: vpmadd52luq 52-bit multiply-add
6. 25 个 52-bit limbs (1279/52 ≈ 24.6)
7. 7 个 __m512i accumulators, 滑动窗口 i ∈ [-7, 24]
8. _mm512_mask_madd52lo_epu64 + _mm512_mask_madd52hi_epu64
9. carry 处理: 4 段 accum, carry = srli 52, carry_into = alignr_epi64
10. 测试 cmp = bit_1279 检查 >= 2^1279-1

## 关键 payload

```
sloth_root difficulty=7337 / Mersenne 2^1279-1 / mpz_mod_mersenne / AVX-512 IFMA vpmadd52luq / 25 52-bit limbs / 7 accumulators 滑动窗口 / carry2 循环
```

## 经验教训

kCTF PoW 是 Memory-hard 算法 (Mersenne 模乘),AVX-512 IFMA 52-bit 乘加是加速核心;滑动窗口 + carry propagation 是大数乘法模板。

## 标签

kCTF PoW、Mersenne 2^1279-1、1277平方、7337迭代、GMP、mpz_mul + mpz_mod_2exp、AVX-512 IFMA、vpmadd52luq、vpmadd52huq、25个52-bit limbs、_mm512_mask_madd52lo_epu64、_mm512_madd52hi_epu64、$21、337 base + $10、000 stability + $20、000 0-day

## 参考来源

- https://www.ctfiot.com/255114.html
- 原文件：Beating_the_kCTF_PoW_with_AVX512IFMA_for_$51k.full.md

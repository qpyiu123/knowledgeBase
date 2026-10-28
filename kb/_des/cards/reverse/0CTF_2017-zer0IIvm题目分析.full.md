---
title: "0CTF 2017 - zer0IIvm 题目分析"
category: reverse
tags: ["0CTF 2017", "reverse", "LLVM", "obfuscation", "OLLVM", "AES"]
signals: ["0CTF 2017 2017", "LLVM", "obfuscation", "OLLVM", "AES", "SBox", "MixColumns", "CRC32爆破", "key-recovery", "reverse", "crypto_rsa", "flatten", "AES-like", "scramble"]
difficulty: insane
source: "https://www.ctfiot.com/44501.html"
tools: ["IDA", "OLLVM", "Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 0CTF 2017 - zer0IIvm 题目分析

> 赛事：0CTF 2017 2017 | 方向：reverse | 难度：insane | 工具：IDA、OLLVM、Sage

## 一句话总结

OLLVM flatten + AES-like scramble + CRC32 爆破前 3 字节 + GF(2) 线性方程恢复 PRNG seed

## 攻击链

1. IDA 看 main 是巨大的 switch state machine（OLLVM flatten 混淆）
2. 分析 lib0opsPass.so 找 Oops::CryptoUtils::prng_seed + scramble32
3. crc32('FTC0', &key, 3) == 0xF9E319A6 爆破前 3 字节 = 179, 197, 140
4. scramble32 = 4 轮 AES-like XorKey+SubBytes+MixColumn+XorKey
5. 用 AES_PRECOMP_TE[i](x) = MixColumns(SBox(x) << 8*i) 验证 = AES SBox
6. key 用于 scramble plains[65806] 数组
7. PRNG 是 8 位非线性 S-box TABLE + 线性 bit 累加，构造 GF(2) 线性系统
8. Sage 解 128×16 线性方程组 → 16 字节 seed

## 经验教训

LLVM 混淆插件常用 CryptoUtils 做 PRNG；GF(2) 线性化是把非线性 S 盒转成线性系统求密钥的经典方法

## 标签

LLVM、obfuscation、OLLVM、AES、SBox、MixColumns、CRC32爆破、key-recovery、GF(2)-linear、sage、AES_PRECOMP_TE、PRNG

## 参考来源

- https://www.ctfiot.com/44501.html
- 原文件：0CTF_2017-zer0IIvm题目分析.full.md

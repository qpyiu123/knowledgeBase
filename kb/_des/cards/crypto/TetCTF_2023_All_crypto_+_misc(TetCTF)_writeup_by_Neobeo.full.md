---
title: "TetCTF 2023 All crypto + misc writeup by Neobeo"
category: crypto
tags: ["TetCTF", "crypto", "negative-amount", "biased-bits", "lll-attack-ecdsa", "weak-entropy-3n"]
signals: ["TetCTF 2023", "negative-amount", "biased-bits", "lll-attack-ecdsa", "weak-entropy-3n", "aes-cbc-bitflip-json", "sqli-postgres", "crypto_rsa", "TetCTF", "Neobeo", "biased", "PRNG", "byte", "nonce"]
difficulty: hard
source: "https://www.ctfiot.com/89718.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TetCTF 2023 All crypto + misc writeup by Neobeo

> 赛事：TetCTF 2023 | 方向：crypto | 难度：hard

## 一句话总结

TetCTF 2023 Neobeo 综合：负数赌场 + biased PRNG + 1-byte nonce ECDSA LLL + AES-CBC 位翻 LLL + PostgreSQL SQLi。

## 攻击链

1. Casino 注册 + Bet 负数 -10^100 拿无限余额
2. ShowBalanceWithProof 拿 Balance + Proof
3. FlagSeller PrintFlag 拿 flag: TetCTF{fr0m_n3g4t1v3n3ss_t0_b4nkruptcy}
4. biased PRNG seed(2023) + 多次 random.shuffle 恢复
5. 7dfdf6e...baf3c1 29 行 37 字节 hex: 1 bit/行 + 跨 37*8 shuffle
6. Counter bits + majority voting: bit 出现 > len/2 次 → 1
7. TetCTF{fr0m_buggy_sw4p_t0_r4nd0m_b14s!}
8. 64 签名 ECDSA 弱 nonce: nonce = 1 byte (256 个候选)
9. LLL reduce matrix 24 bit = 256 (248 候选)
10. 64 sigs 矩阵 BKZ 还原私钥 1 byte
11. 验证 (m + r*k) * s^-1 * G == r 即正确 key
12. key 8JPNOogLTn8CPhlHzCkrywaSJciX5ygSkOff3P+kRes= → flag{TetCTF{0n3_byt3_0v3rfl0w_l34ds_t0_full_pr1v4t3_k3y_r3c0v3r}}
13. Toy 加密 AES-CBC + key+iv 硬编码
14. 位翻 + JSON 模 n 整除
15. 1529 inputs 二分位爆破 + LLL
16. Web: AES-CBC + jwt 伪造 + PostgreSQL INSERT INTO orders (image) VALUES (''/flag'') SQL 注入
17. TetCTF{R_u_4_f0rm3r_d3v_0f_th3_c0mp4ny?}

## 关键 payload

```
{"Command":"Bet","Amount":-10**100}
```

## 经验教训

整数溢出 (int 类型足够大) + 弱 PRNG 种子 (seed=2023) + 1 字节 ECDSA nonce (256^2 候选) 三个经典漏洞组合。

## 标签

negative-amount、biased-bits、lll-attack-ecdsa、weak-entropy-3n、aes-cbc-bitflip-json、sqli-postgres

## 参考来源

- https://www.ctfiot.com/89718.html
- 原文件：TetCTF_2023_All_crypto_+_misc(TetCTF)_writeup_by_Neobeo.full.md

---
title: "Google CTF 2023 Writeup by Venom"
category: misc
tags: ["Google CTF 2023", "misc", "PWN_UBF", "PWN_WFW1", "PWN_WFW2字节级爆破", "PWN_WFW3_libc"]
signals: ["Google CTF 2023 2023", "PWN_UBF", "PWN_WFW1", "PWN_WFW2字节级爆破", "PWN_WFW3_libc", "PWN_gradebook", "LCG_公钥恢复", "RSA_Multi_prime", "Lattice_格_爆破", "misc_unknown", "Google", "CTF", "VP-Union", "PWN"]
difficulty: hard
source: "https://www.ctfiot.com/122434.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Google CTF 2023 Writeup by Venom

> 赛事：Google CTF 2023 2023 | 方向：misc | 难度：hard

## 一句话总结

Google CTF 2023 VP-Union 综合：5 道 PWN + LCG 多素数 RSA + ECDH TLS。

## 攻击链

1. UBF (Underflow Bug Fix): corrupt booleans fix + base64 payload
2. WFW1: image_addr + 0x21e0 + 80 字节读
3. WFW2: 字节级爆破 flag 字符
4. WFW3: libc 地址泄漏 + 多个 0x... + p32(1337) 控制
5. gradebook: stack 泄漏 + file write 攻击 + add_grade 覆写返回地址
6. LCG: 6 个状态输出还原 a,b,n, 爆破 seed 生成 512-bit 素数
7. 多个 512-bit 素数 RSA + 爆破中末 5 字符
8. ECDH TLS: CA 证书 + 客户端证书 + ECDH 协商 + HKDF 派生 + HMAC
9. CTF{C0nGr@tz_RiV35t_5h4MiR_nD_Ad13MaN_W0ulD_b_h@pPy}
10. CTF{w0W_c0Nt1nUed_fr4Ct10ns_suR3_Ar3_fUn_Huh}

## 关键 payload

```
LCG 状态差分 + a,b,n 还原 + 多素数 RSA + 已知明文爆破
```

## 经验教训

LCG 6 组输出可还原 a,b,n；多素数 RSA 用 LCG 状态生成；ECDH TLS 协商需要 CA + 客户端证书。

## 标签

PWN_UBF、PWN_WFW1、PWN_WFW2字节级爆破、PWN_WFW3_libc、PWN_gradebook、LCG_公钥恢复、RSA_Multi_prime、Lattice_格_爆破、ECDH_TLS、VP-Union

## 参考来源

- https://www.ctfiot.com/122434.html
- 原文件：Google_CTF_2023_Writeup_by_Venom.full.md

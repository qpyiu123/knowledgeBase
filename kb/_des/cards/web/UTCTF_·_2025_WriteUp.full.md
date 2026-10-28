---
title: "UTCTF 2025 WriteUp (狼组)"
category: web
tags: ["UTCTF 2025", "web", "otp_blast", "game_elo_spoof", "rop_read_open", "ssh_acl"]
signals: ["UTCTF 2025 2025", "otp_blast", "game_elo_spoof", "rop_read_open", "ssh_acl", "qr_bitstring", "ostrich_algorithm", "cookie_clicker_ce", "vm_64k", "rop", "UTCTF", "Web", "Game", "Pwn"]
difficulty: medium
source: "https://www.ctfiot.com/232193.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UTCTF 2025 WriteUp (狼组)

> 赛事：UTCTF 2025 2025 | 方向：web | 难度：medium | 工具：ROP

## 一句话总结

狼组出品的 UTCTF 2025 全 11 题解，覆盖 Web/Game/Pwn/Misc/Reverse/Crypto 全部题型，详细到脚本可直接复用。

## 攻击链

1. OTP:注册 username+lookup secret 差值最小爆破 32 位 flag → Number Champion:lat/lon 二分定位 geopy 训练地址 (3000 elo) → secbof:ROP 链 (read→bss, open, read→bss+0x300, write→stdout) → Trapped 1/2:ssh 进去 flag 启 ACL 扩展+secretuser 读 → Streamified:25x25 bitstring 还原 QR → Ostrich:跳过开环循环即得 → Retro Cookie Clicker:CE 搜索单字节找 Dozen=0x7fff → Safe Word:malloc 巨型内存初始化+char-pick VM 解释器+0xC358XX6A 验证 → DCΔ:n=p² → RSA:e=3 小明文攻击 → Autokey:已知 flag 头 utflag{ 推 key

## 关键 payload

```
utflag{On3_sT3P_4t_4_t1m3} / utflag{1059-s-high-st-columbus-43206} / pl = b'A'*(0x80+8) + flat([rdi_ret,0,rsi_ret,bss+0x200,rdx_rbx_ret,0x100,0,read,...])
```

## 经验教训

鸵鸟算法"在 CTF 里指绕过潜在复杂检查的策略；很多题目 reverse 关键不是"逆向"而是"识别它不检查什么"。

## 标签

otp_blast、game_elo_spoof、rop_read_open、ssh_acl、qr_bitstring、ostrich_algorithm、cookie_clicker_ce、vm_64k、rsa_p_square、rsa_e3、autokey_cipher、friendly_intro

## 参考来源

- https://www.ctfiot.com/232193.html
- 原文件：UTCTF_·_2025_WriteUp.full.md

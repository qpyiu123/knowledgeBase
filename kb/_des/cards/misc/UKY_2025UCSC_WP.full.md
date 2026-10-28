---
title: "UKY 2025 UCSC WP"
category: misc
tags: ["UKY 2025 UCSC 高校赛", "misc", "stego", "blind_watermark", "base64_morse", "usb_hid"]
signals: ["UKY 2025 UCSC 高校赛 2025", "stego", "blind_watermark", "base64_morse", "usb_hid", "fmt_string", "rand_seed", "io_leak", "house_of_apple", "UKY", "UCSC", "Misc", "pwn", "crypto"]
difficulty: medium
source: "https://www.ctfiot.com/244129.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKY 2025 UCSC WP

> 赛事：UKY 2025 UCSC 高校赛 2025 | 方向：misc | 难度：medium

## 一句话总结

UKY 战队 UCSC 赛 8 小时 4 题全解+Misc 全收，覆盖 3 路 stego、3 道 pwn、4 道 re、4 道 crypto 完整链。

## 攻击链

1. 小套不是套:QR+伪加密 PNG 拼回+明文攻击 → three-ucs:BlindWatermark 8f02d3e7+二进制 0100→base64→morse -ce89-4d6b-830e+pcapng thinkbell 解密 5d0cb5695077 → Userlogin:supersecureuser fmt-string 两次利用 %9$hn 写 ret → BoFido:name 覆盖 rand 种子为 0 → 疯狂复制:edit(-4) 改 _IO_2_1_stdout 走 house of apple2 → easy_re:data[i]^10 → simplere:魔改 UPX+逆 base58 变表 → EZ_debug:RC4 动调 → re_ez:BFS 找 5,5,5,1,1,-5,-5,-5 路径+md5 → XR4:RC4 decrypt+random.seed() → essential-ucsc:RSA p,q 邻近+iroot → MERGE_ECC:ECC Pohlig-Hellman+Smart's attack → Ez_Calculate:背包+RSA+Rabin

## 关键 payload

```
flag{8f02d3e7-ce89-4d6b-830e-5d0cb5695077} / b'%10$p'+b'%{shell}c%9$hn' / flat({0:b'  sh', 0x8:p64(0), 0x10:p64(1), 0x18:p64(2)}) → system
```

## 经验教训

高校赛题的"组合技"是常态：XR4=RC4+random seed；MERGE_ECC=爆破+Smart's attack；Ez_Calculate=背包+RSA+Rabin 一题三杀。

## 标签

stego、blind_watermark、base64_morse、usb_hid、fmt_string、rand_seed、io_leak、house_of_apple、xor、base58_modify、rc4、rsa_close_prime、smart_attack_ecc、rabin、knapsack、bfs_md5

## 参考来源

- https://www.ctfiot.com/244129.html
- 原文件：UKY_2025UCSC_WP.full.md

---
title: "Hackvent 2022 Hard 全套"
category: reverse
tags: ["Hackvent 2022", "reverse", "ADCP", "base64", "haystack", "QR"]
signals: ["Hackvent 2022 2022", "ADCP", "base64", "haystack", "QR", "pyzbar", "zip2john", "hashcat", "AES-ECB", "reverse", "stego_image", "block_cipher", "pwn_unknown", "Hard"]
difficulty: hard
source: "https://www.ctfiot.com/89723.html"
tools: ["hashcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hackvent 2022 Hard 全套

> 赛事：Hackvent 2022 2022 | 方向：reverse | 难度：hard | 工具：hashcat

## 一句话总结

五题 Hard 覆盖频谱/图像/密码/AES/pwn

## 攻击链

1. 解析 ADCP 频谱找 base64 flag
2. 切 24800x24800 PNG 网格 pyzbar 扫 QR
3. PBKDF2-HMAC zip 碰撞爆破前缀密码
4. AES-ECB 字节翻转 oracle 解 flag
5. UAF + heap 控制写 present 指针

## 关键 payload

```
HV22{v-wish-v-g0t-b33r} / HV22{1'm_y0ur_need13.} / HV22{HAVING_FUN_WITH_CHOSEN_PREFIX_PBKDF2_HMAC_COLLISIONS_nzvwuj} / HV22{len()!=len()} / NOPELOS (ASCII art flag)
```

## 经验教训

PBKDF2-HMAC 已知末段可前缀爆破；AES-ECB 配合可控前缀可逐字节 oracle；UAF 后用未清空指针覆盖堆块写任意地址

## 标签

ADCP、base64、haystack、QR、pyzbar、zip2john、hashcat、AES-ECB、bytewise、heap-exploit、UAF

## 参考来源

- https://www.ctfiot.com/89723.html
- 原文件：Hackvent_2022_–_Hard.full.md

---
title: "1337UP LIVE CTF WriteUp"
category: misc
tags: ["1337UP LIVE CTF 2023", "misc", "Intigriti", "jpg-zip-concat", "stegsolve", "sha256-crack"]
signals: ["1337UP LIVE CTF 2023 2023", "Intigriti", "jpg-zip-concat", "stegsolve", "sha256-crack", "X-Forwarded-For", "BioCorp", "XOR-reversible", "wifi-pcap", "stego_image", "sqli", "lfi", "web_unknown", "LIVE"]
difficulty: medium
source: "https://www.ctfiot.com/216053.html"
tools: ["PHP", "Stegsolve"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 1337UP LIVE CTF WriteUp

> 赛事：1337UP LIVE CTF 2023 2023 | 方向：misc | 难度：medium | 工具：PHP、Stegsolve

## 一句话总结

1337UP LIVE CTF 8 大题：sanity + stego + XOR + web + bio + wifi + esolang

## 攻击链

1. Q1 Sanity Check: 直接看题面 INTIGRITI{1f_y0u_l34v3_7h3_fl46_w1ll_b3_r3v0k3d}
2. Q2 In Plain Sight: jpg 尾接 zip（FFD9 + 504B 中间是 zip），解压后 stegsolve 出 flag
3. Q3 Socials: Twitter h0p3_y0u + youtube _3nj0y_ + reddit d4_c7f → INTIGRITI{h0p3_y0u_3nj0y_d4_c7f}
4. Q4 irrOReversible: 按位或运算 → 传 256 个 x00 还原 → INTIGRITI{b451c_x0r_wh47?}
5. Q5 Pizza Paradise: robots.txt → js 登录 sha256 爆破 → 任意文件读
6. Q6 BioCorp: PHP $_SERVER 超全局 → X-Forwarded-For / X-Biocorp-VPN 等头变 HTTP_* 访问内部资源
7. Q7 Knight: 两层 knight escargot esolang → INTIGRITI{}
8. Q8 WIFI: pcap 解 WPA2 → 拿 SSID/密码

## 关键 payload

```
INTIGRITI{1f_y0u_l34v3_7h3_fl46_w1ll_b3_r3v0k3d}
```

## 经验教训

jpg 后接 zip 是经典 MISC 套路；XOR 全 0 还原是 reverse 入门；escargot esolang 是字符画

## 标签

Intigriti、jpg-zip-concat、stegsolve、sha256-crack、X-Forwarded-For、BioCorp、XOR-reversible、wifi-pcap、knight-knight、escargot-esolang

## 参考来源

- https://www.ctfiot.com/216053.html
- 原文件：1337UP_LIVE_CTF_WriteUp.full.md

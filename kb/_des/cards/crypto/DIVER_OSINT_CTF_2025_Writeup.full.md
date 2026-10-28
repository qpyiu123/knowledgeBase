---
title: "DIVER OSINT CTF 2025 Writeup"
category: crypto
tags: ["DIVER", "crypto", "osint", "ndl", "opendata", "japan-internment"]
signals: ["DIVER 2025", "osint", "ndl", "opendata", "japan-internment", "flightradar", "google-earth", "sentinel-2", "korea-hotel", "misc_math", "DIVER", "OSINT", "CTF", "CLACKER"]
difficulty: medium
source: "https://www.ctfiot.com/255111.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DIVER OSINT CTF 2025 Writeup

> 赛事：DIVER 2025 | 方向：crypto | 难度：medium

## 一句话总结

DIVER OSINT CTF 2025 复盘，作者 CLACKER 前田。

## 攻击链

1. internment: 藤井富太郎木曜島真珠採り → ヘイ収容所 → Rushworth Camp 4
2. 澳大利亚开放数据库 + 官方记录
3. hole: 山西大同市 CM 拍摄
4. Sentinel-2 2024-08-27 卫星图找 霊丘県
5. elevator: 客室内 + 窗外景色 → 韩国東横イン
6. 特征外灯定位
7. 韩国电梯故障数据库

## 关键 payload

```
メタ読み（metadata reading）+ Sentinel-2 卫星图
```

## 经验教训

当 solve 数少的 hard 题，通过"问题描述的 solve 数"反推真实难度（メタ読み）。

## 标签

osint、ndl、opendata、japan-internment、flightradar、google-earth、sentinel-2、korea-hotel、elevator-db

## 参考来源

- https://www.ctfiot.com/255111.html
- 原文件：DIVER_OSINT_CTF_2025_Writeup.full.md

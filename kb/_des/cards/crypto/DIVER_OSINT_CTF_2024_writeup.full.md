---
title: "DIVER OSINT CTF 2024 writeup"
category: crypto
tags: ["DIVER", "crypto", "osint", "gmail", "google-maps", "twitter"]
signals: ["DIVER 2024", "osint", "gmail", "google-maps", "twitter", "openstreetmap", "flightradar", "address", "misc_math", "DIVER", "OSINT", "CTF", "ad_directiare", "Google"]
difficulty: medium
source: "https://www.ctfiot.com/187577.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DIVER OSINT CTF 2024 writeup

> 赛事：DIVER 2024 | 方向：crypto | 难度：medium

## 一句话总结

DIVER OSINT CTF 2024 复盘，日文 + 中文双语 WP 5 题。

## 攻击链

1. ad_directiare: gmail osint + Google Maps 评论找午餐价 4400
2. osprey1: 推特搜"屋久島 オスプレイ コールサイン"得 12-0065_GUNDAM22
3. osprey2: 推文定位 16:46 武士健身中心 OpenStreetMap Way 810021666
4. chiban: 饺子满洲+サンディ双葉店+地番検索くん → 筆界未定地-6
5. italy: 飞行数据网站搜 10/27 → I-LIDI Alidaunia 13:45:46 1600

## 关键 payload

```
Gmail/Google Maps + 推特 + OpenStreetMap + FlightRadar24
```

## 经验教训

OSINT 题的关键工具是 Gmail/Google Maps/推特/OpenStreetMap/FlightRadar24 五件套。

## 标签

osint、gmail、google-maps、twitter、openstreetmap、flightradar、address

## 参考来源

- https://www.ctfiot.com/187577.html
- 原文件：DIVER_OSINT_CTF_2024_writeup.full.md

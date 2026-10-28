---
title: "TUCTF 2024 Writeup"
category: misc
tags: ["TUCTF", "misc", "rot13", "custom-image-format", "crc8-checksum", "wifi-aircrack"]
signals: ["TUCTF 2024", "rot13", "custom-image-format", "crc8-checksum", "wifi-aircrack", "embrava-bello", "misc_unknown", "TUCTF", "TIMG", "WiFi", "aircrack", "reingvbaonetr", "chr", "ord"]
difficulty: easy
source: "https://www.ctfiot.com/226943.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TUCTF 2024 Writeup

> 赛事：TUCTF 2024 | 方向：misc | 难度：easy

## 一句话总结

TUCTF 2024 4 题：rot13 + TIMG 自定义图像格式 + WiFi aircrack 爆破。

## 攻击链

1. S = "reingvbaonetr" 字符 chr(ord(s) - 0x61 + 0x54) = rot13
2. TU Image Program: 自定义 TIMG 格式 (4 byte header + width/height + RUBY tag)
3. 三通道 DATR/DATG/DATB + 每行 crc8 校验和
4. img.getpixel([j,i])[0] R 通道
5. timg_to_jpg 解码脚本：struct.unpack('>I', data[8:12]) width
6. airodump-ng + aircrack-ng 爆破 WiFi (D8:3A:DD:07:AA:5A)
7. aircrack-ng -w /usr/share/wordlists/rockyou.txt

## 关键 payload

```
rot13("reingvbaonetr")
```

## 经验教训

rot13 加密的字符串仅偏移 0x54 位 (chr(ord(c) - 0x61 + 0x54))；自研图像格式常带 crc8 行校验。

## 标签

rot13、custom-image-format、crc8-checksum、wifi-aircrack、embrava-bello

## 参考来源

- https://www.ctfiot.com/226943.html
- 原文件：TUCTF_2024_Writeup.full.md

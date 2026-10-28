---
title: "DEFCON ガジェット① Aerospace Village Badge"
category: misc
tags: ["DEFCON", "misc", "badge", "hardware", "wifi", "base64"]
signals: ["DEFCON 2023", "badge", "hardware", "wifi", "base64", "moongoku", "ipv4", "sao", "misc_unknown", "DEFCON", "Aerospace", "Village", "Badge", "Base64"]
difficulty: easy
source: "https://www.ctfiot.com/130703.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DEFCON ガジェット① Aerospace Village Badge

> 赛事：DEFCON 2023 | 方向：misc | 难度：easy

## 一句话总结

DEFCON Aerospace Village Badge 硬件解谜，刻印 Base64 当 Wifi 密码。

## 攻击链

1. 看 Badge 边缘的刻印 MVNtYWxsU3RlcA==
2. Base64 解码得 1SmallStep
3. 当 Wifi 密码连 WrightStuff AP
4. 看另一侧"First moonwalk data as ipv4
5. 解 IPv4 数据包
6. 莱特兄弟 / James Webb SAO

## 关键 payload

```
物理 Base64 刻印 + Wifi 密码
```

## 经验教训

硬件 Badge 谜题第一步永远看边缘/背面刻印 + 物理连接器。

## 标签

badge、hardware、wifi、base64、moongoku、ipv4、sao

## 参考来源

- https://www.ctfiot.com/130703.html
- 原文件：DEFCONガジェット①_Aerospace_Village_Badge.full.md

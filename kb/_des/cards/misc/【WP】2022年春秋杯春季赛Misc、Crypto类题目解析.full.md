---
title: "【WP】2022年春秋杯春季赛 Misc、Crypto 类题目解析"
category: misc
tags: ["春秋杯", "misc", "CRC-stego", "IDAT-10000-blocks", "vera-crypt", "winhex-recover"]
signals: ["春秋杯 2022", "CRC-stego", "IDAT-10000-blocks", "vera-crypt", "winhex-recover", "ICMP-data-len", "IP-38-39-binary", "PDF-reorder", "capture-radiate", "reverse", "Misc", "Crypto", "CRC", "VeraCrypt"]
difficulty: medium
source: "https://www.ctfiot.com/51678.html"
tools: ["tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2022年春秋杯春季赛 Misc、Crypto 类题目解析

> 赛事：春秋杯 2022 | 方向：misc | 难度：medium | 工具：tshark

## 一句话总结

2022 春秋杯春季赛 Misc/Crypto 4 题 WP，CRC 隐写 + VeraCrypt 爆破 + ICMP 流量恢复 zip + IP 末位编码。

## 攻击链

1. 签到 关注公众号 + 音谱点击/Capture Radiate Chart alien.png 10000+ IDAT 块 CRC 最后一字节藏 RAR/RecoverMe VeraCrypt 密码本爆破 aaaAAA111 + winhex 恢复挂载盘 + secret.pcapng ICMP data.len 拼 zip 头 50 4B 03 04 + tshark 提取 IP 38/39 编码二进制 = 压缩包密码

## 关键 payload

```
春秋伽玛公众号"上课铃声"  VeraCrypt 密码 aaaAAA111  IP 末位 38/39 → 0/1
```

## 经验教训

PNG IDAT 10000+ 块且 CRC 不正常是 CRC 隐写标志；VeraCrypt 密码本爆破可让 passware kit 跑 10 分钟；ICMP data.len 字段可编码文件内容；IP 末位 38/39 二值编码是隐蔽通道。

## 标签

CRC-stego、IDAT-10000-blocks、vera-crypt、winhex-recover、ICMP-data-len、IP-38-39-binary、PDF-reorder、capture-radiate

## 参考来源

- https://www.ctfiot.com/51678.html
- 原文件：【WP】2022年春秋杯春季赛Misc、Crypto类题目解析.full.md

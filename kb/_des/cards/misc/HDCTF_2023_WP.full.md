---
title: "HDCTF 2023 WP"
category: misc
tags: ["HDCTF 2023", "misc", "stego", "zsteg", "base64", "zip-crc"]
signals: ["HDCTF 2023 2023", "stego", "zsteg", "base64", "zip-crc", "rockyou", "bkcrack", "分卷压缩", "png-height", "misc_unknown", "HDCTF", "MISC", "zip", "CRC"]
difficulty: medium
source: "https://www.ctfiot.com/111656.html"
tools: ["zsteg"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HDCTF 2023 WP

> 赛事：HDCTF 2023 2023 | 方向：misc | 难度：medium | 工具：zsteg

## 一句话总结

HDCTF 2023 3道MISC：zsteg+zip CRC爆破+分卷flag

## 攻击链

1. hardMisc: zsteg得到数据解base64
2. flag: HDCTF{wE1c0w3_10_HDctf_M15c}
3. ExtremeMisc: IDAT.png文件尾分离zip
4. Dic.zip用rockyou字典爆破
5. Reverse.piz字节倒序: int(((''%02x''%i)[::-1],16)).to_bytes(1,''little'')
6. bkcrack明文攻击
7. MasterMisc: 分卷压缩爆破
8. topic.png后有png+wav+png
9. 改png高度得第二段flag
10. flag: NSSCTF{e67d8104-7536-4433-bfff-96759901c405}

## 关键 payload

```
HDCTF{wE1c0w3_10_HDctf_M15c}
```

## 经验教训

zip CRC爆破+明文攻击(bkcrack)组合解分段压缩

## 标签

stego、zsteg、base64、zip-crc、rockyou、bkcrack、分卷压缩、png-height、wav

## 参考来源

- https://www.ctfiot.com/111656.html
- 原文件：HDCTF_2023_WP.full.md

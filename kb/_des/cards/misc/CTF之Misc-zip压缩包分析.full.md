---
title: "CTF 之 Misc - zip 压缩包分析"
category: misc
tags: ["Misc CTF", "misc", "zip结构", "文件头 50 4B 03 04", "目录头 50 4B 01 02", "结束符 50 4B 05 06"]
signals: ["Misc CTF 2022", "zip结构", "文件头 50 4B 03 04", "目录头 50 4B 01 02", "结束符 50 4B 05 06", "伪加密 1400XX0008", "fcrackzip暴力破解", "CRC32爆破", "5字符", "misc_unknown", "CTF", "Misc", "zip", "XX0008"]
difficulty: easy
source: "https://www.ctfiot.com/75389.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 之 Misc - zip 压缩包分析

> 赛事：Misc CTF 2022 | 方向：misc | 难度：easy

## 一句话总结

CTF Misc zip 压缩包分析 — 伪加密 (1400XX0008 改 9) + fcrackzip 暴力破解 + CRC32 5 字符爆破 + 明文攻击 (hex 对比) + linux/windows 换行符 0A vs 0D0A 差异。

## 攻击链

1. zip 3 部分: 数据区 + 目录区 + 结束符
2. 文件头 50 4B 03 04, 目录 50 4B 01 02, 结束 50 4B 05 06
3. 伪加密: 目录文件标记后 4 字节 1400XX0008, XX 改 9 → 伪加密, 改 0 还原
4. 暴力破解: fcrackzip -b -l 6-6 -c 1 -p 000000 passwd.zip
5. CRC32 爆破: 5 字符全字典 ascii_letters + _ + 0-9
6. 明文攻击: 已知文件 ZIP 加密后, 对比 hex 找 3 个 key
7. linux 0A vs windows 0D0A 换行符差异

## 关键 payload

```
zip 文件头 50 4B 03 04 / 目录 50 4B 01 02 / 伪加密 1400XX0008 / fcrackzip -b -l 6-6 -c 1 / CRC32 5 字符爆破 / 明文攻击 hex 对比 / linux 0A vs windows 0D0A
```

## 经验教训

zip 伪加密是改目录 14 00 XX 00 08 中 XX 第 1 位 (0/1 切换);CRC32 爆破只适合 ≤5 字符;明文攻击需已知明文 + 相同压缩算法。

## 标签

zip结构、文件头 50 4B 03 04、目录头 50 4B 01 02、结束符 50 4B 05 06、伪加密 1400XX0008、fcrackzip暴力破解、CRC32爆破、5字符、明文攻击、ARCHPR、看雪 wx_酸菜鱼

## 参考来源

- https://www.ctfiot.com/75389.html
- 原文件：CTF之Misc-zip压缩包分析.full.md

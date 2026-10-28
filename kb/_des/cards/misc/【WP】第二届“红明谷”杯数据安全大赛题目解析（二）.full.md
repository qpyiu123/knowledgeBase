---
title: "【WP】第二届\"红明谷\"杯数据安全大赛题目解析（二）"
category: misc
tags: ["红明谷", "misc", "SM2-Biased-nonce-attack", "HNP-lattice", "DPAPI-blob", "Master-Key"]
signals: ["红明谷 2022", "SM2-Biased-nonce-attack", "HNP-lattice", "DPAPI-blob", "Master-Key", "volatility-imageinfo", "hashdump-getsids", "mftparser", "CVE-2022", "forensic_memory", "SM2", "biased", "nonce", "DPAPI"]
difficulty: hard
source: "https://www.ctfiot.com/32512.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第二届"红明谷"杯数据安全大赛题目解析（二）

> 赛事：红明谷 2022 | 方向：misc | 难度：hard

## 一句话总结

第二届红明谷杯题解（二），SM2 biased nonce 攻击 + DPAPI masterkey/blob 内存取证解密。

## 攻击链

1. 1. SM2: nonce 前 6 bits 永远 0 + 构造 HNP 格子解密钥 /2. MissingFile: volatility imageinfo + filescan + mftparser + hivelist + hashdump + getsids + dpapi masterkey 解 + dpapi blob 解得 flag{Hide_Behind_Windows}

## 关键 payload

```
dpapi masterkey  SID=S-1-5-21-206512979-2006505507-2644814589-1001  password=123456  flag{Hide_Behind_Windows}
```

## 经验教训

SM2 nonce 偏差攻击用 HNP (Hidden Number Problem) 构造 LLL 格；DPAPI Master Key 用用户密码 + SID + 16 字节随机数加密；volatility mftparser + hivelist + hashdump 是 Windows 内存取证三件套。

## 标签

SM2-Biased-nonce-attack、HNP-lattice、DPAPI-blob、Master-Key、volatility-imageinfo、hashdump-getsids、mftparser、CVE-2022

## 参考来源

- https://www.ctfiot.com/32512.html
- 原文件：【WP】第二届“红明谷”杯数据安全大赛题目解析（二）.full.md

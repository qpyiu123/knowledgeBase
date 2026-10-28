---
title: "2022 第六届强网杯青少赛 Misc & Crypto WriteUp"
category: crypto
tags: ["强网杯青少赛 2022", "crypto", "base64", "奇偶分离", "异或32", "大小写偏移"]
signals: ["强网杯青少赛 2022 2022", "base64", "奇偶分离", "异或32", "大小写偏移", "NGC660安全实验室", "入门", "crypto_oracle", "Base64", "XOR", "chuyinweilai", "png", "decode", "zfill"]
difficulty: easy
source: "https://www.ctfiot.com/71039.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 第六届强网杯青少赛 Misc & Crypto WriteUp

> 赛事：强网杯青少赛 2022 2022 | 方向：crypto | 难度：easy

## 一句话总结

入门：Base64 + 字节奇偶互换 + XOR 32 + 大小写 -31/-32 偏移。

## 攻击链

1. 读 chuyinweilai.png 文件 Base64 decode
2. 字节奇偶分离交换 + zfill(2) 重组 PNG
3. XOR 32 还原 FLAG[vxpsDqCElwwoClsoColwpuvlqFvvFrpopBss]
4. 大写字母 -31 / 小写字母 -32 解密
5. 大写字母 -32 解密反向偏移

## 关键 payload

```
cryher = "FLAG[vxpsDqCElwwoClsoColwpuvlqFvvFrpopBss]"; res = chr(ord(i)^32)
```

## 经验教训

PNG 字节奇偶互换 + zfill(2) 重组是常见 stego 套路；大小写偏移 -31/-32 区分大小写。

## 标签

base64、奇偶分离、异或32、大小写偏移、NGC660安全实验室、入门

## 参考来源

- https://www.ctfiot.com/71039.html
- 原文件：2022第六届强网杯青少赛_Misc&Crypto-WriteUp.full.md

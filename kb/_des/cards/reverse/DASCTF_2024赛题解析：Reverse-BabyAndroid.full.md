---
title: "DASCTF 2024 赛题解析：Reverse - BabyAndroid"
category: reverse
tags: ["DASCTF", "reverse", "android", "jni", "rc4", "custom-hash"]
signals: ["DASCTF 2024", "android", "jni", "rc4", "custom-hash", "aes-ecb", "in-memory-dex", "dct", "reverse", "DASCTF", "BabyAndroid", "Android", "JNI", "RC4"]
difficulty: medium
source: "https://www.ctfiot.com/197671.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2024 赛题解析：Reverse - BabyAndroid

> 赛事：DASCTF 2024 | 方向：reverse | 难度：medium

## 一句话总结

DASCTF 2024 BabyAndroid：Android JNI + RC4 + InMemoryDexClassLoader + AES/ECB + DCT 浮点加密。

## 攻击链

1. loadData 读 assets/Sex.jpg (RC4 key="DASCTF")
2. InMemoryDexClassLoader 加载 dex
3. 反射 site.qifen.note.ui.Encrypto.encrypt
4. 自定义 hash 派生 AES 16 字节 key
5. AES/ECB/PKCS5Padding 加密
6. native JNI encrypt 走 IDCT
7. DCT 浮点 29 维
8. 逆 IDCT 还原

## 关键 payload

```
RC4 解 dex + 自定义 hash 派生 AES + IDCT 浮点变换
```

## 经验教训

Android 逆向链：assets RC4 → InMemoryDexClassLoader → 反射调用 → 自定义 hash 派生 → AES → native JNI 二次变换。

## 标签

android、jni、rc4、custom-hash、aes-ecb、in-memory-dex、dct

## 参考来源

- https://www.ctfiot.com/197671.html
- 原文件：DASCTF_2024赛题解析：Reverse-BabyAndroid.full.md

---
title: "bi0sCTF 2024 Tallocator (未翻译)"
category: pwn
tags: ["bi0sCTF", "pwn", "android-native", "custom-allocator", "talloc", "jni"]
signals: ["bi0sCTF 2024", "android-native", "custom-allocator", "talloc", "jni", "anti-debug", "key-xor", "pwn_unknown", "bi0sCTF", "Android", "JNI", "Tallocator", "Java_bi0sctf_android_challenge_MainActivity_talloc", "mmap"]
difficulty: hard
source: "https://www.ctfiot.com/182577.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# bi0sCTF 2024 Tallocator (未翻译)

> 赛事：bi0sCTF 2024 | 方向：pwn | 难度：hard | 工具：Java

## 一句话总结

bi0sCTF 2024 Android JNI 自定义分配器 Tallocator 题，未翻译版本（中文 WP 暂未覆盖）。

## 攻击链

1. Java_bi0sctf_android_challenge_MainActivity_talloc 入口
2. 自定义分配器 mmap(0x41410000) + sbrk
3. is_talloc_inited 单次初始化
4. 调试器检测 v8 = v7[5] 调用
5. size 范围 0x150-0xFFF 走 sbrk_ed wilderness
6. 0x30 + 0xFC8 + 0x3A63 三个魔数
7. key = "50133tbd5mrt1769" XOR

## 关键 payload

```
自定义 talloc + anti-debug 回调 + wilderness 分配器
```

## 经验教训

Android 逆向链 = Java → JNI → native lib（libtallocator.so），必须结合三层。

## 标签

android-native、custom-allocator、talloc、jni、anti-debug、key-xor

## 参考来源

- https://www.ctfiot.com/182577.html
- 原文件：bi0sCTF_2024_Tallocator_（未翻译）.full.md

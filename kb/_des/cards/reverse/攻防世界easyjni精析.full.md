---
title: "攻防世界 easyjni 精析"
category: reverse
tags: ["攻防世界 (xctf)", "reverse", "APK", "JNI", "native", "base64"]
signals: ["攻防世界 (xctf) 2023", "APK", "JNI", "native", "base64", "自定义编码表", "swap", "字符交换", "看雪", "reverse", "crypto_oracle", "JADX", "Ghidra", "JNI_OnLoad"]
difficulty: medium
source: "https://www.ctfiot.com/97303.html"
tools: ["Ghidra"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 攻防世界 easyjni 精析

> 赛事：攻防世界 (xctf) 2023 | 方向：reverse | 难度：medium | 工具：Ghidra

## 一句话总结

自定义 base64 字母表 + JNI 字符串置换还原

## 攻击链

1. APK 反编译定位 JNI native 方法
2. JADX/Ghidra 打开 .so 看 JNI_OnLoad 注册函数
3. 识别自定义 base64 编码表 'i5jLW7S0GX6uf1cv3ny4q8es2Q+bdkYgKOIT/tAxUrFlVPzhmow9BHCMDpEaJRZN
4. 用 str.maketrans 映射回标准 base64 字母表
5. base64 解码得 flag 字符串
6. 看 so 函数：先做 16 字节字符表置换 (s1[i] = t_str[i+16])
7. 再做 32 字节相邻 swap 还原

## 关键 payload

```
str1.translate(str.maketrans(string1, string2)) → base64.b64decode
```

## 经验教训

native 层 base64 经常换字母表防识别；JNI_OnLoad 里 StringUTFChars 读入后做字符表 swap

## 标签

APK、JNI、native、base64、自定义编码表、swap、字符交换、看雪、xianxiong

## 参考来源

- https://www.ctfiot.com/97303.html
- 原文件：攻防世界easyjni精析.full.md

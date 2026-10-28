---
title: "解析2025强网拟态EZMiniAPP"
category: reverse
tags: ["强网拟态 2025 EZMiniAPP", "reverse", "wechat-mini-program", "wxapkg", "big-endian", "struct-unpack"]
signals: ["强网拟态 2025 EZMiniAPP 2025", "wechat-mini-program", "wxapkg", "big-endian", "struct-unpack", "XoR", "rotl", "enigmaticTransformation", "js-decompile", "reverse", "EZMiniAPP", "UTF-8", "XOR", "newKey2025"]
difficulty: medium
source: "https://www.ctfiot.com/278076.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态EZMiniAPP

> 赛事：强网拟态 2025 EZMiniAPP 2025 | 方向：reverse | 难度：medium

## 一句话总结

强网拟态2025 EZMiniAPP微信小程序逆向,wxapkg解包(二进制格式+大端索引+UTF-8文件名)+enigmaticTransformation加密函数+XOR/rotl逆运算推导+密钥newKey2025!。

## 攻击链

1. 微信小程序:__APP__.wxapkg文件
2. 二进制格式,包含JS代码+页面模板+样式表+配置文件
3. wxapkg文件结构:文件头+索引区+数据区
4. 解析:struct.unpack('B', data)解包1字节,struct.unpack('>I', data)解包4字节大端
5. 文件名:UTF-8编码
6. 加密函数:enigmaticTransformation(混淆名)
7. 密钥:newKey2025!
8. 预期密文:[1, 33, 194, 133, 195, 102, 232, 104, 200, 14, 8, 163, 131, 71, 68, 97, 2, 76, 72, 171, 74, 106, 225, 1, 65]
9. 异或:交换律/结合律/自反性A^B^B=A/恒等律A^0=A/归零律A^A=0
10. 循环左移(rotl)逆运算是循环右移(ror)
11. 异或的逆运算仍是异或
12. 解密:简化位运算表达式→识别算法类型(对称/非对称)→提取密钥→推导逆运算→实现解密

## 关键 payload

```
enigmaticTransformation + newKey2025!
```

## 经验教训

微信小程序逆向从__APP__.wxapkg开始,用unwxapkg/wxappUnpacker解包;JS代码混淆名(enigmaticTransformation)是常见模式;位运算加密(XOR/rotl)识别后逆运算就是它本身。

## 标签

wechat-mini-program、wxapkg、big-endian、struct-unpack、XoR、rotl、enigmaticTransformation、js-decompile、mobile-reverse、crypto-identification

## 参考来源

- https://www.ctfiot.com/278076.html
- 原文件：解析2025强网拟态EZMiniAPP.full.md

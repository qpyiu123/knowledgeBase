---
title: "逆向心法修炼之道 FLARE ON 9TH WRITEUP"
category: reverse
tags: ["FLARE ON 9th Challenge", "reverse", "FlareOn", "Mandiant", "mixed-mode-PE", ".NET-native"]
signals: ["FLARE ON 9th Challenge 2022", "FlareOn", "Mandiant", "mixed-mode-PE", ".NET-native", "capa", "floss", "PE32", "RC4", "reverse", "Flaredle", "Pixel", "Poker", "Magic"]
difficulty: hard
source: "https://www.ctfiot.com/74040.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 逆向心法修炼之道 FLARE ON 9TH WRITEUP

> 赛事：FLARE ON 9th Challenge 2022 | 方向：reverse | 难度：hard

## 一句话总结

FlareOn 9th (2022)全11题WP,涵盖Flaredle硬编码/Pixel Poker坐标/Magic 8 Ball方向键/darn_mice单字节ret反推/T8满月+srand+RC4+月相计算+àla mode mixed-mode PE+pipe RPC+password MyV0ic3!。

## 攻击链

1. 第1题Flaredle:word.js内置硬编码值对比
2. 第2题Pixel Poker:像素坐标x==0x52414C46%0x2E5=95,y==0x6E4F2D45%0x281=313
3. 第3题Magic 8 Ball:输入gimme flag pls?+L L U R U L D U L方向键序列
4. 第4题darn_mice:str[i]+v5[i]=单字节ret(0xC3)+反推输入see three, C3 C3 C3 C3 C3 C3 C3! XD
5. 第5题T8:sleep到满月+srand(本小时毫秒数)+rc4(FO9+randnum)+POST flare-on.com
6. T8攻击:枚举srand seed(14:14:36前后)+遍历65535个md5+找出rc4 key
7. T8解密:14组_SYSTEMTIME+月相值索引alphabet表=flag前缀i_**
8. 第6题àla mode:capa v4.0识别mixed mode+floss-floss找xor解密后的\.\pipe\FlareOn
9. DllEntryPoint定位0x1000181A+native code xor动态解密函数符号+\.\pipe\FlareOn RPC通信
10. 预置密码:MyV0ic3!+0x10001187解密flag

## 关键 payload

```
see three, C3 C3 C3 C3 C3 C3 C3! XD + MyV0ic3!
```

## 经验教训

FlareOn是Windows逆向顶级比赛,Mandiant出题质量高;mixed-mode PE(.NET+native)是复杂逆向场景;capa+floss+IDA联合分析是Windows逆向标配;满月+日期穿越是T8的特色。

## 标签

FlareOn、Mandiant、mixed-mode-PE、.NET-native、capa、floss、PE32、RC4、moonphase-calc、wchar-keystream、xor-decrypt

## 参考来源

- https://www.ctfiot.com/74040.html
- 原文件：逆向心法修炼之道_FLARE_ON_9TH_WRITEUP.full.md

---
title: "Backdoor CTF 2023 Writeup"
category: misc
tags: ["Backdoor CTF", "misc", "exiftool Artist", "flag{7h3_r34l_ctf_15_7h3_fr13nd5_w3_m4k3_al0ng}", "jadx smali", "open_sesame MainActivity"]
signals: ["Backdoor CTF 2023", "exiftool Artist", "flag{7h3_r34l_ctf_15_7h3_fr13nd5_w3_m4k3_al0ng}", "jadx smali", "open_sesame MainActivity", "it4chi n4ut1lus sh4dy sl4y3r", "valid_password 7字节", "XOR循环校验", "Character.isDigit", "misc_unknown", "Backdoor", "CTF", "exiftool", "Artist"]
difficulty: easy
source: "https://www.ctfiot.com/152665.html"
tools: ["ExifTool"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Backdoor CTF 2023 Writeup

> 赛事：Backdoor CTF 2023 | 方向：misc | 难度：easy | 工具：ExifTool

## 一句话总结

Backdoor CTF 2023 — exiftool Artist 字段直接读 flag + open_sesame APK smali 分析 it4chi/n4ut1lus/sh4dy/sl4y3r/flag 函数 + valid_password 0x34 0x6c 0x31 0x62 0x61 0x62 0x61 = "4l1baba"。

## 攻击链

1. friend.jpeg exiftool Artist: flag{7h3_r34l_ctf_15_7h3_fr13nd5_w3_m4k3_al0ng}
2. open_sesame.apk jadx 反编译 smali
3. MainActivity.valid_password = [0x34, 0x6c, 0x31, 0x62, 0x61, 0x62, 0x61] = "4l1baba
4. it4chi: char → int[] 数组
5. n4ut1lus: 比较 int[] 长度和元素
6. sh4dy: 保留数字字符 (Character.isDigit)
7. sl4y3r: 字符串处理
8. flag: charAt 循环 XOR
9. 登录: 输入 user + 密码

## 关键 payload

```
exiftool Artist flag / valid_password 0x34 0x6c 0x31 0x62 0x61 0x62 0x61 = "4l1baba" / it4chi+n4ut1lus+sh4dy+sl4y3r / XOR 循环
```

## 经验教训

JPEG EXIF Artist 字段常被用来藏 flag;smali 读 valid_password 数组转 ASCII 是 APK 入门基础;函数名混淆 it4chi/n4ut1lus/sh4dy/sl4y3r 提示四元素 (海龟汤)。

## 标签

exiftool Artist、flag{7h3_r34l_ctf_15_7h3_fr13nd5_w3_m4k3_al0ng}、jadx smali、open_sesame MainActivity、it4chi n4ut1lus sh4dy sl4y3r、valid_password 7字节、XOR循环校验、Character.isDigit、sl4y3r

## 参考来源

- https://www.ctfiot.com/152665.html
- 原文件：Backdoor_CTF_2023_Writeup.full.md

---
title: "2022 年春秋杯冬季赛部分 WriteUp (天权信安)"
category: web
tags: ["2022 春秋杯冬季赛", "web", "春秋杯", "天权信安", "PHP-下划线绕过", "ftp-pcap"]
signals: ["2022 春秋杯冬季赛 2022", "春秋杯", "天权信安", "PHP-下划线绕过", "ftp-pcap", "零宽隐写", "reindeer-game", "Python-字节码", "位旋转", "sqli", "stego_image", "reverse", "web_unknown", "PHP"]
difficulty: easy
source: "https://www.ctfiot.com/88076.html"
tools: ["PHP", "Python", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 年春秋杯冬季赛部分 WriteUp (天权信安)

> 赛事：2022 春秋杯冬季赛 2022 | 方向：web | 难度：easy | 工具：PHP、Python、Wireshark

## 一句话总结

春秋杯 2022 冬季赛：PHP 下划线弱类型 + 零宽隐写 + Python 字节码

## 攻击链

1. Web ezphp: ?num=1_11 PHP 弱类型 + 数字下划线绕过
2. Misc nan''s analysis: Wireshark 导出 ftp 对象 → 图片末尾附加 shell.zip (零宽隐写)
3. Misc reindeer game: 简单小游戏通关 → flag{82a2acb6-9803-4936-92db-f1431d90c6d1}
4. Re easy_python: Python 字节码逆向 → LOAD_CONST 列表 + 位旋转 (x >> 5 | x << 3) & 0xff
5. flag = [204,141,44,...] → flag{ddbae889-2895-44df-897d-2ae30df77b61}

## 关键 payload

```
flag = (flag[i] >> 5 | flag[i] << 3) & 255
```

## 经验教训

Python 字节码是 reverse 入门利器；PHP 下划线数字 (`1_11`) 是弱类型；零宽隐写是 misc 经典

## 标签

春秋杯、天权信安、PHP-下划线绕过、ftp-pcap、零宽隐写、reindeer-game、Python-字节码、位旋转、IDAPython

## 参考来源

- https://www.ctfiot.com/88076.html
- 原文件：2022年春秋杯冬季赛部分WriteUp.full.md

---
title: "CTF 《2015 移动安全挑战赛》第二题 AliCrackme_2 逆向"
category: reverse
tags: ["移动安全挑战赛", "reverse", "Android so 静态", "while 循环匹配", "aWojiushidaan", "Frida hook fgets"]
signals: ["移动安全挑战赛 2015", "Android so 静态", "while 循环匹配", "aWojiushidaan", "Frida hook fgets", "TracerPid:t0", "hook kill", "mprop ro.debuggable", "AS 64端口12346", "reverse", "AliCrackme_2", "Android", "while", "Frida"]
difficulty: easy
source: "https://www.ctfiot.com/124720.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 《2015 移动安全挑战赛》第二题 AliCrackme_2 逆向

> 赛事：移动安全挑战赛 2015 | 方向：reverse | 难度：easy

## 一句话总结

AliCrackme_2 — Android so 静态分析 while 循环匹配 aWojiushidaan + Frida hook fgets 改 TracerPid:t0 + hook kill + mprop ro.debuggable 1 + android_server64 -p12346 调试。

## 攻击链

1. so 静态: while 循环匹配用户输入 vs 硬编码 aWojiushidaan
2. 反调试: Frida hook fgets 改 TracerPid: 为 TracerPid:t0
3. Frida hook kill 直接返回 0
4. 启动 android_server64 -p 12346 root 调试
5. mprop 工具 ro.debuggable 1 改属性

## 关键 payload

```
while 循环字符比较 / aWojiushidaan / Frida hook fgets 改 TracerPid / Frida hook kill / mprop ro.debuggable 1 / android_server64 12346
```

## 经验教训

Android 经典逆向三件套:静态分析硬编码字符串 + Frida hook 改 TracerPid + mprop 改 ro.debuggable;2015 年风格是 so 字符比较。

## 标签

Android so 静态、while 循环匹配、aWojiushidaan、Frida hook fgets、TracerPid:t0、hook kill、mprop ro.debuggable、AS 64端口12346、看雪 行简、2015经典

## 参考来源

- https://www.ctfiot.com/124720.html
- 原文件：CTF_《2015移动安全挑战赛》第二题_AliCrackme_2_逆向.full.md

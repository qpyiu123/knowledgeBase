---
title: "破译APK口令，解锁知识宝藏：大狗Unlock活动优质经验分享"
category: reverse
tags: ["大狗Unlock活动", "reverse", "APK逆向", "jadx反编译", "AndroidManifest.xml", "Frida hook"]
signals: ["大狗Unlock活动 2024", "APK逆向", "jadx反编译", "AndroidManifest.xml", "Frida hook", "云真机平台", "ROT偏移", "cyberchef", "Check类异或", "reverse", "Unlock", "APK", "jadx", "ROT21"]
difficulty: easy
source: "https://www.ctfiot.com/223172.html"
tools: ["Frida", "Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 破译APK口令，解锁知识宝藏：大狗Unlock活动优质经验分享

> 赛事：大狗Unlock活动 2024 | 方向：reverse | 难度：easy | 工具：Frida、Java

## 一句话总结

大狗Unlock 1-5题全解：APK静态jadx+ROT21/异或+动态Frida hook+云真机

## 攻击链

1. jadx反编译APK→AndroidManifest.xml定位MainActivity→静态算法分析（ROT21偏移/异或）→云真机+Frida hook动态取随机数/修改Checker.code.value=512→提交flag

## 关键 payload

```
ROT21偏移:chr(ord(char)-21)+26补偿;Dagou{Unlok_HOOK_0x1};Checker.code.value=512;frida Java.use + 复制片段
```

## 经验教训

大狗云真机平台+Frida hook组合；APK定位用AndroidManifest.xml的LAUNCHER；ROT偏移负数补偿

## 标签

APK逆向、jadx反编译、AndroidManifest.xml、Frida hook、云真机平台、ROT偏移、cyberchef、Check类异或、静态+动态双解

## 参考来源

- https://www.ctfiot.com/223172.html
- 原文件：破译APK口令，解锁知识宝藏：大狗Unlock活动优质经验分享.full.md

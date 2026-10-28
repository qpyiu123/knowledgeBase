---
title: "Android APK 逆向分析：多组件协同漏洞利用链详解"
category: misc
tags: ["Android 逆向", "misc", "APK反编译", "WebActivity未导出", "CoreService normal权限", "AIDL a.Stub"]
signals: ["Android 逆向 2025", "APK反编译", "WebActivity未导出", "CoreService normal权限", "AIDL a.Stub", "MiscService透传Intent", "CLASS_NAME", "libWaWaWa.so 娜迦加固", "DT_STRTAB损坏", "reverse", "Android", "APK", "MiscService", "Intent"]
difficulty: hard
source: "https://www.ctfiot.com/284169.html"
tools: ["ARM"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Android APK 逆向分析：多组件协同漏洞利用链详解

> 赛事：Android 逆向 2025 | 方向：misc | 难度：hard | 工具：ARM

## 一句话总结

Android 多组件协同漏洞链 — APK 反编译 + MiscService (已导出) 透传 Intent CLASS_NAME 启动未导出 WebActivity + CoreService AIDL 远程调 JNI 拿 key/iv + libWaWaWa.so 娜迦加固解密。

## 攻击链

1. apktool d Load -o decompiled 反编译
2. WebActivity(未导出) 需走 Intent 跳板
3. CoreService (normal 权限) AIDL a.Stub 提供 Load.getUrl/getToken/getIv + decode
4. MiscService (已导出) 透传 Intent CLASS_NAME + putExtras
5. b implements Serializable { key, iv, status } DTO
6. WebActivity 读 Serializable b 实例, 满足 c()="loading" 调 Load.decode
7. libWaWaWa.so 32 位 ARM, DT_STRTAB 损坏, 娜迦加固特征
8. JNI: Java_com_example_wawawa_Load_decode / getUrl / getToken / getIv
9. 攻击: 通过 MiscService 启动 WebActivity, 传 Serializable b 实例
10. 申请 normal 权限 com.example.wawawa.permission.CORE_SERVICE

## 关键 payload

```
APK 多组件协同 / MiscService Intent 透传 / WebActivity 未导出但可间接启动 / CoreService AIDL a.Stub / 娜迦加固 / Serializable b DTO / JNI decode
```

## 经验教训

Android normal 权限形同虚设,任何 app 可申请;MiscService 透传 Intent 是常见未导出组件攻击跳板;娜迦加固 DT_STRTAB 损坏是显著特征;Serializable DTO 跨进程传参可携带攻击 payload。

## 标签

APK反编译、WebActivity未导出、CoreService normal权限、AIDL a.Stub、MiscService透传Intent、CLASS_NAME、libWaWaWa.so 娜迦加固、DT_STRTAB损坏、JNI decode、Serializable DTO、DES key/iv

## 参考来源

- https://www.ctfiot.com/284169.html
- 原文件：Android_APK逆向分析：多组件协同漏洞利用链详解.full.md

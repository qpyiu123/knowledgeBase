---
title: "【WriteUP·中篇】2024WIDC 世界智能驾驶挑战赛\"天融信杯\"信息安全攻防赛"
category: misc
tags: ["WIDC", "misc", "车联网-APP", "IPA-逆向", "命令执行双写%0截断", "WPA-PSK-空口包"]
signals: ["WIDC 2024", "车联网-APP", "IPA-逆向", "命令执行双写%0截断", "WPA-PSK-空口包", "weak-password-123", "base64-16进制解码", "misc_unknown", "WIDC", "APP", "IPA", "WPA", "PSK", "acacatt"]
difficulty: medium
source: "https://www.ctfiot.com/186393.html"
tools: ["Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WriteUP·中篇】2024WIDC 世界智能驾驶挑战赛"天融信杯"信息安全攻防赛

> 赛事：WIDC 2024 | 方向：misc | 难度：medium | 工具：Wireshark

## 一句话总结

2024 WIDC 天融信杯中篇，车联网 APP 控车 + IPA 逆向 + 命令执行双写%0 截断 + WPA PSK 解密 + 弱口令 123。

## 攻击链

1. 1. APP 远程控车 → 拿 IPA/2. 命令执行：双写加 %0 截断 ip=1.1.1.1%0acacatt flflagag.php/3. ssid=wifi + password=root12222 生成 PSK/4. Wireshark wpa-psk 工具生成 WPA PSK 解密空口 wifi 包/5. 弱口令 123 解压/6. Winhex base64 + 16 进制转字符串解码得 flag

## 关键 payload

```
ip=1.1.1.1%0acacatt flflagag.php  PSK 生成 wireshark.org/tools/wpa-psk.html  flag{f7sgu2lsagbgfa90f63dc8b6e0e2Kg2lVW}
```

## 经验教训

命令执行双写（flflagag.php 走 fl 跳 flag）+ %0a 截断；WPA PSK 用 ssid+password 算；Winhex 看 base64 后转 16 进制字符串。

## 标签

车联网-APP、IPA-逆向、命令执行双写%0截断、WPA-PSK-空口包、weak-password-123、base64-16进制解码

## 参考来源

- https://www.ctfiot.com/186393.html
- 原文件：【WriteUP·中篇】2024WIDC世界智能驾驶挑战赛“天融信杯”信息安全攻防赛.full.md

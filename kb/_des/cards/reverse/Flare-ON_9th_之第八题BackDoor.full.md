---
title: "Flare-ON 9th 之第八题BackDoor"
category: reverse
tags: ["Flare-ON 9 (2022)", "reverse", "rev", "csharp", "dotnet", "flareon"]
signals: ["Flare-ON 9 (2022) 2022", "rev", "csharp", "dotnet", "flareon", "dnslib", "dns-tunnel", "arc4", "powershell", "reverse", "Flare-ON", "BackDoor", "DNS", "RC4"]
difficulty: hard
source: "https://www.ctfiot.com/84092.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Flare-ON 9th 之第八题BackDoor

> 赛事：Flare-ON 9 (2022) 2022 | 方向：reverse | 难度：hard | 工具：C

## 一句话总结

Flare-ON 9 第8题BackDoor：C#反混淆+DNS隧道+RC4解密flag

## 攻击链

1. C#反混淆：dnlib解析方法体
2. flareon_wrap_decrypt解包装方法（Nop+Call+flare_71）
3. flareon_decrypt解flared方法：RC4(0x12784adf, sec_data)
4. DNS隧道协议：dnslib自定义TestResolver
5. op=[2,10,8,19,...]操作序列→base32 dns子域
6. 解密flag：arc4(hashlib.md5(ps), ...)
7. powershell -exec bypass -enc base64命令

## 关键 payload

```
ps = "powershell -exec bypass -enc " + base64 + "...
```

## 经验教训

flareon_wrap_decrypt基于Nop+Call+flare_71模式识别包装方法

## 标签

rev、csharp、dotnet、flareon、dnslib、dns-tunnel、arc4、powershell、cil-body

## 参考来源

- https://www.ctfiot.com/84092.html
- 原文件：Flare-ON_9th_之第八题BackDoor.full.md

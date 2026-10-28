---
title: "2025 御网杯【本科组】线下半决赛 CTF+总决赛应急响应综合渗透 WriteUp"
category: misc
tags: ["2025 御网杯", "misc", "御网杯 2025 本科组 线下半决赛", "USB 键盘流量 <DEL> 删除", "压缩包密码爆破 882401", "exe 实际是压缩包改后缀解压"]
signals: ["2025 御网杯 2025", "御网杯 2025 本科组 线下半决赛", "USB 键盘流量 <DEL> 删除", "压缩包密码爆破 882401", "exe 实际是压缩包改后缀解压", "全局搜索 flag+hex 解码 666c61677b", "工业流量分析 按时间排序 STOP", "0k4o rot13", "Base32+Base64+Ascii85 混合解码 3 次", "stego_image", "sqli", "web_unknown", "misc_math", "Misc"]
difficulty: easy
source: "https://www.ctfiot.com/267352.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 御网杯【本科组】线下半决赛 CTF+总决赛应急响应综合渗透 WriteUp

> 赛事：2025 御网杯 2025 | 方向：misc | 难度：easy

## 一句话总结

2025 御网杯本科组线下半决赛 Misc+Crypto 多题：USB 键盘流量+压缩包爆破+exe 改后缀+工业流量+rot13+Base 混合解码。

## 攻击链

1. 键盘流量: iloveyou<DEL>...flag{}inKJ<DEL>...op97ya<DEL>...bc6g9 → 删 DEL 前内容 → flag{inop97bc6g9}
2. 压缩包密码爆破: 882401 解压 + 文档清除格式
3. exe 实际是压缩包: 16 进制头 50 4B 改后缀解压 → 流量包 → 全局搜 flag 编码 → 666c6167... → flag{DGswTfgy1GD236fs2sfF2dskLng}
4. 工业流量分析: 按时间排序，最先 STOP 的包 → flag{ac6417423bb3000c}
5. 0k4o 0k46 ... rot13 → Base32→Base64→Ascii85 → flag{hnctfqwer54321}

## 关键 payload

```
USB 键盘流量 <DEL> 8 次 = 8 个删除字符
```

## 经验教训

USB 键盘流量 `<DEL>` 是 Backspace 退格键，要计算删除字符数还原真实输入；exe 改后缀解压是流量包杂项最常见套路；Base32→Base64→Ascii85 混合解码是 CTF crypto 经典链。

## 标签

御网杯 2025 本科组 线下半决赛、USB 键盘流量 <DEL> 删除、压缩包密码爆破 882401、exe 实际是压缩包改后缀解压、全局搜索 flag+hex 解码 666c61677b、工业流量分析 按时间排序 STOP、0k4o rot13、Base32+Base64+Ascii85 混合解码 3 次、工业控制 s7comm、IEC 60870-5 104

## 参考来源

- https://www.ctfiot.com/267352.html
- 原文件：2025御网杯【本科组】线下半决赛CTF+总决赛应急响应综合渗透WriteUp.full.md

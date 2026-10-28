---
title: "2022 年强网杯青少年专项赛 writeup"
category: web
tags: ["2022 强网杯青少年专项赛", "web", "青少年", "强网杯", "data://", "base64"]
signals: ["2022 强网杯青少年专项赛 2022", "青少年", "强网杯", "data://", "base64", "Sliver-Range-Water-Circle", "Python-pickle", "LSB-stego", "二维码", "lfi", "deserialize", "crypto_oracle", "stego_image", "data"]
difficulty: medium
source: "https://www.ctfiot.com/58504.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 年强网杯青少年专项赛 writeup

> 赛事：2022 强网杯青少年专项赛 2022 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

强网青少年赛 6 大题：data:// LFI + Python 反序列化链 + LSB + 二维码排列

## 攻击链

1. Q1: data:// + fopen + fputs + include LFI, 长度限制 21, 过滤 php/file/http/eval/exec/system/popen/flag/<">
2. ?file=data://,1111&content=data://text/plain;base64,PD9waHAgc3lzdGVtKCd0eXBlIGluZGV4LnBocCcpOz8+ → include php://filter
3. Q2: Python 反序列化 Sliver→Range→Water→Circle.dash=''@eval($_GET[a]);
4. Q3: FLAG[vxpsDqCElwwoClsoColwpuvlqFvvFrpopBss] 字符大小写转换
5. Q4: 十六进制数据按 2 字节 swap → ctf.txt
6. Q5: python2 lsb.py extract 1.png 1.txt 4536251 LSB 隐写
7. Q6: 29x29 矩阵 + pyzbar 暴力 permutations(720×120) 拼二维码

## 关键 payload

```
?file=data://,1111&content=data://text/plain;base64,PD9waHAgc3lzdGVtKCd0eXBlIGluZGV4LnBocCcpOz8+
```

## 经验教训

data:// 协议 + fopen + fputs + include 是 LFI 经典；青少年赛偏基础 + 趣味

## 标签

青少年、强网杯、data://、base64、Sliver-Range-Water-Circle、Python-pickle、LSB-stego、二维码、pyzbar、permutations

## 参考来源

- https://www.ctfiot.com/58504.html
- 原文件：2022年强网杯青少年专项赛writeup.full.md

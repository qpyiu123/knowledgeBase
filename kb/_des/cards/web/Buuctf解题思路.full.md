---
title: "Buuctf 解题思路"
category: web
tags: ["Buuctf", "web", "DialogFunc Win32", "GetDlgItemTextA 8字符", "字符串比较", "sub_4010F0 快排"]
signals: ["Buuctf 2022", "DialogFunc Win32", "GetDlgItemTextA 8字符", "字符串比较", "sub_4010F0 快排", "sub_401000 base64 编码", "byte_407830 表", "APK jadx", "dd2940c04462b4dd7c450528835cca15 XOR", "web_unknown", "Buuctf", "DialogFunc", "base64", "APK"]
difficulty: medium
source: "https://www.ctfiot.com/64553.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Buuctf 解题思路

> 赛事：Buuctf 2022 | 方向：web | 难度：medium

## 一句话总结

Buuctf 3 题合集 — 刮开有奖 DialogFunc 8 字符 + 快排 + base64 编码比较 + 简单注册器 APK 32 字符 + dd2940c0... XOR + reverse + easy strcmp qword 减法还原。

## 攻击链

1. 刮开有奖: DialogFunc 接受 8 字符, 内部数组 v9-v19 存 90,74,83,69,67,97,78,72,51,110,103 (ZJSECaNH3ng)
2. sub_4010F0 快排: 改 v9-v19 顺序
3. sub_401000 base64 编码: 拿排序后字符串
4. 比较条件: String == v9+34 && v21 == v13 && 4*v22-141 == 3*v11 && v23/4 == 2*(v16/9) && !strcmp(v6, "ak1w") && !strcmp(v7, "V1Ax")
5. 简单注册器: APK jadx, MainActivity 32 字符注册码 + dd2940c04462b4dd7c450528835cca15 改 + reverse
6. easy strcmp: qword 减法恢复 3 个 8 字节字符串拼接 flag

## 关键 payload

```
DialogFunc 8 字符 / sub_4010F0 快排 v9-v19 / sub_401000 base64 编码 / dd2940c04462b4dd7c450528835cca15 XOR + reverse / qword_201060 3 个 8字节减法
```

## 经验教训

字符串比较题多步:输入字符串 → 数组排序 → base64 编码 → 多重比较;APK 注册码常用 char[] + char 运算 + reverse;qword 减法是反编译快速 strcmp 还原的常见手段。

## 标签

DialogFunc Win32、GetDlgItemTextA 8字符、字符串比较、sub_4010F0 快排、sub_401000 base64 编码、byte_407830 表、APK jadx、dd2940c04462b4dd7c450528835cca15 XOR、qword 减法、easy strcmp

## 参考来源

- https://www.ctfiot.com/64553.html
- 原文件：Buuctf解题思路.full.md

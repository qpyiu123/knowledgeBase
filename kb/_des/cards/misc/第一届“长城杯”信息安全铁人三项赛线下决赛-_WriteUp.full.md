---
title: "第一届“长城杯”信息安全铁人三项赛线下决赛- WriteUp"
category: misc
tags: ["第一届长城杯信息安全铁人三项赛", "misc", "长城杯", "铁人三项", "EDI安全", "企业环境渗透"]
signals: ["第一届长城杯信息安全铁人三项赛 2024", "长城杯", "铁人三项", "EDI安全", "企业环境渗透", "取证溯源", "php://filter读源码", "综合靶场", "misc_unknown", "flag", "flag1-14", "php", "filter"]
difficulty: medium
source: "https://www.ctfiot.com/183955.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第一届“长城杯”信息安全铁人三项赛线下决赛- WriteUp

> 赛事：第一届长城杯信息安全铁人三项赛 2024 | 方向：misc | 难度：medium

## 一句话总结

第一届长城杯信息安全铁人三项赛线下决赛：12+flag企业环境渗透+取证溯源综合WP

## 攻击链

1. 12+个flag(flag1-14)→企业环境渗透(202.0.6.195/194/193)→php://filter读flag.php→取证溯源(data2024.zip+SSH+VNC)

## 关键 payload

```
flag1-14多flag;php://filter/read=convert.base64-encode/resource=flag.php;202.0.5.236 root:Szivfn4bLZ;data2024.zip
```

## 经验教训

铁人三项赛综合渗透：企业环境+移动应用+取证溯源

## 标签

长城杯、铁人三项、EDI安全、企业环境渗透、取证溯源、php://filter读源码、综合靶场

## 参考来源

- https://www.ctfiot.com/183955.html
- 原文件：第一届“长城杯”信息安全铁人三项赛线下决赛-_WriteUp.full.md

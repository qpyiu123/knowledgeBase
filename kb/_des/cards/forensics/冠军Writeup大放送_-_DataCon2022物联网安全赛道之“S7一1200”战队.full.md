---
title: "冠军Writeup大放送 | DataCon2022物联网安全赛道之\"S7一1200\"战队"
category: forensics
tags: ["DataCon2022 物联网安全", "forensics", "DataCon", "物联网安全", "固件基地址识别", "函数符号恢复"]
signals: ["DataCon2022 物联网安全 2022", "DataCon", "物联网安全", "固件基地址识别", "函数符号恢复", "整数溢出检测", "bindiff", "S7-1200", "中科院信工所", "forensic_disk", "DataCon2022"]
difficulty: medium
source: "https://www.ctfiot.com/92303.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 冠军Writeup大放送 | DataCon2022物联网安全赛道之"S7一1200"战队

> 赛事：DataCon2022 物联网安全 2022 | 方向：forensics | 难度：medium

## 一句话总结

DataCon2022 物联网安全冠军 S7-1200：固件基地址识别 + bindiff 符号恢复 + 整数溢出检测。

## 攻击链

1. 中科院信工所 S7-1200 战队 (李红老师)
2. 第一部分: 固件基地址识别 (图1 加载基址示意)
3. 图2 各固件字符串数量统计柱形图
4. 图3 加载基址识别过程示意
5. 第二部分: 函数符号恢复 (bindiff 工具)
6. 第三部分: 整数溢出检测
7. S7-1200 PLC 相关固件逆向
8. 2021 DataCon 第二名战绩 (老板说得真队)

## 关键 payload

```
固件基地址识别 + bindiff 函数符号恢复 + 整数溢出检测
```

## 经验教训

固件逆向三件套: 1) 加载基地址识别 (字符串统计+熵分析) 2) bindiff 对比已知版本恢复符号 3) 整数溢出检测 (符号执行/约束求解)。

## 标签

DataCon、物联网安全、固件基地址识别、函数符号恢复、整数溢出检测、bindiff、S7-1200、中科院信工所

## 参考来源

- https://www.ctfiot.com/92303.html
- 原文件：冠军Writeup大放送_-_DataCon2022物联网安全赛道之“S7一1200”战队.full.md

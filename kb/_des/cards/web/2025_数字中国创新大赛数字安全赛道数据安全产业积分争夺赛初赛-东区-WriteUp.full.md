---
title: "2025 数字中国创新大赛数字安全赛道数据安全产业积分争夺赛初赛-东区 WP"
category: web
tags: ["2025 数字中国创新大赛数字安全赛道", "web", "数字中国 2025 数据安全东区", "ez_upload 漏洞", "加密驱动器 BitLocker 解密", "web 日志分析 awk 排序 uniq 统计"]
signals: ["2025 数字中国创新大赛数字安全赛道 2025", "数字中国 2025 数据安全东区", "ez_upload 漏洞", "加密驱动器 BitLocker 解密", "web 日志分析 awk 排序 uniq 统计", "溯源与取证", "数据社工 邮箱爆破", "数据跨境 语音通话还原", "awk -F ' ' '{print $1}' 1.log", "sqli", "forensic_disk", "misc_unknown", "BitLocker", "web"]
difficulty: easy
source: "https://www.ctfiot.com/235930.html"
tools: ["Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 数字中国创新大赛数字安全赛道数据安全产业积分争夺赛初赛-东区 WP

> 赛事：2025 数字中国创新大赛数字安全赛道 2025 | 方向：web | 难度：easy | 工具：Wireshark

## 一句话总结

2025 数字中国数据安全产业积分争夺赛：BitLocker 解密 + web 日志 awk 排序找黑客 IP + 邮箱对比 + VoIP 流量还原。

## 攻击链

1. 数据安全 ez_upload: 文件上传漏洞利用
2. 服务器 web 日志 awk -F ' ' '{print $1}' 1.log | sort | uniq -c | sort -nr → 找黑客 IP
3. 加密驱动器 BitLocker 解密 → 拿 web 日志
4. 数据社工 邮箱爆破：员工.xlsx + mysql_data.txt 对比
5. 数据跨境 语音通话还原：流量文件 VoIP 提取（小写 26 字母）

## 关键 payload

```
awk -F ' ' '{print $1}' 1.log | sort | uniq -c | sort -nr
```

## 经验教训

BitLocker 加密驱动器是数据安全赛常见考点；awk -F ' ' 取 IP + sort | uniq -c | sort -nr 是日志分析标准流程；VoIP 流量还原用 Wireshark + rtp 分析。

## 标签

数字中国 2025 数据安全东区、ez_upload 漏洞、加密驱动器 BitLocker 解密、web 日志分析 awk 排序 uniq 统计、溯源与取证、数据社工 邮箱爆破、数据跨境 语音通话还原、awk -F ' ' '{print $1}' 1.log

## 参考来源

- https://www.ctfiot.com/235930.html
- 原文件：2025_数字中国创新大赛数字安全赛道数据安全产业积分争夺赛初赛-东区-WriteUp.full.md

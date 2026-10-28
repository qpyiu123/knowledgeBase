---
title: "DownUnderCTF 2024——取证方向题解"
category: forensics
tags: ["DownUnderCTF 2024", "forensics", "forensics", "nmap", "wmi", "mimikatz"]
signals: ["DownUnderCTF 2024 2024", "forensics", "nmap", "wmi", "mimikatz", "domain-controller", "emuc2", "traffic-analysis", "forensic_disk", "DownUnderCTF", "WMI", "Bad", "Policies", "Baby"]
difficulty: medium
source: "https://www.ctfiot.com/196634.html"
tools: ["nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DownUnderCTF 2024——取证方向题解

> 赛事：DownUnderCTF 2024 2024 | 方向：forensics | 难度：medium | 工具：nmap

## 一句话总结

DownUnderCTF 2024 取证4题：流量+域控WMI+Bad Policies+emuc2

## 攻击链

1. Baby''s First Forensics: 流量分析识别扫描工具及版本
2. SAM I AM: WMI+域管理员密码 mimikatz
3. Bad Policies: 域控制器访问方法还原
4. emuc2: 模拟C2恶意软件流量分析

## 关键 payload

```
nmap_7.25  # 类似格式
```

## 经验教训

取证题常用流量分析+SMB事件+注册表+内存镜像组合

## 标签

forensics、nmap、wmi、mimikatz、domain-controller、emuc2、traffic-analysis

## 参考来源

- https://www.ctfiot.com/196634.html
- 原文件：DownUnderCTF_2024——取证方向题解.full.md

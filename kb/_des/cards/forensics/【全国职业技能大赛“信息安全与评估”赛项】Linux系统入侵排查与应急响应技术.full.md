---
title: "【全国职业技能大赛\"信息安全与评估\"赛项】Linux系统入侵排查与应急响应技术"
category: forensics
tags: ["全国职业技能大赛", "forensics", "应急响应", "Linux-IR", "lsof-process", "/etc/passwd"]
signals: ["全国职业技能大赛 2024", "应急响应", "Linux-IR", "lsof-process", "/etc/passwd", "cron-check", "auth.log", "SSH", "init.d", "forensic_disk", "Linux", "cron", "ssh", "lsof"]
difficulty: easy
source: "https://www.ctfiot.com/218471.html"
tools: ["objdump"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【全国职业技能大赛"信息安全与评估"赛项】Linux系统入侵排查与应急响应技术

> 赛事：全国职业技能大赛 2024 | 方向：forensics | 难度：easy | 工具：objdump

## 一句话总结

全国职业技能大赛 Linux 应急响应技术，9 大模块：进程/端口/历史/恶意文件/恶意程序/账户/cron/系统日志/.ssh。

## 攻击链

1. 1. 进程排查 lsof -p PID /2. 端口 ss/netstat /3. 历史命令 history /4. 恶意文件 find /tmp /dev/shm /5. 分析恶意程序 strings+objdump /6. Linux 账户 /etc/passwd uid=0 /etc/shadow /7. cron /etc/crontab /var/spool/cron/ /8. 系统日志 /var/log/cron/message/btmp/wtmp/secure /9. .ssh authorized_keys

## 关键 payload

```
lsof -p  /etc/passwd uid=0  /var/log/secure  /etc/crontab  /var/spool/cron
```

## 经验教训

应急响应 9 模块：lsof 进程 + 端口 + history + find + strings + /etc/passwd + cron + /var/log + .ssh。

## 标签

应急响应、Linux-IR、lsof-process、/etc/passwd、cron-check、auth.log、SSH、init.d

## 参考来源

- https://www.ctfiot.com/218471.html
- 原文件：【全国职业技能大赛“信息安全与评估”赛项】Linux系统入侵排查与应急响应技术.full.md

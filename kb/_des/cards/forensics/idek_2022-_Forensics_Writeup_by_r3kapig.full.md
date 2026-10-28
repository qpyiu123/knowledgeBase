---
title: "idek 2022: Forensics Writeup by r3kapig"
category: forensics
tags: ["idekCTF", "forensics", "pgp-private-key", "gpg2john", "hashcat-17010", "rockyou"]
signals: ["idekCTF 2022", "pgp-private-key", "gpg2john", "hashcat-17010", "rockyou", "netascii-7z", "ssh-aes-gcm", "network-parser", "openssh", "forensic_memory", "idekCTF", "r3kapig", "Forensics", "PGP"]
difficulty: hard
source: "https://www.ctfiot.com/92742.html"
tools: ["hashcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# idek 2022: Forensics Writeup by r3kapig

> 赛事：idekCTF 2022 | 方向：forensics | 难度：hard | 工具：hashcat

## 一句话总结

idekCTF 2022 r3kapig 战队 Forensics 套题，PGP+SSH+流量+内存取证综合。

## 攻击链

1. PGP 私钥 gpg2john → hashcat -m 17010 爆破
2. Netascii 7z 修复 (CR/LF 替换)
3. SSH AES-GCM 密钥 + IV 解析
4. network-parser 解密 SSH 流量
5. proc mem 提取 root 密码
6. 总结报告

## 关键 payload

```
PGP 爆破 + Netascii 修复 + SSH AES-GCM 解密
```

## 经验教训

真实企业环境中 PGP/SSH 凭据泄露是高频事件，forensic 套题模拟完整流程。

## 标签

pgp-private-key、gpg2john、hashcat-17010、rockyou、netascii-7z、ssh-aes-gcm、network-parser、openssh、pidstat、volatility、proc-mem

## 参考来源

- https://www.ctfiot.com/92742.html
- 原文件：idek_2022-_Forensics_Writeup_by_r3kapig.full.md

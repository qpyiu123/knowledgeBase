---
title: "CTF学习交流群 第六期writeup大放送"
category: web
tags: ["群赛出题", "web", "misc", "etl", "smb", "NTLM"]
signals: ["群赛出题 2017", "misc", "etl", "smb", "NTLM", "hashcat", "reverse", "life_or_flag", "群活动", "forensic_traffic", "SMB", "Net-NTLM", "flag", "etl2pcapng"]
difficulty: medium
source: "https://www.ctfiot.com/92889.html"
tools: ["hashcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF学习交流群 第六期writeup大放送

> 赛事：群赛出题 2017 | 方向：web | 难度：medium | 工具：hashcat

## 一句话总结

群第6期三题，etl+SMB Net-NTLM爆破+逆向flag约束方程

## 攻击链

1. etl2pcapng转换netsh trace为pcap
2. wireshark看SMB抓flag.zip多次重传
3. 提取Net-NTLM hash format username::domain:challenge:HMAC-MD5:blob
4. hashcat -m 5600爆破administrator密码为flag
5. life_or_flag: 20字符flag读入后deal()分支运算+4字节线性方程组

## 关键 payload

```
hashcat64 -m 5600 administrator:::8b1ca28f...:1c4d7b10...:010100... flag.txt
```

## 经验教训

Net-NTLM从SMB包中提取后hashcat秒破

## 标签

misc、etl、smb、NTLM、hashcat、reverse、life_or_flag、群活动

## 参考来源

- https://www.ctfiot.com/92889.html
- 原文件：CTF学习交流群_第六期writeup大放送.full.md

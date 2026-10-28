---
title: "Hack The Boo 2022 CTF题目解析"
category: misc
tags: ["Hack The Boo 2022 (HTB)", "misc", "htb", "halloween", "forensics", "rev"]
signals: ["Hack The Boo 2022 (HTB) 2022", "htb", "halloween", "forensics", "rev", "pwn", "web", "olevba", "base64", "misc_unknown", "HTB", "Hack", "Boo", "Halloween"]
difficulty: medium
source: "https://www.ctfiot.com/75596.html"
tools: ["PHP", "Python", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hack The Boo 2022 CTF题目解析

> 赛事：Hack The Boo 2022 (HTB) 2022 | 方向：misc | 难度：medium | 工具：PHP、Python、tshark

## 一句话总结

HTB Hack The Boo 2022：10题Halloween主题（Forensics+Rev+Pwn+Web）

## 攻击链

1. 第1题: olevba 提取 invitation.docm 宏
2. decodeAsHex + decodeChar 还原 base64
3. echo "JABzAD0A..." | base64 -d → HTB{5up3r_345y_m4cr05}
4. 第2题 DNS流量分析: tshark -r capture.pcap
5. rev: base64 + rev
6. HTB{j4v4_5pr1ng_just_b3c4m3_j4v4_sp00ky!!}
7. pwn: strcmp("sup3r_s3cr3t_p455w0rd_f0r_u!") + system("/bin/sh")
8. rev: printf 不可见字符过滤
9. HTB{h4unt3d_by_th3_gh0st5_0f_ctf5_p45t!}
10. web: PHP type juggling $2a$12 hash + docker

## 关键 payload

```
olevba.py invitation.docm → base64 -d → HTB{5up3r_345y_m4cr05}
```

## 经验教训

olevba是提取Office宏的标配工具

## 标签

htb、halloween、forensics、rev、pwn、web、olevba、base64、docker

## 参考来源

- https://www.ctfiot.com/75596.html
- 原文件：Hack_The_Boo_2022_CTF题目解析.full.md

---
title: "2025 高校网络安全管理运维赛-电子取证分析师赛道-决赛 WriteUp"
category: forensics
tags: ["2025 高校网络安全管理运维赛", "forensics", "高校网络安全管理运维赛 2025 决赛", "电子取证分析师", "签到题 gif 分帧组合扫码", "log 日志 awk 过滤"]
signals: ["2025 高校网络安全管理运维赛 2025", "高校网络安全管理运维赛 2025 决赛", "电子取证分析师", "签到题 gif 分帧组合扫码", "log 日志 awk 过滤", "MD5 11cd6a875898416+6c37ac826a2a04bc", "3c6e0b8a9c15224a 解密密钥", "pcap redis/1234567qwerc Caddy /usr/share/caddy/testinfo.php", "VeraCrypt 加密卷 SM3 校验", "forensic_disk", "forensic_memory", "misc_unknown", "GIF", "log"]
difficulty: medium
source: "https://www.ctfiot.com/278549.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 高校网络安全管理运维赛-电子取证分析师赛道-决赛 WriteUp

> 赛事：2025 高校网络安全管理运维赛 2025 | 方向：forensics | 难度：medium

## 一句话总结

2025 高校网络安全管理运维赛电子取证分析师决赛：签到 GIF + log awk + PACP pcap + Keepass + VeraCrypt + 勒索恢复 + RAID 对比。

## 攻击链

1. 签到: gif 分帧-组合-画图-拼接-扫码
2. 谁真正执行命令: log awk 过滤
3. 网络流量 MD5 解密: 11cd6a875898416+6c37ac826a2a04bc → 3c6e0b8a9c15224a
4. PACPdfir-pcap: flag{redis}, flag{1234567qwerc}, flag{/usr/share/caddy/testinfo.php}
5. DFIR-archer: 账户创建时间 2022-02-05 00:25:26
6. Keepass ironbox.safe 密码 PqR$34%sTuVwX
7. VeraCrypt SM3 校验: ce4a2f20ebc2bcdce729885ae12fb3de0a7231e6c0a8dc1cc050605f9f8f1663
8. DFIR-rensom: 用户 maaiyu, U 盘 jetflash
9. DFIR-RAID: lvscan + mount + diff -r back new

## 关键 payload

```
Keepass ironbox.safe → PqR$34%sTuVwX
```

## 经验教训

高校运维赛取证赛道覆盖签到/log/pcap/账户/Keepass/VeraCrypt/勒索/RAID 全栈；Keepass 主密码 PqR$34%sTuVwX 需 keepass2john + john 爆破；VeraCrypt SM3 是国密场景。

## 标签

高校网络安全管理运维赛 2025 决赛、电子取证分析师、签到题 gif 分帧组合扫码、log 日志 awk 过滤、MD5 11cd6a875898416+6c37ac826a2a04bc、3c6e0b8a9c15224a 解密密钥、pcap redis/1234567qwerc Caddy /usr/share/caddy/testinfo.php、VeraCrypt 加密卷 SM3 校验、Keepass ironbox.safe PqR$34%sTuVwX、用户名 maaiyu、U 盘 jetflash、RAID lvscan 挂载对比

## 参考来源

- https://www.ctfiot.com/278549.html
- 原文件：2025高校网络安全管理运维赛-电子取证分析师赛道-决赛WriteUp.full.md

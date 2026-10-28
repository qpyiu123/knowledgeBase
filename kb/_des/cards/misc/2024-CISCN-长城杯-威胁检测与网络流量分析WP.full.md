---
title: "2024 CISCN x 长城杯 威胁检测与流量分析 WP（zeroshell + WinFT）"
category: misc
tags: ["CISCN x 长城杯", "misc", "zeroshell防火墙", "CVE-2019-12725", "x509view命令注入", "Wireshark追踪TCP流"]
signals: ["CISCN x 长城杯 2024", "zeroshell防火墙", "CVE-2019-12725", "x509view命令注入", "Wireshark追踪TCP流", "Referer base64", "WinFT exe分析", "火绒剑", "PCHunter启动项", "stego_traffic", "rce", "forensic_disk", "misc_unknown", "Wireshark"]
difficulty: medium
source: "https://www.ctfiot.com/226315.html"
tools: ["IDA", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 CISCN x 长城杯 威胁检测与流量分析 WP（zeroshell + WinFT）

> 赛事：CISCN x 长城杯 2024 | 方向：misc | 难度：medium | 工具：IDA、Wireshark

## 一句话总结

Wireshark 追踪 Referer base64 + CVE-2019-12725 命令注入 + WinFT 火绒剑 PCHunter。

## 攻击链

1. Wireshark 打开 pcap → 搜 "exec" 关键字 → 定位 HTTP 包 → 追踪 TCP 流 → 解码 Referer base64 拿 flag → 找 zeroshell 漏洞 CVE-2019-12725 /cgi-bin/kerbynet?Action=x509view&x509type=''%0Aid%0A'' 命令注入 → 读 /DB/_DB.001/flag 与 /Database/flag → netstat 查外联 IP 202.115.89.103 → 找 /tmp/.nginx 木马 → IDA 找密钥 11223344qweasdzxc → 启动项 /var/register/system/startup/scripts/nat/File → WinFT 流量分析: 微步云沙箱判 exe 木马 + 火绒剑查外联 IP:PORT + PCHunter 启动项最后一行 flag + cyberchef 解密 + CTF-NetA 梭出分片压缩包

## 关键 payload

```
/cgi-bin/kerbynet?Action=x509view&Section=NoAuthREQ&x509type='%0Aid%0A' ; flag{c6045425-6e6e-41d0-be09-95682a4f65c4} ; flag{202.115.89.103} ; flag{.nginx} ; flag{11223344qweasdzxc} ; flag{/var/register/system/startup/scripts/nat/File}
```

## 经验教训

zeroshell 防火墙 x509view 接口 %0A 注入 16 年漏洞至今野外仍常见，防火墙类取证要查启动项。

## 标签

zeroshell防火墙、CVE-2019-12725、x509view命令注入、Wireshark追踪TCP流、Referer base64、WinFT exe分析、火绒剑、PCHunter启动项、CTF-NetA 压缩包

## 参考来源

- https://www.ctfiot.com/226315.html
- 原文件：2024-CISCN-长城杯-威胁检测与网络流量分析WP.full.md

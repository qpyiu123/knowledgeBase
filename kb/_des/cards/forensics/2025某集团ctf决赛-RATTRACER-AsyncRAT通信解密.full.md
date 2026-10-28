---
title: "2025 某集团 ctf 决赛 RATTRACER - AsyncRAT 通信解密（TLS 私钥 + gzip + MsgPack + RDP JPEG）"
category: forensics
tags: ["2025 某集团 ctf 决赛", "forensics", "RATTRACER 2025 决赛", "AsyncRAT-C-Sharp 开源项目", "ST.p12 PKCS#12 私钥", "openssl pkcs12 -info -in ST.p12 无密码"]
signals: ["2025 某集团 ctf 决赛 2025", "RATTRACER 2025 决赛", "AsyncRAT-C-Sharp 开源项目", "ST.p12 PKCS#12 私钥", "openssl pkcs12 -info -in ST.p12 无密码", "openssl pkcs12 -legacy -in ST.p12 -nocerts -nodes -out key.pem", "Wireshark TLS 解密 ip port 私钥", "1f 8b 08 gzip 头", "MsgPack 解析", "forensic_traffic", "pwn_unknown", "web_unknown", "RATTRACER", "p12"]
difficulty: hard
source: "https://www.ctfiot.com/285924.html"
tools: ["C", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 某集团 ctf 决赛 RATTRACER - AsyncRAT 通信解密（TLS 私钥 + gzip + MsgPack + RDP JPEG）

> 赛事：2025 某集团 ctf 决赛 2025 | 方向：forensics | 难度：hard | 工具：C、Wireshark

## 一句话总结

2025 某集团决赛 RATTRACER：ST.p12 私钥解 TLS + AsyncRAT 通信解密 gzip+MsgPack + RDP JPEG 截图提取 flag。

## 攻击链

1. 1. 看到证书 p12 → openssl pkcs12 -info -in ST.p12 检密码（无密码）
2. 2. openssl pkcs12 -legacy -in ST.p12 -nocerts -nodes -out key.pem 提私钥
3. 3. Wireshark → 编辑→首选项→protocols→tls → 填 ip port 私钥
4. 4. 解密后看到 AsyncRAT 特征（NYAN-x-CAT/AsyncRAT-C-Sharp 开源）
5. 5. 内层 = 1f 8b 08 gzip 头 → gunzip
6. 6. MsgPack 解析 (parseMsgPack readstring readbinary getbuflen)
7. 7. 0xc4 = short binary, 0xc6 = long binary
8. 8. JPEG SOI ffd8ffd8 / EOI ffd9 提取 RDP 远程桌面截图
9. 9. flag 在 RDP 截图里

## 关键 payload

```
1f 8b 08 gzip 头 + MsgPack 0xc4 0xc6 标记
```

## 经验教训

AsyncRAT 通信 = TLS 1.x 外层 + gzip+MsgPack 内层 + 0xc4/0xc6 binary 标记；p12 无密码直接 openssl 提私钥；Wireshark TLS 解密后用协议特征搜索开源项目代码分析。

## 标签

RATTRACER 2025 决赛、AsyncRAT-C-Sharp 开源项目、ST.p12 PKCS#12 私钥、openssl pkcs12 -info -in ST.p12 无密码、openssl pkcs12 -legacy -in ST.p12 -nocerts -nodes -out key.pem、Wireshark TLS 解密 ip port 私钥、1f 8b 08 gzip 头、MsgPack 解析、0xc4 0xc6 二进制标记、gzip_uncompress 批量、RDP JPEG ffd8 ffd9 提取、remoteDesktop- 流量

## 参考来源

- https://www.ctfiot.com/285924.html
- 原文件：2025某集团ctf决赛-RATTRACER-AsyncRAT通信解密.full.md

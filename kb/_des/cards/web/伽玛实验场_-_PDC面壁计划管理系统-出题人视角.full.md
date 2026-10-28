---
title: "伽玛实验场｜PDC面壁计划管理系统-出题人视角"
category: web
tags: ["VNCTF 2022 PDC面壁计划", "web", "aiortc", "WebRTC", "DTLS", "RSA->EC证书"]
signals: ["VNCTF 2022 PDC面壁计划 2022", "aiortc", "WebRTC", "DTLS", "RSA->EC证书", "token验证", "PK-SK映射", "substring漏洞", "DataChannel", "auth_bypass", "RSA", "token", "substring", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/100552.html"
tools: ["Python", "Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 伽玛实验场｜PDC面壁计划管理系统-出题人视角

> 赛事：VNCTF 2022 PDC面壁计划 2022 | 方向：web | 难度：hard | 工具：Python、Wireshark

## 一句话总结

aiortc WebRTC 证书从 RSA 改 EC + token 验证 substring PK 漏洞，借伟思身份 WebRTC 拿 flag。

## 攻击链

1. 附件包: aiortc 库 + app.py + cmdHostory + important.pcapng
2. diff aiortc 主分支与附件: RSA 改为 EC (SECP256R1) 证书体系变更
3. Wireshark 用 SSLKEYLOGFILE 解密 DTLS 信道
4. pcap 发现: tell2me?token=... + WebRTC SDP 交换 + DataChannel ''xiaolanlan:cat flag'' (Permission denied)
5. 漏洞: token 校验 substring PK 匹配 PK-SK 映射
6. 服务端遍历 pk2sk 如果 pkKey in pk (substring) → 拿到 sk
7. 攻击: 伪造 weisi 的 token, timeStamp 1674991453000 距今 < 600000ms
8. 用 伟思身份 (weisi=8d509c28896865f8640f328f30f15721) 建立 WebRTC Client
9. 重连重发 'xiaolanlan:cat flag' 拿 flag

## 关键 payload

```
token=md5(timestamp-sk)[:32]+timestamp+pk + WebRTC DataChannel xiaolanlan:cat flag
```

## 经验教训

字典 key in user_substring 漏洞 (应该用 == 严格匹配)；WebRTC 内网穿透靠 TUN/STUN 公司/学校可能判定违规；SSLKEYLOGFILE 通用 DTLS 解密法。

## 标签

aiortc、WebRTC、DTLS、RSA->EC证书、token验证、PK-SK映射、substring漏洞、DataChannel、RCE

## 参考来源

- https://www.ctfiot.com/100552.html
- 原文件：伽玛实验场_-_PDC面壁计划管理系统-出题人视角.full.md

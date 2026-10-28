---
title: "网鼎半决赛IoT-babyrtp"
category: misc
tags: ["网鼎半决赛 IoT", "misc", "IoT-pwn", "rtp-stream", "ffmpeg", "AES-encrypted-jpg"]
signals: ["网鼎半决赛 IoT 2024", "IoT-pwn", "rtp-stream", "ffmpeg", "AES-encrypted-jpg", "tshark-rtp-payload", "IPv4-validation", "HTTP-server-pwn", "IP-cam", "misc_unknown", "IoT-babyrtp", "IoT", "RTP", "binwalk"]
difficulty: medium
source: "https://www.ctfiot.com/218450.html"
tools: ["Wireshark", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 网鼎半决赛IoT-babyrtp

> 赛事：网鼎半决赛 IoT 2024 | 方向：misc | 难度：medium | 工具：Wireshark、tshark

## 一句话总结

网鼎半决赛IoT-babyrtp IoT固件RTP推流题,binwalk提取固件+HTTP server+url=参数IPv4验证+rtp_aes_push循环推流+Wireshark截RTP+AES解密flag.jpg。

## 攻击链

1. binwalk提取固件,分析pwn文件(usr文件夹)
2. 实现简单HTTP服务器:socket+bind(8080)+listen+accept+handle_request
3. handle_request调extract_url提取url=参数内容
4. extract_url检查"url="后内容是否为有效IPv4地址
5. 有效URL:返回s(IPv4地址),继续走if逻辑
6. 关键:push_stream使用rtp_aes_push for flag.jpg aes_key.bin [url] 5004
7. 推流命令:while true; do ./rtp_aes_push flag.jpg aes_key.bin [url] 5004; sleep 5; done
8. GET传参不能进入逻辑,改用POST传参
9. Wireshark/tshark截获RTP流,rtp.payload提取密文
10. AES解密(key=aes_key.bin)得flag.jpg

## 关键 payload

```
AES(key=aes_key.bin).decrypt(rtp_payload)
```

## 经验教训

IoT固件题要从bin开始,用binwalk提取文件系统;HTTP server常见url参数验证;rtp推流是IP camera常见协议,ffmpeg是核心库;AES加密的图片用tshark抓payload后解密。

## 标签

IoT-pwn、rtp-stream、ffmpeg、AES-encrypted-jpg、tshark-rtp-payload、IPv4-validation、HTTP-server-pwn、IP-cam、get-post、AES-decrypt

## 参考来源

- https://www.ctfiot.com/218450.html
- 原文件：网鼎半决赛IoT-babyrtp.full.md

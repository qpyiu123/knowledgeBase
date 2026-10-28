---
title: "DefCon REST-AND-ATTEST"
category: web
tags: ["DEFCON 31 (Quals 2023)", "web", "rust", "firmware", "attestation", "smart-lock"]
signals: ["DEFCON 31 (Quals 2023) 2023", "rust", "firmware", "attestation", "smart-lock", "socat", "uploader", "trusted-firmware", "reverse", "web_unknown", "DEFCON", "REST-AND-ATTEST", "Rust", "tcp4-listen"]
difficulty: hard
source: "https://www.ctfiot.com/118801.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DefCon REST-AND-ATTEST

> 赛事：DEFCON 31 (Quals 2023) 2023 | 方向：web | 难度：hard

## 一句话总结

DEFCON 31 REST-AND-ATTEST：智能锁固件证明Rust程序

## 攻击链

1. socat tcp4-listen:4444 fork exec:./wrapper.sh
2. wrapper.sh exec ./uploader
3. 菜单: upload/download/run/quit
4. 读取trusted_firmware.raw include_bytes!
5. get_new_image() 用户上传image
6. do_download() image to hex print
7. run_device() 启动SFM+launcher
8. SFM Secure Firmware Module 固件证明

## 关键 payload

```
get_new_image()? // user input image
```

## 经验教训

固件证明（attestation）基于Root of Trust的固件安全

## 标签

rust、firmware、attestation、smart-lock、socat、uploader、trusted-firmware、reverse

## 参考来源

- https://www.ctfiot.com/118801.html
- 原文件：DefCon_REST-AND-ATTEST.full.md

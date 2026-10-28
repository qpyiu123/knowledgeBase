---
title: "2024 中国工业互联网安全大赛智能家电行业赛道 writeup by Mini-Venom"
category: forensics
tags: ["智能家电行业赛道", "forensics", "BLE 协议 link key", "binwalk", "RSA gcdext 同模攻击", "vigor_router 路由器"]
signals: ["智能家电行业赛道 2024", "BLE 协议 link key", "binwalk", "RSA gcdext 同模攻击", "vigor_router 路由器", "命令注入", "shiro 反序列化", "Modbus 拼接图", "FINS 协议", "forensic_memory", "crypto_rsa", "web_unknown", "stego_traffic", "BLE"]
difficulty: medium
source: "https://www.ctfiot.com/197031.html"
tools: ["binwalk", "gmpy2", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 中国工业互联网安全大赛智能家电行业赛道 writeup by Mini-Venom

> 赛事：智能家电行业赛道 2024 | 方向：forensics | 难度：medium | 工具：binwalk、gmpy2、tshark

## 一句话总结

BLE+RSA gcdext+路由器注入+shiro 反序列化+Modbus 图拼接+libc XOR。

## 攻击链

1. BLE pcap link key 解压压缩包 / RSA 同模攻击 (e1=3, e2=17, gcdext) / vigor_router mainfunction.cgi keyPath 注入 / shiro 反序列化 / Modbus 35152 拼接图 / IEC104 ioa 提 flag / libc.so XOR 0x17 字符串解密

## 关键 payload

```
g, s, t = gmpy2.gcdext(3, 17) ; m = pow(c1, s, n) * pow(c2, t, n) % n ; from iroot(m, g)[0] ; tshark -r ics.pcapng -T fields -e modbus.regval_uint16 ; tshark -r 1.pcapng -T fields -e iec60870_asdu.ioa
```

## 经验教训

RSA 同模攻击 (e1, e2 互质) 必须用 gcdext 找逆元；工控流量 modbus 35152 是 PNG 起始 magic。

## 标签

BLE 协议 link key、binwalk、RSA gcdext 同模攻击、vigor_router 路由器、命令注入、shiro 反序列化、Modbus 拼接图、FINS 协议、IEC104 ioa、libc.so XOR 0x17

## 参考来源

- https://www.ctfiot.com/197031.html
- 原文件：2024中国工业互联网安全大赛智能家电行业赛道_writeup_by_Mini-Venom.full.md

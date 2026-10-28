---
title: "UniCTF 两道流量分析 WP"
category: forensics
tags: ["UniCTF (YunSee团队)", "forensics", "modbus", "opc_ua", "dns", "http"]
signals: ["UniCTF (YunSee团队) 2025", "modbus", "opc_ua", "dns", "http", "icmp", "snmp", "bkcrack", "xor_key_recover", "forensic_traffic", "YunSee", "flag", "BlueBreath", "XOR"]
difficulty: medium
source: "https://www.ctfiot.com/296062.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UniCTF 两道流量分析 WP

> 赛事：UniCTF (YunSee团队) 2025 | 方向：forensics | 难度：medium | 工具：C

## 一句话总结

YunSee 团队招新流量分析题，工厂应急响应 7 个 flag + BlueBreath XOR 加密 webshell 完整解密，HTTP+Modbus+OPC UA+SNMP 协议全接触。

## 攻击链

1. 工厂应急响应 (7 任务):Modbus 0x05/ff00 → OPC UA ReadRequest → DNS 解析 → TCP 首连时间 → HTTP Host/URI → ICMP seq=0x0123 → SNMP OID → BlueBreath:TCP 8000 端口 bkcrack PNG 头明文攻击 → POST /uploads/shell.php → gzip 1f8b08 已知头推 XOR key → 解密 webshell 流量

## 关键 payload

```
modbus.func_code==5 && modbus.data==ff:00 / bkcrack -C hint.zip -c hint.png -p png.header / KEY=b"dc3ef5ff0c670152" (16-byte XOR)
```

## 经验教训

Webshell 加密流量特征：gzip 头 1f 8b 08 是常见的"先压缩再异或"模板，可用已知明文反推 XOR key 头 9 字节再爆破。

## 标签

modbus、opc_ua、dns、http、icmp、snmp、bkcrack、xor_key_recover、gzip_known_plaintext、tcp_reassemble、webshell_decrypt、scada_forensic

## 参考来源

- https://www.ctfiot.com/296062.html
- 原文件：UniCTF_两道流量分析_WP.full.md

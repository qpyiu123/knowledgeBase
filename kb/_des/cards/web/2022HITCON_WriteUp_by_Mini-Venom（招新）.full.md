---
title: "2022 HITCON WriteUp by Mini-Venom (招新)"
category: web
tags: ["HITCON CTF 2022", "web", "HITCON", "RCE", "字符级爆破", "增量cookie"]
signals: ["HITCON CTF 2022 2022", "HITCON", "RCE", "字符级爆破", "增量cookie", "NodeJS", "child_process", "require", "Windows-driver", "ssrf", "rce", "web_unknown", "reverse", "cookie"]
difficulty: hard
source: "https://www.ctfiot.com/81488.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 HITCON WriteUp by Mini-Venom (招新)

> 赛事：HITCON CTF 2022 2022 | 方向：web | 难度：hard

## 一句话总结

HITCON 字符级增量 cookie 爆破 + NodeJS child_process RCE + Windows 驱动 IOCTL

## 攻击链

1. Web RCE: 字符级 cookie 增量爆破恢复 server 端 NodeJS 代码
2. NodeJS payload: global.a1=''child''; a1=a1+''_process''; b=require(a1); c1=''cat /flag-1e''+suffix; b.exec(c1)
3. ThreadPool(10) 并发 16 字符 payload 字符串每 1 字符顺序爆破
4. exploit 字符 1: ''global.a1 = ''child'' 字符串服务端 echo 回去
5. exploit 字符 2: 拼 ''a1 = a1 + ''_process'''' 等等
6. Reverse: Windows 驱动 IRP switch ByteOffset 0x222000..0x222070 调用 sub_1400014D0
7. sub_1400014D0(N) 把数据写到 byte_140013190+N 偏移
8. 0x222000 + N*0x10 触发不同全局变量初始化

## 关键 payload

```
global.a1='child'; a1=a1+'_process'; b=require(a1); c1='cat /flag-...'; b.exec(c1)
```

## 经验教训

增量 cookie 响应可逐字符爆破服务端代码；Windows 驱动 IOCTL 0x222000 是 32 字节间隔的 dispatch

## 标签

HITCON、RCE、字符级爆破、增量cookie、NodeJS、child_process、require、Windows-driver、IOCTL、IRP、0x222000

## 参考来源

- https://www.ctfiot.com/81488.html
- 原文件：2022HITCON_WriteUp_by_Mini-Venom（招新）.full.md

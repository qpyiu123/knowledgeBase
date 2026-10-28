---
title: "柏鹭杯2023 WP -Polaris战队"
category: pwn
tags: ["柏鹭杯2023", "pwn", "PWN eval/heap", "Java反序列化", "Redis SSH公钥注入", "Express.js"]
signals: ["柏鹭杯2023 2023", "PWN eval/heap", "Java反序列化", "Redis SSH公钥注入", "Express.js", "file协议", "RSA连分数", "维吉尼亚密码", "deserialize", "Polaris", "PWN", "Redis", "SSH", "Java"]
difficulty: medium
source: "https://www.ctfiot.com/139080.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 柏鹭杯2023 WP -Polaris战队

> 赛事：柏鹭杯2023 2023 | 方向：pwn | 难度：medium

## 一句话总结

柏鹭杯2023 Polaris战队综合WP：PWN+Redis SSH公钥+Java反序列化+Express file协议+RSA连分数+维吉尼亚

## 攻击链

1. PWN eval:one_gadget链调用→PWN heap:tcache+_IO_FILE结构+setcontext→Web综合7:读application.properties泄露redis端口+密码→写SSH公钥+config set dir+save→SSH免密登录→综合题6:Java反序列化+Runtime.exec反弹shell+suid dig提权→express js:file协议href/origin/protocol+双层URL编码flag.txt→综合5:XOR解密enc_flag1→Crypto rsa:连分数+leak=pow(p-q, num1, n)→d=invert(e)→p-q→p*q=n解p,q

## 关键 payload

```
eval:libc+0x52290+0x54310+0x1b45bd+0x23b6a;heap:guard+heap_addr+image_addr 0xEAD;redis-cli -x set xqq;config set dir /root/.ssh;config set dbfilename authorized_keys;continued_fraction(num3) convergents;pow(p-q, num1, num1*num2)
```

## 经验教训

Redis写authorized_keys免密登录+连分数求RSA p/q+Java反序列化Runtime反弹shell

## 标签

PWN eval/heap、Java反序列化、Redis SSH公钥注入、Express.js、file协议、RSA连分数、维吉尼亚密码

## 参考来源

- https://www.ctfiot.com/139080.html
- 原文件：柏鹭杯2023_WP_-Polaris战队.full.md

---
title: "DASCTF 2022 7 月赋能赛官方 Write Up"
category: web
tags: ["DASCTF", "web", "ssti-unicode", "phar-deser", "fakerphp", "golang-ssti"]
signals: ["DASCTF 2022", "ssti-unicode", "phar-deser", "fakerphp", "golang-ssti", "ua-spoof", "sys-auth-rc4", "docker-layer", "ssti", "DASCTF", "Web", "Misc", "HardFlask", "unicode"]
difficulty: medium
source: "https://www.ctfiot.com/50504.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2022 7 月赋能赛官方 Write Up

> 赛事：DASCTF 2022 | 方向：web | 难度：medium

## 一句话总结

DASCTF 2022 7 月赋能赛官方 WP，4 Web + 4 Misc + 取证综合。

## 攻击链

1. HardFlask: unicode 编码绕 SSTI 过滤
2. 盲注外带数据
3. 找 popen 子类(133) 触发命令
4. ezgetshell: phar 反序列化 + 条件竞争
5. NewSer: composer.json 泄露 + fakerphp 引用绕 __wakeup
6. 绝对防御: jsfinder + SQL 注入
7. 听说你是个侦探: 推理破压缩密码
8. 哆来咪: 圆周率索引提取
9. Colorful Strips: YCbCr vs RGB 还原
10. ez_forensics: vmdk+raw 取证

## 关键 payload

```
SSTI unicode 编码 + phar 反序列化 + 推理密码
```

## 经验教训

当 SSTI 过滤了 `__class__` 等关键字，unicode 编码 `\u005f\u005f...` 是万能绕法。

## 标签

ssti-unicode、phar-deser、fakerphp、golang-ssti、ua-spoof、sys-auth-rc4、docker-layer

## 参考来源

- https://www.ctfiot.com/50504.html
- 原文件：DASCTF｜2022DASCTF7月赋能赛官方Write_Up.full.md

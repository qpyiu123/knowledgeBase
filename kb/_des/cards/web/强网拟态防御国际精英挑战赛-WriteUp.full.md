---
title: "强网拟态防御/zerocalc"
category: web
tags: ["强网拟态", "web", "notevil patched eval", "cookieSession key 可控", "cookie pollution", "readFile"]
signals: ["强网拟态 2021", "notevil patched eval", "cookieSession key 可控", "cookie pollution", "readFile", "/etc/passwd 泄露", "/flag 随机名", "ssti", "ssrf", "rce", "notevil", "etc", "passwd", "cookieSession"]
difficulty: medium
source: "https://www.ctfiot.com/2601.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网拟态防御/zerocalc

> 赛事：强网拟态 2021 | 方向：web | 难度：medium

## 一句话总结

notevil 注入 readFile 读 /etc/passwd + 找 cookieSession secret 伪造 session

## 攻击链

1. 题目给 notevil（patched 过的 eval）但还接受额外 utils 参数
2. 注入：readFile('/etc/passwd') 直接读 /etc/passwd（notevil 不挡 fs.readFile）
3. cookieSession 用 Math.random().toString(16) 作 secret（弱但难爆破）
4. 注入读 /proc/self/environ 或 /proc/1/environ 找 secret
5. 用 secret 伪造 session 注入 cookieSession 污染
6. 注入 hi.unshift(`${e} = ${ret}`) 让历史记录显示任意内容
7. flag 路径随机：find / -name 'flag*' 2>/dev/null 遍历目录
8. 读 flag 文件

## 关键 payload

```
e = "readFile('/etc/passwd')
```

## 经验教训

patched" 库接受额外参数时仍可注入；cookieSession secret 用弱熵 Math.random 易被读 /proc 还原

## 标签

notevil patched eval、cookieSession key 可控、cookie pollution、readFile、/etc/passwd 泄露、/flag 随机名

## 参考来源

- https://www.ctfiot.com/2601.html
- 原文件：强网拟态防御国际精英挑战赛-WriteUp.full.md

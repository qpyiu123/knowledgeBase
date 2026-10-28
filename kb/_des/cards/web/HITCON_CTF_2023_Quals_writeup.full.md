---
title: "HITCON CTF 2023 Quals writeup"
category: web
tags: ["HITCON CTF 2023 Quals", "web", "node.js", "lisp.js", "jailbreak", "prototype-pollution"]
signals: ["HITCON CTF 2023 Quals 2023", "node.js", "lisp.js", "jailbreak", "prototype-pollution", "child_process", "execsync", "caller", "arguments", "web_unknown", "HITCON", "CTF", "Lisp", "jail"]
difficulty: hard
source: "https://www.ctfiot.com/135316.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON CTF 2023 Quals writeup

> 赛事：HITCON CTF 2023 Quals 2023 | 方向：web | 难度：hard | 工具：pwntools

## 一句话总结

HITCON CTF 2023 Lisp.js jail：递归caller 7次拿到module→execSync读flag

## 攻击链

1. Node.js 20-alpine + pwn.red/jail
2. Lisp.js v0.1.0 自定义语言
3. --disallow-code-generation-from-strings
4. --disable-proto=delete (防 __proto__ 删除)
5. 攻击: (let f (fun (x) (. f "caller"))) 反射
6. 递归caller七次拿module wrapper
7. 拿require参数+module.children[0].exports.extendedScope
8. extendedScope内置Object/Array/String+额外js互操作
9. 调用require("child_process").execSync("./readflag")
10. flag: hitcon{it_is_actually_a_node.js_jail_in_disguise!!}

## 关键 payload

```
7次 .caller拿module wrapper → require("child_process").execSync
```

## 经验教训

Function.caller + 递归拿Node.js module wrapper是Node jail经典逃逸

## 标签

node.js、lisp.js、jailbreak、prototype-pollution、child_process、execsync、caller、arguments

## 参考来源

- https://www.ctfiot.com/135316.html
- 原文件：HITCON_CTF_2023_Quals_writeup.full.md

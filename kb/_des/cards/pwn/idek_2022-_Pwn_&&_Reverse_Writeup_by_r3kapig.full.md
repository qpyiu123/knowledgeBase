---
title: "idek 2022: Pwn && Reverse Writeup by r3kapig"
category: pwn
tags: ["idekCTF", "pwn", "fmt-string", "canary-leak", "stack-leak", "ret2dlresolve"]
signals: ["idekCTF 2022", "fmt-string", "canary-leak", "stack-leak", "ret2dlresolve", "fmt-arg-overlap", "glibc-2.31", "pwn_unknown", "idekCTF", "r3kapig", "Pwn", "Reverse", "survey", "canary"]
difficulty: hard
source: "https://www.ctfiot.com/93115.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# idek 2022: Pwn && Reverse Writeup by r3kapig

> 赛事：idekCTF 2022 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

idekCTF 2022 r3kapig 战队 Pwn + Reverse 套题，survey 泄 canary + fmt-string 任意写。

## 攻击链

1. y' 进 survey
2. a'*11 输入泄 canary (8 字节覆盖)
3. a'*10 覆盖 canary 控 ret
4. a'*0x1a 泄 textaddr
5. 改返回地址 + 0x1273 偏移
6. leak_payload: pop rdi + fgets@got + printf@plt
7. 泄 libc
8. system("/bin/sh")
9. sprinter: fmt-string + 任意地址写
10. %9$hhn / %31$hhn / %33$n / %34$hhn 改写 strchr@got
11. ROP 链 system

## 关键 payload

```
格式化字符串 %9$hhn + canary 泄 + ret2dlresolve
```

## 经验教训

多步 fmt-string 利用要先泄 canary 再泄 textaddr 才能构造 ret 链。

## 标签

fmt-string、canary-leak、stack-leak、ret2dlresolve、fmt-arg-overlap、glibc-2.31

## 参考来源

- https://www.ctfiot.com/93115.html
- 原文件：idek_2022-_Pwn_&&_Reverse_Writeup_by_r3kapig.full.md

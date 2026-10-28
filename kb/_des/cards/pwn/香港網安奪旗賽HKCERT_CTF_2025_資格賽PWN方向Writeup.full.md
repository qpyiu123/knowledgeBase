---
title: "香港網安奪旗賽HKCERT CTF 2025 資格賽PWN方向Writeup"
category: pwn
tags: ["HKCERT CTF 2025 資格賽", "pwn", "fmtstr", "pwntools", "GOT-overwrite", "fmtstr_payload"]
signals: ["HKCERT CTF 2025 資格賽 2025", "fmtstr", "pwntools", "GOT-overwrite", "fmtstr_payload", "ret2libc", "ORW", "FSOP", "fake-io", "pwn_unknown", "HKCERT", "PWN", "PIE", "leak"]
difficulty: hard
source: "https://www.ctfiot.com/288942.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 香港網安奪旗賽HKCERT CTF 2025 資格賽PWN方向Writeup

> 赛事：HKCERT CTF 2025 資格賽 2025 | 方向：pwn | 难度：hard | 工具：pwntools

## 一句话总结

HKCERT 2025资格赛PWN方向5题集合,涵盖fmtstr基础题+PIE leak+GOT覆盖+ret2libc+ORW+musl FSOP fake IO_FILE。

## 攻击链

1. 第一题:Question Number 负数+Result数组下标system/bin_sh/prdi直接拼地址进数组
2. 第二题:fmtstr_payload(6, {printf_got: backdoor})覆盖printf GOT触发后门
3. 第三题:栈溢出0x70字节+0x10字节溢出覆盖返回地址+ret2libc ORW
4. 第四题:login用户删除后第二次add复用chunk+tcache泄露+edit越界
5. 第五题:musl libc pwn-IO fake IO_FILE构造+open/read/write三件套

## 关键 payload

```
fmtstr_payload(6, {printf_got: backdoor})
```

## 经验教训

fmtstr_payload偏移要从栈上找;musl的IO攻击面比glibc小很多,要自己分析__stdout_FILE结构体并构造fake io file。

## 标签

fmtstr、pwntools、GOT-overwrite、fmtstr_payload、ret2libc、ORW、FSOP、fake-io、libc-internal、musl-pwn

## 参考来源

- https://www.ctfiot.com/288942.html
- 原文件：香港網安奪旗賽HKCERT_CTF_2025_資格賽PWN方向Writeup.full.md

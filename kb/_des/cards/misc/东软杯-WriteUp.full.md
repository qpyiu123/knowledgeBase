---
title: "东软杯-WriteUp"
category: misc
tags: ["东软杯 / ChaMd5 Neusoft NSSCTF", "misc", "SSTI", "Jinja2", "模板上传", "压缩包密码爆破"]
signals: ["东软杯 / ChaMd5 Neusoft NSSCTF 2022", "SSTI", "Jinja2", "模板上传", "压缩包密码爆破", "DH bsgs", "AES-ECB", "BigInteger素数", "signal驱动VM", "misc_unknown", "SQL", "bsgs", "Java", "PWN"]
difficulty: medium
source: "https://www.ctfiot.com/15954.html"
tools: ["Flask", "Java", "Jinja2", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 东软杯-WriteUp

> 赛事：东软杯 / ChaMd5 Neusoft NSSCTF 2022 | 方向：misc | 难度：medium | 工具：Flask、Java、Jinja2、Python

## 一句话总结

东软杯 8 题混合栈：SSTI 模板上传 + SQL 盲注 + 压缩包爆破 + DH bsgs + Java 素数 + 3 道 PWN + signal 驱动 VM。

## 攻击链

1. 题 1: Python Flask 文件上传 + path 模板路径 + .tpl 含 {{system(''cat /flag'')}}
2. 题 2: ?user=* 通配 SQL 盲注 + ?pass= 密码校验
3. 题 3: 加密压缩包 yasuobao.zip 数字密码爆破
4. 题 4: DH 离散对数 bsgs(G, A, (0, 2^40)) → a=822690494337
5. key = pow(B, a, p) → AES-ECB key 16 字节
6. 题 5: Java BigInteger 素数测试 (Fermat + Miller-Rabin) + getPrime(1024)
7. 题 6 PWN: exit_got=setvbuf_got-1 改 setvbuf 为 0x4011A9 + ret2system
8. 题 7 PWN: pop_rdi + read@got + ret2libc 0x404020
9. 题 8 PWN: list 双向链表 + overwrite idx+libc 泄 + edit atoi_got=system
10. 题 9 RE: signal 驱动 VM sigaction(34-47) + mmap 0x200 共享内存
11. opcode=[17,52,0,42,...] 自定义指令 push/pop/add/sub/xor/call/ret/jmp/jz
12. sub_40144B 一次性注册 14 个信号 handler
13. dump 0x4019c0 opcode 流 + 模拟器反推

## 关键 payload

```
a=bsgs(G,A,(0,2^40))=822690494337 + setvbuf_got-1+0x4011A9 ret2system
```

## 经验教训

signal 驱动 VM 是 RE 高级形态，sigaction(34-47) 各绑 handler (push/pop/add/sub/xor/call/ret/jmp/jz) + mmap 共享内存 + 主进程通过 kill 给子进程发信号执行指令。

## 标签

SSTI、Jinja2、模板上传、压缩包密码爆破、DH bsgs、AES-ECB、BigInteger素数、signal驱动VM、sigaction

## 参考来源

- https://www.ctfiot.com/15954.html
- 原文件：东软杯-WriteUp.full.md

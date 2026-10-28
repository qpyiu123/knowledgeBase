---
title: "F.Z.N CTF网络安全大赛PWN方向题解"
category: pwn
tags: ["F.Z.N CTF", "pwn", "pwn", "canary", "stack-pivoting", "tcache-poisoning"]
signals: ["F.Z.N CTF 2024", "pwn", "canary", "stack-pivoting", "tcache-poisoning", "i386", "amd64", "ret2libc", "heap_exploit", "PWN", "stack_pivoting", "tcache", "poisoning", "backdoor"]
difficulty: medium
source: "https://www.ctfiot.com/282169.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# F.Z.N CTF网络安全大赛PWN方向题解

> 赛事：F.Z.N CTF 2024 | 方向：pwn | 难度：medium

## 一句话总结

F.Z.N PWN 3题：canary爆破+stack_pivoting+tcache poisoning

## 攻击链

1. 题1 canary (i386): 栈溢出覆盖返回backdoor(0x8049285)
2. 泄露canary: A*0x64+B 接收到\x00+3字节
3. 题2 stack_pivoting_x64: 栈迁移leave_ret
4. 泄露栈地址: A*0x28+B*8接收6字节
5. rsp_addr=stack_leak-0x40
6. 题3 attachment 堆题: tcache poisoning
7. 0x418+0x20unsorted bin leak libc (libc2.27 main_arena+96=0x3ebca0)
8. tcache 0x68改fd指向__free_hook
9. 分配两次第二次覆盖__free_hook=system
10. delete带/bin/sh的chunk触发system

## 关键 payload

```
edit(4, p64(__free_hook)); add(0x68, p64(system)); delete(7)  # /bin/sh
```

## 经验教训

栈迁移rsp=leak-0x40+leave_ret；tcache改fd指向__free_hook

## 标签

pwn、canary、stack-pivoting、tcache-poisoning、i386、amd64、ret2libc

## 参考来源

- https://www.ctfiot.com/282169.html
- 原文件：F.Z.N_CTF网络安全大赛PWN方向题解.full.md

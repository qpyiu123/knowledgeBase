---
title: "N1CTF 2023 pwn1OS writeup"
category: pwn
tags: ["N1CTF 2023", "pwn", "iOS_pwn", "Objective_C_msgSend", "NSData伪造", "addrof原语"]
signals: ["N1CTF 2023 2023", "iOS_pwn", "Objective_C_msgSend", "NSData伪造", "addrof原语", "arbitrary_read", "ISA泄漏", "ASLR绕过", "莫莫安全", "pwn_unknown", "N1CTF", "pwn1OS", "iOS", "addrof"]
difficulty: hard
source: "https://www.ctfiot.com/140328.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# N1CTF 2023 pwn1OS writeup

> 赛事：N1CTF 2023 2023 | 方向：pwn | 难度：hard | 工具：C

## 一句话总结

N1CTF 2023 pwn1OS：iOS addrof + arbitrary_read + ISA 泄漏 + ASLR 绕过。

## 攻击链

1. Objective-C 桥接：Bob* bob = [[Bob alloc] init]; [bob doSomething];
2. 漏洞：getFlag 接受 urlString + base64 flag 上送外网
3. JS 桥 addrof：捕获对象地址 n1ctf.challenge/setChallenge_
4. 任意地址读：make_nsdata(addr, len) 伪造 NSData + addMultiPartData_
5. ctf.dealloc 释放后 addMultiPartData_ 复用
6. CoreServiceClass 地址 = coreservice_isa & 0x0000000ffffffff8
7. ASLR = CoreServiceClass - offset
8. 远程 URL 拼 flag 外发

## 关键 payload

```
function addrof(obj) { ... /instance (0x[da-f]+)/ ... }
```

## 经验教训

iOS pwn 经典 addrof + arbitrary_read 组合；NSData 伪造是任意读核心；ISA + class mask 算 ASLR。

## 标签

iOS_pwn、Objective_C_msgSend、NSData伪造、addrof原语、arbitrary_read、ISA泄漏、ASLR绕过、莫莫安全

## 参考来源

- https://www.ctfiot.com/140328.html
- 原文件：N1CTF_2023_pwn1OS_writeup.full.md

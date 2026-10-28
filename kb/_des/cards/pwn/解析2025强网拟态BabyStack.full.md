---
title: "解析2025强网拟态BabyStack"
category: pwn
tags: ["强网拟态 2025 BabyStack", "pwn", "stack-overflow", "variable-overwrite", "No-PIE", "no-canary"]
signals: ["强网拟态 2025 BabyStack 2025", "stack-overflow", "variable-overwrite", "No-PIE", "no-canary", "NX-enabled", "pwntools-p64", "ROP-exploit", "read-256", "heap_exploit", "BabyStack", "read", "x1337abc", "shell"]
difficulty: easy
source: "https://www.ctfiot.com/276999.html"
tools: ["ROP", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态BabyStack

> 赛事：强网拟态 2025 BabyStack 2025 | 方向：pwn | 难度：easy | 工具：ROP、pwntools

## 一句话总结

强网拟态2025 BabyStack简单栈溢出,No-PIE+no-canary+NX,两次read(24/256),第二次248字节垃圾+8字节0x1337abc覆盖栈上v3变量,绕过if检查拿shell。

## 攻击链

1. ELF 64-bit LSB, Partial RELRO, No canary, NX enabled, No PIE
2. 程序:两次read()输入+一个pwn()函数
3. 关键:pwn()中第二次read允许输入256字节,可覆盖栈上的v3变量
4. 偏移计算:
5. 第一次read的buf大小:0x18=24字节
6. 第二次read起点:rbp-0x120+0x18=rbp-0x108
7. 第二次read大小:0x100=256字节
8. v3变量位置:rbp-0x10
9. 距离:0x108-0x10=0xf8=248字节
10. 关键:初始化v3=0xabc1337,检查v3==0x1337abc
11. Exploit:
12. 第一次:sa(b':',b'a'*0x18) 填充24字节
13. 第二次:s(b'a'*0xf8+p64(0x1337abc)) 248字节垃圾+8字节目标值
14. 触发:0x1337abc覆盖原v3,通过if检查
15. 获得:shell

## 关键 payload

```
b'a'*0xf8 + p64(0x1337abc)
```

## 经验教训

变量覆盖是栈溢出基础题,关键是计算read起点到目标变量的距离;初始化值与检查值不同(0xabc1337 vs 0x1337abc)是出题人故意设置的小陷阱。

## 标签

stack-overflow、variable-overwrite、No-PIE、no-canary、NX-enabled、pwntools-p64、ROP-exploit、read-256、pwn-menu、bypwn

## 参考来源

- https://www.ctfiot.com/276999.html
- 原文件：解析2025强网拟态BabyStack.full.md

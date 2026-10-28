---
title: "EHAX CTF 2026 Writeup by Mini-Venom"
category: web
tags: ["EHAX CTF 2026", "web", "pwn", "slice-uaf", "double-free", "built-in-func-ptr-overwrite"]
signals: ["EHAX CTF 2026 2026", "pwn", "slice-uaf", "double-free", "built-in-func-ptr-overwrite", "bytecode-vm", "aarch64", "web_unknown", "EHAX", "Slice", "UAF", "CrackMe", "AES", "pyc"]
difficulty: hard
source: "https://www.ctfiot.com/301285.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# EHAX CTF 2026 Writeup by Mini-Venom

> 赛事：EHAX CTF 2026 2026 | 方向：web | 难度：hard | 工具：Python

## 一句话总结

EHAX 2026 6题：Slice UAF+CrackMe AES+迷宫+智能合约+pyc

## 攻击链

1. Slice和Buffer共享data_ptr但GC不知道
2. Buffer被GC释放→Slice仍引用data_ptr
3. BUILTIN复用该chunk通过Slice PRINTB泄露func_ptr
4. Slice被GC再次释放同一data_ptr→double free
5. NEWBUF第二次获得同一chunk通过WRITEBUF覆写func_ptr
6. CALL builtin→跳转到execve("/bin/sh")
7. CrackMe: 8函数+32字节key约束z3求解
8. AES ghost key: key[:16] SHA256+AES-CBC key[16:] MD5 IV
9. 智能合约: EvilGov pwn() sstore(0,0) sstore(1,caller())
10. Python pyc: grid 10x10迷宫+N/S/E/W路径

## 关键 payload

```
func_ptr overwrite → execve("/bin/sh")
```

## 经验教训

Slice-Buffer共享data_ptr是GC漏判导致double-free经典模式

## 标签

pwn、slice-uaf、double-free、built-in-func-ptr-overwrite、bytecode-vm、aarch64、aarch64

## 参考来源

- https://www.ctfiot.com/301285.html
- 原文件：EHAX_CTF_2026_Writeup_by_Mini-Venom.full.md

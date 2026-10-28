---
title: "解析2025强网拟态Stack"
category: pwn
tags: ["强网拟态 2025 Stack", "pwn", "SROP", "sigreturn", "stack-pivot", "mprotect"]
signals: ["强网拟态 2025 Stack 2025", "SROP", "sigreturn", "stack-pivot", "mprotect", "BSS", "syscall", "openat", "sendfile", "pwn_unknown", "Stack", "shellcode", "No-PIE", "No-canary"]
difficulty: hard
source: "https://www.ctfiot.com/276775.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态Stack

> 赛事：强网拟态 2025 Stack 2025 | 方向：pwn | 难度：hard

## 一句话总结

强网拟态2025 Stack SROP+栈迁移+shellcode,No-PIE+No-canary+NX+Full RELRO,泄露栈+栈迁移到BSS+SROP调用mprotect(7=PROT_READ|WRITE|EXEC)+shellcode(openat/sendfile读flag)。

## 攻击链

1. 题目描述:"I don't need libc, and I guess you don't need it either" 不需要libc
2. 环境:No PIE+No canary+NX enabled+Full RELRO
3. 关键gadgets:
4. 0x40140e: syscall ; ret
5. 0x40121d: pop rbp ; ret
6. 0x4013b7: leave ; ret (栈迁移)
7. 思路:SROP (Sigreturn Oriented Programming)
8. 步骤:
9. 1. 泄露栈地址:printf("Hello, %s!") 后0x10字节填充
10. 2. 栈溢出0x60+8(rbp)+8(ret)→read到BSS段
11. 3. 在BSS段构造SROP frame
12. 4. syscall 15 (rt_sigreturn) 恢复所有寄存器
13. 5. 调用mprotect(bss, 0x100, 7) 修改BSS段为RWX
14. 6. 在BSS段执行shellcode
15. 7. shellcode: openat(-100, ''/flag'') + sendfile(1, ''rax'', 0, 0x50)
16. read返回字节数:15→触发rt_sigreturn
17. BSS页对齐:0x404000

## 关键 payload

```
SROP + mprotect(bss, 0x100, 7) + shellcode(openat+sendfile)
```

## 经验教训

SROP是绕过NX+Full RELRO+无libc环境的终极武器,关键是构造SigreturnFrame+read返回15触发rt_sigreturn;mprotect+BSS段是NX保护绕过的标准组合;openat+sendfile是Linux文件读取的稳定syscall。

## 标签

SROP、sigreturn、stack-pivot、mprotect、BSS、syscall、openat、sendfile、No-PIE、No-canary

## 参考来源

- https://www.ctfiot.com/276775.html
- 原文件：解析2025强网拟态Stack.full.md

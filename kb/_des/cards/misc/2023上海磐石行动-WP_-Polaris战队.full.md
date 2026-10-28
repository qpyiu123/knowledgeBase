---
title: "2023 上海磐石行动 WP - Polaris 战队"
category: misc
tags: ["2023 上海磐石行动", "misc", "keybox负数绕过", "off_by_one", "SROP", "mprotect栈执行"]
signals: ["2023 上海磐石行动 2023", "keybox负数绕过", "off_by_one", "SROP", "mprotect栈执行", "mybash_structural_confusion", "ret2dlresolve", "RSA", "RSA_repeated_squaring", "misc_unknown", "pwn", "keybox", "ssql", "x291"]
difficulty: hard
source: "https://www.ctfiot.com/119177.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 上海磐石行动 WP - Polaris 战队

> 赛事：2023 上海磐石行动 2023 | 方向：misc | 难度：hard | 工具：ROP

## 一句话总结

磐石行动 4 道 pwn：keybox 负数绕 + ssql 0x291+one_gadget + Hp SROP + mybash ucontext_t。

## 攻击链

1. keybox: 负数数组下标绕过 s[v5]=v4 (v5=-9223372036854775796)
2. edit 负索引 (-0x398) 覆盖 v9 指针，调用 end 替代 exit
3. add(0x18) + edit(-0x398, 8, p64(0x401765)[:7]) 写 ROP
4. ssql: column off-by-one + 0x291 fake size + hijack 链表
5. libc 2.35 _IO_list_all + 0x52290 one_gadget
6. Hp: HTTP 自定义解析器 + off-by-one + 8 字节部分写
7. 改 chunk size 0x0101 + fake IO_FILE 触发 _IO_wfile_jumps
8. SROP: pop rax=10 + mprotect(rdi=stack, rsi=0x1000, rdx=7) + shellcode
9. mybash: realloc 调整 chunk_size + strncpy 类型混淆
10. ucontext_t SROP: rsp+0x100 控制 rip/rsp
11. changeaddr: 写 4 字节到 0x804C020 改 putchar GOT
12. RE ezEXE: switch case 反编译 + 数组字符串
13. encrytor: 反复跑 process 等 flag.txt.enc 含 flag
14. WEB ezpython: 模板注入
15. Crypto twice: getpq from e*d-1 + k=k//2 + gcd(powmod(g,k,n)-1, n) 分解

## 关键 payload

```
first key = -9223372036854775796, second key = 1
```

## 经验教训

负数数组下标可绕过 s[v5]=v4 边界；off-by-one + 0x291 fake size 是经典菜单题；ucontext_t SROP 在 realloc 场景里特别好用。

## 标签

keybox负数绕过、off_by_one、SROP、mprotect栈执行、mybash_structural_confusion、ret2dlresolve、RSA、RSA_repeated_squaring、Polaris战队

## 参考来源

- https://www.ctfiot.com/119177.html
- 原文件：2023上海磐石行动-WP_-Polaris战队.full.md

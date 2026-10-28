---
title: "SECCON 2024 - 动态二进制插桩 trace 破解函数式编程混淆"
category: misc
tags: ["SECCON 2024", "misc", "functional-programming", "obfuscation", "cpp", "std-variant"]
signals: ["SECCON 2024 2024", "functional-programming", "obfuscation", "cpp", "std-variant", "std-shared_ptr", "pyda", "dynamic-binary-instrumentation", "sub_byte", "misc_unknown", "SECCON", "std", "variant", "shared_ptr"]
difficulty: hard
source: "https://www.ctfiot.com/220833.html"
tools: ["C", "IDA", "Python", "objdump"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON 2024 - 动态二进制插桩 trace 破解函数式编程混淆

> 赛事：SECCON 2024 2024 | 方向：misc | 难度：hard | 工具：C、IDA、Python、objdump

## 一句话总结

SECCON 2024 函数式编程混淆 C++ 逆向：std::variant + std::shared_ptr<Cons> 节点链表 + pyda 动态二进制插桩 trace cmp + Cons 节点 4 步加密 (sub_byte + mul + rotl + XOR) 还原。

## 攻击链

1. SECCON 2024 函数式编程混淆 C++ (std::variant + std::shared_ptr<Cons>)
2. IDA 逆向: ZNKR3fixIZ4mainEUlT_St7variantIJj... 模板函数链
3. level 1 _Function_handler::M_invoke
4. level 2 std::__invoke_r
5. level 3 std::__invoke_impl
6. level 4 main::lambda::operator()
7. level 5 Cons + variant 操作
8. Cons 节点 (rdi, rsi, rdx) 构造链表
9. pyda 动态二进制插桩 + objdump 找 cmp 位置
10. cmp_locs 解析 + p.hook(e.address+x, cmp_hook) 跟踪每次比较
11. 关键 cmp: 0x1891b rcx vs rdx 比较目标密文
12. 用户输入 ABCDEFGH 0x40 字节触发多次 cons() 调
13. 还原加密 4 步:
14. 1) sub_byte: 0x41414141 -> 0x4e4e4e4e (SubBytes AES-like)
15. 2) mul: 0x4e4e4e4e * 0xe14de95e = 0x93af4e5e (Galois mul)
16. 3) rotl(0x93af4e5e, 29) ^ rotl(0x93af4e5e, 17) ^ rotl(0xd36975c1, 7) ^ 0xe14de95e = 0xac0af82
17. 4) 再 sub_byte 0x4e4e4e4e (循环)
18. flag: SECCON{fUnCt10n4l_pRoGr4mM1n6_1s_pR4c7iC4lLy_a_pUr3_0bfu5c4T1oN}
19. gdb + ida + pyda backtrace 跟踪 0x8741 first_transform 函数
20. Cons 链表每节点 (rdi, rsi, rdx) -> (cons_value, op_target, next_cons)
21. Frame #6: 0x8741 = first_transform 调用入口
22. Frame #5: 0x3bfe = level 5 std::variant 操作
23. 完整调用栈: 0x1007c → 0x12afe → 0x1430f → ... → 0x8741
24. cmp @ 0x1891b rcx=0xc3df45f3 rdx=0x11793013 失败 = "Wrong
25. cmp @ 0x15787 rdx=0x100000001 rax=0x100000001 True 多次验证

## 关键 payload

```
pyda cmplog.py + p.hook(0x15a06, cons) 跟踪 Cons(rdi=0, rsi, rdx) 节点
```

## 经验教训

函数式编程混淆 (variant + shared_ptr<Cons>) 是高级 C++ 反混淆难点；pyda 动态二进制插桩跟踪 cmp/cons 节点是还原 Cons 链表算法的高阶工具；cmp 位置 + cmp 值对比可爆破密钥。

## 标签

functional-programming、obfuscation、cpp、std-variant、std-shared_ptr、pyda、dynamic-binary-instrumentation、sub_byte、mul、rotl、sbox、cons-trace

## 参考来源

- https://www.ctfiot.com/220833.html
- 原文件：SECCON_2024：动态二进制插桩trace_破解函数式编程混淆.full.md

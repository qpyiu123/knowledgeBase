---
title: "从新生赛入门PWN"
category: pwn
tags: ["新生赛 PWN 入门", "pwn", "canary绕过", "栈迁移", "ret2csu", "ret2text"]
signals: ["新生赛 PWN 入门 2022", "canary绕过", "栈迁移", "ret2csu", "ret2text", "fmtstr", "fini_array", "yellowgot", "treasure", "pwn_unknown", "bad_c0de", "PWN", "canary", "ret2libc"]
difficulty: medium
source: "https://www.ctfiot.com/99155.html"
tools: ["C", "C++"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从新生赛入门PWN

> 赛事：新生赛 PWN 入门 2022 | 方向：pwn | 难度：medium | 工具：C、C++

## 一句话总结

bad_c0de 新生赛 11 题 PWN 入门：canary/ret2csu/fmtstr/C++虚函数/ret2libc/orw。

## 攻击链

1. 题 1 pivot: canary 0x28+7 字节截断 + start=0x4010d0 栈迁移
2. 二次输入 0x37 字节泄 libc_base=u64(r(6))-128-0x29d10
3. ret2libc: pop_rdi+binsh+ret+system
4. 题 2 ret2csu: pop_rdi=0x4012b3 + write(1, write_got, 8) 泄 libc + main 重入
5. 题 3 ret2text: 0x4011e5 0x108 溢出覆盖返回地址
6. 题 4 fmtstr_level2: fini_array=0x4031f0 改 start + %15$s 泄 puts + puts_got 改 system
7. 题 5 yellowgot: 任意地址读 puts_got + pop_rax 链 close+read+open+read+puts
8. pop_rdi=0x23b6a, pop_rsi=0x2601f, pop_rdx=0x142c92, pop_rax=0x36174
9. 改 __stack_chk_fail=puts plt + atoi=gets
10. 题 6 treasure C++ 虚函数: UndiscoveredTreasure.description + edit 越界写 RareTreasure.description=DESC_FUNC* 指向 backdoor 0x40257A
11. 题 7 ret2libc: pop_rdi+puts_got+puts_plt+main 泄 libc + 二次溢出 system
12. 题 8 fmtstr_level1.5: %9011c%8$n + p64(0x4040A0) 写 4 字节
13. 题 9 ez_backdoor: 0x108+0x4011D2 ret
14. 题 10 smash: 0x1f8+p64(0x404060) 覆盖 flag_addr
15. 题 11 Catcat: %35$p 泄 libc + edit 0x20 字节 + one_gadget 0x50a37

## 关键 payload

```
9 题 PWN 题库：canary+栈迁移+ret2csu+fmtstr+虚函数+one_gadget
```

## 经验教训

canary 截断 7 字节 + '\x10' 末尾恢复；ret2csu 用 0x4012aa 0x401290 中间跳板；fini_array 写 fini_array[0]=start 触发 backdoor；C++ 虚函数 vtable 改写 + edit 越界写 description = backdoor 地址。

## 标签

canary绕过、栈迁移、ret2csu、ret2text、fmtstr、fini_array、yellowgot、treasure、ret2libc、one_gadget

## 参考来源

- https://www.ctfiot.com/99155.html
- 原文件：从新生赛入门PWN.full.md

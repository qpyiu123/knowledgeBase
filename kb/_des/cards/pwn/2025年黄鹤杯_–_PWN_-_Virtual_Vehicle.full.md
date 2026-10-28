---
title: "2025 黄鹤杯 PWN Virtual_Vehicle（VM 逆向+VM PWN+seccomp）"
category: pwn
tags: ["2025 黄鹤杯", "pwn", "黄鹤杯 2025 PWN Virtual_Vehicle", "自定义 VM 逆向+VM PWN", "vtable 8 个函数指针 (push_from_reg/push_from_imm/pop_to_reg/add_reg2_reg3_to_reg1/sub/mul/load/print)", "heap 0x1000 ope 字节码"]
signals: ["2025 黄鹤杯 2025", "黄鹤杯 2025 PWN Virtual_Vehicle", "自定义 VM 逆向+VM PWN", "vtable 8 个函数指针 (push_from_reg/push_from_imm/pop_to_reg/add_reg2_reg3_to_reg1/sub/mul/load/print)", "heap 0x1000 ope 字节码", "hashtable mmap RWX 0x1000", "seccomp-tools 沙箱", "KILL execve", "init_process() 初始化", "vm", "shellcode", "rop", "seccomp", "PWN"]
difficulty: hard
source: "https://www.ctfiot.com/271973.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 黄鹤杯 PWN Virtual_Vehicle（VM 逆向+VM PWN+seccomp）

> 赛事：2025 黄鹤杯 2025 | 方向：pwn | 难度：hard

## 一句话总结

2025 黄鹤杯 PWN Virtual Vehicle：自定义 VM 字节码 + vtable 8 函数指针 + seccomp 禁 execve + hashtable RWX 段喷 shellcode。

## 攻击链

1. seccomp-tools 检查：禁 execve（KILL 0xc000003e != 0x3b），其他 ALLOW
2. 喷 shellcode 到 mmap 0x1000 RWX 段
3. main 9 种操作 → vtable 8 个函数指针
4. 字节码 choide (4字节) + arg (n*4字节)
5. 覆盖 vtable 指针或 hashtable 内容 → 控制流劫持
6. 9 种操作 + print_data 喷出 flag
7. 实际与车联网无关，是 VM 逆向+VM PWN

## 关键 payload

```
vtable 8 个函数指针 + hashtable RWX mmap 0x1000
```

## 经验教训

VM PWN 套路：先反汇编字节码格式（choide+arg），再算 op 总数与 vtable 索引对应关系，seccomp-tools dump 是必做；本题实际是 VM 逆向（字节码 op）+ VM PWN（控制流劫持）混合。

## 标签

黄鹤杯 2025 PWN Virtual_Vehicle、自定义 VM 逆向+VM PWN、vtable 8 个函数指针 (push_from_reg/push_from_imm/pop_to_reg/add_reg2_reg3_to_reg1/sub/mul/load/print)、heap 0x1000 ope 字节码、hashtable mmap RWX 0x1000、seccomp-tools 沙箱、KILL execve、init_process() 初始化、main 9 种操作 8 种通过 vtable、喷 shellcode 到 RWX

## 参考来源

- https://www.ctfiot.com/271973.html
- 原文件：2025年黄鹤杯_–_PWN_-_Virtual_Vehicle.full.md

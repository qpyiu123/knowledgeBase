---
title: "Understanding Dirty Pagetable – m0leCon Finals 2023 CTF Writeup"
category: pwn
tags: ["m0leCon Finals 2023", "pwn", "linux_kernel", "modprobe_path", "dirty_pagetable", "commit_creds"]
signals: ["m0leCon Finals 2023 2023", "linux_kernel", "modprobe_path", "dirty_pagetable", "commit_creds", "find_task_by_vpid", "switch_task_namespaces", "copy_fs_struct", "kpti_trampoline", "rop", "m0leCon", "Finals", "Linux", "PWN"]
difficulty: hard
source: "https://www.ctfiot.com/151200.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Understanding Dirty Pagetable – m0leCon Finals 2023 CTF Writeup

> 赛事：m0leCon Finals 2023 2023 | 方向：pwn | 难度：hard

## 一句话总结

m0leCon Finals 2023 决出的 Linux 内核 PWN 题 Dirty Pagetable 完整 shellcode 复盘，覆盖 kaslr 定位+提权+namespace+fs+KPTI bypass 完整六件套。

## 攻击链

1. 通过 modprobe_path 触发自定义 shellcode → call a:pop r15 取 kaslr offset → commit_creds(init_cred) → find_task_by_vpid(1) → switch_task_namespaces(task, init_nsproxy) → copy_fs_struct(init_fs) → find_task_by_vpid(getpid()) → 改 current->fs=0x740 → kpti_bypass 跳回用户态

## 关键 payload

```
lea rdi, [r15 + init_cred] / mov [rsp+0x00], rax (zero) / mov [rsp+0x10], 0x2222222222222222 (win) / mov rax, 0x3333333333333333 (cs)
```

## 经验教训

Linux kernel exploit 的 6 步经典链：commit_creds(init_cred) → find_task_by_vpid(1) → switch_task_namespaces → copy_fs_struct → 改 current->fs → kpti_trampoline 跳回。

## 标签

linux_kernel、modprobe_path、dirty_pagetable、commit_creds、find_task_by_vpid、switch_task_namespaces、copy_fs_struct、kpti_trampoline、userfaultfd、custom_shellcode、ret2usr_64

## 参考来源

- https://www.ctfiot.com/151200.html
- 原文件：Understanding_Dirty_Pagetable_–_m0leCon_Finals_2023_CTF_Writeup.full.md

---
title: "2023 ACTF writeup by Arr3stY0u"
category: pwn
tags: ["2023 ACTF", "pwn", "ACTF", "QEMU-pwn", "qemu-system-x86_64", "MMIO"]
signals: ["2023 ACTF 2023", "ACTF", "QEMU-pwn", "qemu-system-x86_64", "MMIO", "PMIO", "iopl", "OOB", "fpga", "heap_exploit", "pwn_unknown", "web_unknown", "reverse", "QEMU"]
difficulty: insane
source: "https://www.ctfiot.com/142224.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 ACTF writeup by Arr3stY0u

> 赛事：2023 ACTF 2023 | 方向：pwn | 难度：insane

## 一句话总结

2023 ACTF：QEMU 用户态 pwn + io_uring + MMIO/PMIO + 自写 loader

## 攻击链

1. Q1 BabyNote: tcache dup 任意地址写, tcache_perthread_struct 攻击 → __free_hook = system
2. Q2 QEMU pwn: MMIO/PMIO 攻击 qemu-system-x86_64 模拟器, iopl(3) 拿 I/O 权限, leak qemu/elf base, 写 shellcode
3. Q3 flashhacker: ACTF{REv3rsE_2_bE_A_fLAshH4cK3r_c001}
4. Q4 QEMU seccomp: BPF 沙箱限制 read/write/open, 用 name_to_handle_at/open_by_handle_at 绕过
5. Q5 fxxk: io_uring + sendmmsg 走 ORW (open via io_uring_prep_openat + sendmmsg 把 mmap 数据发给 server)
6. Q6 memfd + mmap + recv 自写 loader 加载 ELF 反弹

## 关键 payload

```
leak_u64(heap_base + 0x000e28) - 0xa23d4f = qemu-system-x86_64 base
```

## 经验教训

QEMU 用户态逃逸是 2023+ 高级 pwn；io_uring + sendmmsg 可绕 seccomp；MMIO/PMIO 直接打设备

## 标签

ACTF、QEMU-pwn、qemu-system-x86_64、MMIO、PMIO、iopl、OOB、fpga、PCI-device、BabyNote-tcache、blob-arena、io_uring、sendmmsg、seccomp-bpf、libc-2.23

## 参考来源

- https://www.ctfiot.com/142224.html
- 原文件：2023_ACTF_writeup_by_Arr3stY0u.full.md

---
title: "corCTF 2023 sysruption SYSRET bug 利用学习"
category: misc
tags: ["corCTF", "misc", "Linux-Kernel", "SYSRET", "canonical-address", "EntryBleed"]
signals: ["corCTF 2023", "Linux-Kernel", "SYSRET", "canonical-address", "EntryBleed", "KASLR-bypass", "side-channel", "qemu-host-cpu", "x86_64", "misc_unknown", "corCTF", "sysruption", "Linux", "Kernel"]
difficulty: hard
source: "https://www.ctfiot.com/166547.html"
tools: ["Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# corCTF 2023 sysruption SYSRET bug 利用学习

> 赛事：corCTF 2023 | 方向：misc | 难度：hard | 工具：Rust

## 一句话总结

corCTF 2023 sysruption：Linux Kernel 6.3.4 删除 SYSRET canonical 检查 + EntryBleed 侧信道绕过 KASLR，内核 RCE。

## 攻击链

1. qemu-system-x86_64 -cpu host -enable-kvm + Linux 6.3.4
2. -cpu host 触发 EntryBleed 侧信道，绕过 KASLR
3. Patch entry_64.S: 删除 SYSRET 前的 canonical address check
4. shl $(64 - (__VIRTUAL_MASK_SHIFT+1)), %rcx + sar + cmpq %rcx, %r11 + jne slow_exit
5. 删除后, SYSRET 返回 non-canonical RCX/RIP 在内核态 #GP
6. 本质让用户接管内核，因为用户态控制 RSP
7. 用户态 syscall → 内核态处理 → SYSRET 跳 non-canonical → #GP 异常
8. #GP 处理路径用户可控 → 内核代码执行
9. 利用：构造特定 non-canonical 地址 + 准备 #GP handler

## 关键 payload

```
qemu -cpu host + EntryBleed + 删除 canonical check + SYSRET non-canonical RCX/RIP + #GP 用户态控制
```

## 经验教训

SYSRET canonical check 是 Intel/AMD 长期存在的硬件 bug 缓解措施，删除后用户态可控制内核 RSP 触发内核执行。

## 标签

Linux-Kernel、SYSRET、canonical-address、EntryBleed、KASLR-bypass、side-channel、qemu-host-cpu、x86_64、FizzBuzz101、Crusaders-of-Rust

## 参考来源

- https://www.ctfiot.com/166547.html
- 原文件：以_corCTF_2023_sysruption_学习_sysret_bug_的利用.full.md

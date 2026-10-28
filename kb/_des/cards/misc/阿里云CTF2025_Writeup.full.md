---
title: "阿里云 CTF 2025 Writeup"
category: misc
tags: ["阿里云CTF", "misc", "alibaba", "BPF", "verifier", "eBPF"]
signals: ["阿里云CTF 2025", "alibaba", "BPF", "verifier", "eBPF", "mmap", "read-only-bypass", "CUDA", "PTX", "misc_unknown", "Alibaba", "CTF", "map", "RCE"]
difficulty: hard
source: "https://www.ctfiot.com/229002.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 阿里云 CTF 2025 Writeup

> 赛事：阿里云CTF 2025 | 方向：misc | 难度：hard

## 一句话总结

Alibaba CTF 2025 多方向题：eBPF 只读 map verifier 缺陷实现只读内存写入 RCE + mba 整数溢出绕自检 + CUDA PTX AES 逆向。

## 攻击链

1. 内核 bpf 扩展函数 alimem_mmap 把物理页 mmap 到用户空间实现零拷贝
2. bpf_func 接受 const 指针 1 与 const 指针 3，size=8，将 *ptr1 异或 2025 写 *ptr3
3. bpf verifier 在 LD 只读 map 时会预载入值，因此即便 pointer 3 实际指向 readonly map 也会通过校验
4. 内核执行时绕过 readonly 标记，实现只读内存写入 → 内核 RCE
5. 数学表达式侧：构造 99999999*(x^y) 12 次累加触发 64 位整数溢出
6. 表达式原值不等于溢出后值 → 绕过 expr!=expr 自检
7. RE 侧 dump PTX 提取 256 字节 S-box T 与逆表 RT，按 AES 标准逆出 flag

## 关键 payload

```
99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)+99999999*(x^y)
```

## 经验教训

eBPF verifier 对只读 map 的预载入是经典绕过点（Map pre-load attack），用户空间的 mmap 物理页可被任意读写，配合 verifier 的提前优化形成只读页写洞。

## 标签

alibaba、BPF、verifier、eBPF、mmap、read-only-bypass、CUDA、PTX、AES、mba-overflow、kernel

## 参考来源

- https://www.ctfiot.com/229002.html
- 原文件：阿里云CTF2025_Writeup.full.md

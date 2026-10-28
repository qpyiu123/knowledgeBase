---
title: "Unknown (smoothie_operator)"
category: pwn
tags: ["Unknown CTF", "pwn", "shared_ptr", "oob_write_0xff", "tcache_poisoning", "fastbin_attack"]
signals: ["Unknown CTF 2022", "shared_ptr", "oob_write_0xff", "tcache_poisoning", "fastbin_attack", "smallbin_consolidate", "free_hook_overwrite", "fake_chunk_in_string", "shared_ptr_vtable", "heap_exploit", "OOB", "write", "UAF", "free_hook"]
difficulty: hard
source: "https://www.ctfiot.com/78940.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Unknown (smoothie_operator)

> 赛事：Unknown CTF 2022 | 方向：pwn | 难度：hard | 工具：C

## 一句话总结

高级 C++ shared_ptr 堆利用 OOB write + UAF 重叠字符串指针 + 双重 free_hook 覆写 + 字符串内嵌 /bin/sh，flag: Sh4r3d_ptrs_R_sm00th$。

## 攻击链

1. Monster::edit_params 输入 0 触发 OOB write quantities[0xff] → 对齐 pastry 对象 0xff*4 字节 → edit_monster 覆写 shared_ptr control block counter=0 → 触发 shared_ptr 析构泄漏 heap+libc → consolidate 0x2000 chunk 触发 smallbin 残留 main_arena+0x128 → 7 次 fill+resolve 翻转 tcache/fastbin → 制造 UAF 重叠字符串指针 → edit_pastry 改 ptr 指向 free_hook → edit_complaint 写入 system → add_complaint '/bin/sh' → free 触发 system("/bin/sh")

## 关键 payload

```
edit_monster(33, 0, 0, 20, 20) # overwrites counter of shared pointer instances to 0 / free_hook = glibc_addr + 0x2248 / system = free_hook - 0x19cbb8
```

## 经验教训

shared_ptr 引用计数被 OOB 写 0 后析构会释放 string 内存但保留 pastry 引用，是堆重叠+任意地址写的关键原语。

## 标签

shared_ptr、oob_write_0xff、tcache_poisoning、fastbin_attack、smallbin_consolidate、free_hook_overwrite、fake_chunk_in_string、shared_ptr_vtable

## 参考来源

- https://www.ctfiot.com/78940.html
- 原文件：Unknown.full.md

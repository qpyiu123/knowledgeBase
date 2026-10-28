---
title: "ZJCTF2021 Reverse - Triple Language"
category: misc
tags: ["ZJCTF 2021", "misc", "unicorn_engine", "mips_emulation", "arm_emulation", "x86_64_host"]
signals: ["ZJCTF 2021 2021", "unicorn_engine", "mips_emulation", "arm_emulation", "x86_64_host", "multi_arch_validate", "custom_hook_callback", "ctf_crc32_table_brute", "base64_decode_xor", "heap_exploit", "ZJCTF", "Triple", "Language", "x86"]
difficulty: hard
source: "https://www.ctfiot.com/36904.html"
tools: ["ARM", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ZJCTF2021 Reverse - Triple Language

> 赛事：ZJCTF 2021 2021 | 方向：misc | 难度：hard | 工具：ARM、x86/x64

## 一句话总结

ZJCTF 2021 Triple Language 逆向：x86 主程序 + Unicorn 模拟 MIPS+ARM 双架构 + 自定义 hook 改寄存器 + CRC32 表爆破前 4 字符 + Base64-style 字符重组还原 flag。

## 攻击链

1. 主程序 + unicorn.dll + uc_open(3=MIPS, 4=ARM) 双架构模拟 → MIPS 段 0x10000：输入前 6 字符 × "zjgcjy" = {0x2F2E, 0x282A, 0x2C42, 0x2A8A, 0x13E0, 0x36D4} 反推 "cann0t" → 后 16 字符 x-y=key1, x+y=key2 解方程 "be_t0o_carefu1" → ARM 段 0x200000：自定义 hook 改 r3 寄存器 → Base64-style 字符重组 3+2+1 位 split + chunk 16 字节 base64 编码 → CRC32 验证前 4 字符爆破 "when" → flag: cann0t_be_t0o_carefu1_when_faclng_ianguage

## 关键 payload

```
MIPS_CODE @0x10000 + uc_reg_read(t1..t6) == {0x2F2E,0x282A,0x2C42,0x2A8A,0x13E0,0x36D4} / ARM_CODE @0x200000 + v3 += 15, v3 ^= 0x6F 等 hook 操作 / key1={0xFC,0x1,0xF3,0xFA,0xE,0xBB,0x3E,0x0} / key2={0xC2,0xC3,0xD7,0xC4,0xDA,0xA5,0xA0,0xBE} / res[]={0x38,0x57,0x3A,0x42,...,0x31} 后 22 字节
```

## 经验教训

Unicorn + Capstone 是跨架构逆向的黄金组合，hook 机制 + 寄存器读/写是观察嵌入式代码执行流的标配；CRC32 验证 4 字符爆破速度足够快。

## 标签

unicorn_engine、mips_emulation、arm_emulation、x86_64_host、multi_arch_validate、custom_hook_callback、ctf_crc32_table_brute、base64_decode_xor、character_split_3_2_1、unicorn_capstone_disasm

## 参考来源

- https://www.ctfiot.com/36904.html
- 原文件：ZJCTF2021_Reverse-Triple_Language.full.md

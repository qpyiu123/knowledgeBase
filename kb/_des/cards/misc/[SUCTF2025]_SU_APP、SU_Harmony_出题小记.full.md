---
title: "[SUCTF2025] SU_APP、SU_Harmony 出题小记"
category: misc
tags: ["SUCTF 2025", "misc", "android_native_re", "frida_hook", "android_dlopen_ext", "fread_buffer_overwrite"]
signals: ["SUCTF 2025 2025", "android_native_re", "frida_hook", "android_dlopen_ext", "fread_buffer_overwrite", "sofixer_dump", "function_similarity_hash", "custom_isa_z3_solve", "14_type_classification", "reverse", "SUCTF", "SU_APP", "Android", "Frida"]
difficulty: hard
source: "https://www.ctfiot.com/226563.html"
tools: ["C", "IDA", "Python", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [SUCTF2025] SU_APP、SU_Harmony 出题小记

> 赛事：SUCTF 2025 2025 | 方向：misc | 难度：hard | 工具：C、IDA、Python、Z3

## 一句话总结

SUCTF 2025 SU_APP Android 逆向：Frida hook android_dlopen_ext+fread 改写返回 ret 0x50 + SoFixer 修复 + 自定义 256 函数 ISA 14 类型聚类 + Z3 求解 32 字节 flag。

## 攻击链

1. SU_APP:Frida hook android_dlopen_ext → suapp 路径时 NativeHook → 0xA158 randcode 收集 + 0x9FA8 重置 + hook fread count==8 时改写 [0x50,0x00,0x00,0x58,0x00,0x02,0x1f,0xd6] 返回 ret 0x50 → SoFixer-Windows-64 修复 → IDA Python 批量重命名 + md5 哈希聚类 14 类型 (type1-14) → 自定义 ISA 6 字节一指令 (a,b,c,indexA,indexB,logic) → C++ type1-14 模板 → Z3 Python 求解 32 字节输入

## 关键 payload

```
Interceptor.attach(dlopen, onEnter) + Interceptor.attach(0xA158, onLeave retval) / Memory.writeByteArray(buffer, [0x50,0x00,0x00,0x58,0x00,0x02,0x1f,0xd6]) / getType(opcode) → 14 types / type1-14 a[] = expression / Z3 BitVec 32
```

## 经验教训

Frida hook fread/strcmp/memcmp 在 count 固定时改写返回值是 anti-debug 通用绕过；自定义 ISA 逆向中"md5 哈希聚类函数类型"是 CTF 高效还原利器。

## 标签

android_native_re、frida_hook、android_dlopen_ext、fread_buffer_overwrite、sofixer_dump、function_similarity_hash、custom_isa_z3_solve、14_type_classification、256_func_bytecode_clustering、instruction_lifting

## 参考来源

- https://www.ctfiot.com/226563.html
- 原文件：[SUCTF2025]_SU_APP、SU_Harmony_出题小记.full.md

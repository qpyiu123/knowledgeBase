---
title: "Aliyun 2025 easy-cuda-rev - PTX 汇编 + CUDA 加速"
category: reverse
tags: ["AliyunCTF", "reverse", "CUDA", "PTX", "sm_52", "cuobjdump"]
signals: ["AliyunCTF 2025", "CUDA", "PTX", "sm_52", "cuobjdump", "AES T-table", "ROT循环", "mov.u64 %SPL __local_depot0", "vprintf", "reverse", "Aliyun", "easy-cuda-rev", "T-table", "bit"]
difficulty: hard
source: "https://www.ctfiot.com/232133.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Aliyun 2025 easy-cuda-rev - PTX 汇编 + CUDA 加速

> 赛事：AliyunCTF 2025 | 方向：reverse | 难度：hard

## 一句话总结

Aliyun 2025 easy-cuda-rev — CUDA PTX 汇编 sm_52 + 5 段 10485760 轮 T-table 查表 + 4-bit swap + XOR 索引 + GPU 加速爆破 + vprintf 逐字节输出。

## 攻击链

1. cuobjdump -ptx easy_cuda 提取 PTX 汇编
2. arch=sm_52, code version=[8,0], compressed
3. T[256] AES T-table (S-box + MixColumns)
4. RT[256] 逆 T-table
5. encrypt_kernel 入口 mov.u64 %SPL, __local_depot0 + cvta.local.u64 %SP
6. 字节处理: ld.global.u8 读 input[i], XOR ((i*73 + key) & 0xFF), 4-bit swap (AND 0xF0, SHL 4, SHR 4, OR)
7. 5 段循环每段 10485760 轮查 T-table, 每轮 XOR 轮计数器
8. 最后 st.global.u8 写回, vprintf("gift%d", byte)
9. vprintf 调用 mov.u64 %rd42, $str; cvta.global.u64; call.uni vprintf
10. GPU 加速爆破 5 段独立循环, 倒数逆向

## 关键 payload

```
cuobjdump -ptx / sm_52 / encrypt_kernel / 5x10485760 轮 / T-table 查表 / 4-bit swap / XOR (i*73+key) / vprintf gift
```

## 经验教训

CUDA reverse 用 cuobjdump -ptx 提汇编;__local_depot0 是 per-thread local memory;vprintf 调 call.uni 输出来看 gift1/gift2/gift3/gift4/gift5 分段结果。

## 标签

CUDA、PTX、sm_52、cuobjdump、AES T-table、ROT循环、mov.u64 %SPL __local_depot0、vprintf、encrypt_kernel、GPU加速、10M轮异或

## 参考来源

- https://www.ctfiot.com/232133.html
- 原文件：Aliyun2025_题解：easy-cuda-rev_PTX汇编+cuda加速.full.md

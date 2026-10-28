---
title: "TetCTF 2024 Writeup"
category: reverse
tags: ["TetCTF", "reverse", "webassembly", "z3-solver", "wasm-decompile", "wasm-check"]
signals: ["TetCTF 2024", "webassembly", "z3-solver", "wasm-decompile", "wasm-check", "fnv1a-hash", "xorshift128", "linalg-solve", "reverse", "TetCTF", "WebAssembly", "check_key", "WASM", "FNV1a"]
difficulty: hard
source: "https://www.ctfiot.com/160243.html"
tools: ["Python", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TetCTF 2024 Writeup

> 赛事：TetCTF 2024 | 方向：reverse | 难度：hard | 工具：Python、Z3

## 一句话总结

TetCTF 2024 WebAssembly + check_key：WASM 字节码 Z3 求解 + FNV1a + xorshift128 矩阵求逆。

## 攻击链

1. baby-asm: WASM 二进制 + WebAssembly.Module 加载
2. processInput 检查 text.length === 27 + 起始 TetCTF{ + 结束 }
3. wasm.init(20) 创 20 元素数组
4. wasm.array_fill(arr, i, text.charCodeAt(i+7)) 写入 c+83
5. wasm.check() 验证 20 个约束
6. 每 4 个一组 (add/sub/mul/xor) + 4 个 global 常量
7. globals = [115,82,52,149,136,67,76,97,71,90,71,74,124,104,84,67,114,127,52,31]
8. next = [1,2,3,0,5,6,7,4,9,10,11,8,...] 交叉排列
9. z3 BitVec 求解 20 个 flag[i+7]
10. check_key: 0x54 长度字符串 + 白名单 21 字符 !_acdefghilmnoprstuwy
11. 每 4 字符一组 (l << 2) hash_64_fnv1a
12. xorshift128 (x=0x75bcd15, y=0x159a55e5, z=0x1f123bb5, w=0xdeadbeef)
13. mem2[a] += mem1[b] * (xorshift128() % 0x400)
14. unk[0..21] 21 个目标值
15. Python: 枚举 21^4 哈希表 + xorshift128 矩阵 + np.linalg.solve 解 21 元一次方程
16. 还原 mem1 字典

## 关键 payload

```
np.linalg.solve(X, B)
```

## 经验教训

WASM 反编译为 WAT 后用 z3 BitVec 求解简单运算链；含 xorshift128 的 21 元一次方程可用 numpy.linalg.solve。

## 标签

webassembly、z3-solver、wasm-decompile、wasm-check、fnv1a-hash、xorshift128、linalg-solve

## 参考来源

- https://www.ctfiot.com/160243.html
- 原文件：TetCTF_2024_Writeup.full.md

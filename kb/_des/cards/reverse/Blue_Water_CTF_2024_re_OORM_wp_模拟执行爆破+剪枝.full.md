---
title: "Blue Water CTF 2024 re OORM wp 模拟执行爆破+剪枝"
category: reverse
tags: ["Blue Water CTF", "reverse", "800 funcs", "keyAs keyBs", "400 funcs_A + 400 funcs_B", "模拟执行 Unicorn"]
signals: ["Blue Water CTF 2024", "800 funcs", "keyAs keyBs", "400 funcs_A + 400 funcs_B", "模拟执行 Unicorn", "20-bit 输入爆破", "剪枝", "dfsA(20", "key)", "reverse", "Blue", "Water", "CTF", "OORM"]
difficulty: hard
source: "https://www.ctfiot.com/213273.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Blue Water CTF 2024 re OORM wp 模拟执行爆破+剪枝

> 赛事：Blue Water CTF 2024 | 方向：reverse | 难度：hard

## 一句话总结

Blue Water CTF 2024 re OORM — 800 个 funcs 链 20-bit 输入 + 模拟执行 Unicorn + DFS 剪枝爆破 (32766 阈值) + 末位 funcs_A_399 校验 (21961/27098)。

## 攻击链

1. main: 800 funcs (400 funcs_A + 400 funcs_B), do while times <= 799
2. funcs_A_i: x = input_bit | (key << 1), y = hashA(x), keyAs[20] = y
3. keyAs[0] 已知, keyBs[0] 已知
4. funcs_A_399: y == 21961 || y == 27098 → ++dwCheck
5. 模拟执行: Unicorn Uc(UC_ARCH_X86, UC_MODE_64)
6. 段映射: 0x6000 段 mem_map + mem_write
7. rva_to_offset 解析 ELF 段
8. dfsA(i, j, key) DFS 20-bit, j=19 末位剪枝
9. 剪枝: sim2(uc, i, j, key, 0/1) 结果 == 32766 接受
10. 关键: uc bug → j==3 重新创建 Uc
11. 输出: 20-bit 路径 + final key

## 关键 payload

```
800 funcs 链 / x = input_bit | (key<<1) / 模拟执行 Unicorn / dfsA(20, j) 剪枝 / uc bug j==3 重建 / final key 校验
```

## 经验教训

模拟执行 + 剪枝是 OORM (Obscure Obfuscated Reversing Machine) 标准解法;Unicorn 跨函数模拟需重建 Uc 实例;rva_to_offset + 段映射是 ELF 操作基础。

## 标签

800 funcs、keyAs keyBs、400 funcs_A + 400 funcs_B、模拟执行 Unicorn、20-bit 输入爆破、剪枝、dfsA(20、key)、x = input_bit | (key<<1)、y = hashA(x)、keyAs[20] = y、看雪 wx_御史神风

## 参考来源

- https://www.ctfiot.com/213273.html
- 原文件：Blue_Water_CTF_2024_re_OORM_wp_模拟执行爆破+剪枝.full.md

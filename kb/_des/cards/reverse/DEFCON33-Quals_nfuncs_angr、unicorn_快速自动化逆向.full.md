---
title: "DEFCON33-Quals nfuncs angr、unicorn 快速自动化逆向"
category: reverse
tags: ["DEFCON", "reverse", "angr-symbolic", "unicorn-emulation", "smc", "virtualprotect"]
signals: ["DEFCON 2025", "angr-symbolic", "unicorn-emulation", "smc", "virtualprotect", "capstone", "pefile", "hook-loop", "lut", "reverse", "DEFCON", "Quals", "nfuncs", "angr"]
difficulty: hard
source: "https://www.ctfiot.com/253727.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DEFCON33-Quals nfuncs angr、unicorn 快速自动化逆向

> 赛事：DEFCON 2025 | 方向：reverse | 难度：hard

## 一句话总结

DEFCON 33 Quals nfuncs 逆向题，angr + unicorn 联合自动化求解 8 字节表查找链。

## 攻击链

1. angr 项目用 read hook 收集 symbolic byte
2. capstone 提取 8 个 cmp/test 值
3. 约束求解 (input[i] == target - 13)
4. unicorn 模拟执行获取 VirtualProtect smc 内容
5. 把 smc 写回 PE 文件
6. checkpoint 记录下次 FUN_VA
7. 反复 hook 循环直到 memcmp 命中
8. 提取最终 ans

## 关键 payload

```
angr + unicorn 混合符号执行 + SMC 自修改
```

## 经验教训

现代 DEFCON 逆向题常用 SMC 自修改代码 + 多层函数调用，需要 angr 符号执行 + unicorn 模拟混合。

## 标签

angr-symbolic、unicorn-emulation、smc、virtualprotect、capstone、pefile、hook-loop、lut、memcmp

## 参考来源

- https://www.ctfiot.com/253727.html
- 原文件：DEFCON33-Quals_nfuncs_angr、unicorn_快速自动化逆向.full.md

---
title: "从ANGR-CTF项目入手ANGR和符号执行技术"
category: misc
tags: ["jakespringer/angr_ctf 训练营", "misc", "angr", "符号执行", "SimProcedure", "hook"]
signals: ["jakespringer/angr_ctf 训练营 2022", "angr", "符号执行", "SimProcedure", "hook", "veritesting", "reverse", "misc_unknown", "angr-CTF", "find", "avoid", "Project", "base_addr", "auto_load_libs"]
difficulty: medium
source: "https://www.ctfiot.com/285534.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从ANGR-CTF项目入手ANGR和符号执行技术

> 赛事：jakespringer/angr_ctf 训练营 2022 | 方向：misc | 难度：medium

## 一句话总结

angr-CTF 15 关系统训练，从 find/avoid 路径搜索到 SimProcedure 替换库函数避爆。

## 攻击链

1. 加载 angr Project 设定 base_addr 与 auto_load_libs=False
2. factory.entry_state 创建符号化初始状态
3. claripy.BVS 创建符号向量绑定寄存器/内存
4. simgr.explore(find=目标, avoid=陷阱) 反向求解
5. @project.hook 替换目标函数直接返回 eax
6. SimProcedure 类替换库函数（check_equals/scanf）避开路径爆炸
7. project.hook_symbol 按函数名挂 SimProcedure
8. 启用 veritesting=True 自动合并路径
9. 处理静态编译 strlen/共享库 validate 入口函数
10. 任意读通过 %7$s 格式化字符串符号化

## 关键 payload

```
simgr.explore(find=target, avoid=un_target) + BVS(password, 8*16) + solver.eval()
```

## 经验教训

SimProcedure 替代 check_equals + veritesting 是处理 2^16 路径爆炸的标准姿势；hook_symbol 比 hook(addr) 健壮，符号化 stdin 写入 SimFile 即可虚拟文件读取。

## 标签

angr、符号执行、SimProcedure、hook、veritesting、reverse

## 参考来源

- https://www.ctfiot.com/285534.html
- 原文件：从ANGR-CTF项目入手ANGR和符号执行技术.full.md

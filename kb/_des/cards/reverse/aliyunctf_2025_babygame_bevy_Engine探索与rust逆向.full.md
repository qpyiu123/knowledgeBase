---
title: "aliyunctf 2025 babygame bevy Engine 探索与 rust 逆向"
category: reverse
tags: ["aliyunctf", "reverse", "rust", "bevy", "ecs", "unity-like"]
signals: ["aliyunctf 2025", "rust", "bevy", "ecs", "unity-like", "scene", "query", "transform", "reverse", "CTF", "Rust", "scn", "ECS", "bevy_packed"]
difficulty: medium
source: "https://www.ctfiot.com/236198.html"
tools: ["Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# aliyunctf 2025 babygame bevy Engine 探索与 rust 逆向

> 赛事：aliyunctf 2025 | 方向：reverse | 难度：medium | 工具：Rust

## 一句话总结

阿里云 CTF 2025 Rust bevy 引擎逆向题，从 .scn 场景文件还原 ECS 实体组件系统状态机。

## 攻击链

1. 解压 bevy_packed 资源
2. 加载 .scn 场景文件
3. 解析世界/资源/实体表
4. 重放 ECS System
5. 还原 state machine
6. 拼装 transform

## 关键 payload

```
flag 通过 ECS Query<&mut Transform> 状态推进触发
```

## 经验教训

现代 Rust 游戏引擎(bevy)逆向关键是理解 ECS 模型 + App schedule + 系统依赖图，不必纠结 Rust 闭包语法。

## 标签

rust、bevy、ecs、unity-like、scene、query、transform

## 参考来源

- https://www.ctfiot.com/236198.html
- 原文件：aliyunctf_2025_babygame_bevy_Engine探索与rust逆向.full.md

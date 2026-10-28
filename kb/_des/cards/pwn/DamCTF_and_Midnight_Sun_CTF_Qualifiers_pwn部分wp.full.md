---
title: "DamCTF and Midnight Sun CTF Qualifiers pwn部分wp"
category: pwn
tags: ["DamCTF 2023 / Midnight Sun CTF 2023", "pwn", "pwn", "golden-banana", "text-adventure", "gets"]
signals: ["DamCTF 2023 / Midnight Sun CTF 2023 2023", "pwn", "golden-banana", "text-adventure", "gets", "fmt-string", "bing-ai", "房间指针劫持", "fmt_string", "DamCTF", "Golden", "Banana", "Bing", "main"]
difficulty: medium
source: "https://www.ctfiot.com/112814.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DamCTF and Midnight Sun CTF Qualifiers pwn部分wp

> 赛事：DamCTF 2023 / Midnight Sun CTF 2023 2023 | 方向：pwn | 难度：medium

## 一句话总结

DamCTF 2023 Golden Banana：gets栈溢出+fmt-string劫持房间指针

## 攻击链

1. Golden Banana: 文字冒险游戏+Bing AI生成的剧情
2. main中game结构体存房间信息
3. 输入选项处gets栈溢出
4. printf(l->description) 格式化字符串泄露栈地址
5. 第二次gets溢出覆盖选项结构体跳到SECRET ROOM
6. SECRET ROOM直接输出flag

## 关键 payload

```
gets(g.input_buf); printf(l->description)  # fmt-string leak
```

## 经验教训

gets+printf描述信息可fmt-string泄露地址

## 标签

pwn、golden-banana、text-adventure、gets、fmt-string、bing-ai、房间指针劫持

## 参考来源

- https://www.ctfiot.com/112814.html
- 原文件：DamCTF_and_Midnight_Sun_CTF_Qualifiers_pwn部分wp.full.md

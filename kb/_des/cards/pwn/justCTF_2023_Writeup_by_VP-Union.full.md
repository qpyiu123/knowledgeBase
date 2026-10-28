---
title: "justCTF 2023 Writeup by VP-Union"
category: pwn
tags: ["justCTF", "pwn", "house-pwn", "nucleus-pwn", "integer-overflow", "tcache-perthread"]
signals: ["justCTF 2023", "house-pwn", "nucleus-pwn", "integer-overflow", "tcache-perthread", "glibc-2.35", "exp-craft", "pwn_unknown", "justCTF", "VP-Union", "PWN", "house", "nucleus", "login"]
difficulty: hard
source: "https://www.ctfiot.com/119315.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# justCTF 2023 Writeup by VP-Union

> 赛事：justCTF 2023 | 方向：pwn | 难度：hard

## 一句话总结

justCTF 2023 VP-Union 战队 PWN 复盘，house + nucleus 两题。

## 攻击链

1. house: login admin + 0xff 覆盖 + -152 整数下溢
2. 栈溢出 + ret2libc
3. nucleus: tcache poisoning + libc 2.35
4. ab'*0x1f0 填充
5. delete 触发 0x1024 tcache
6. 泄 libc + 改 free_hook
7. ret2system

## 关键 payload

```
house 整数下溢 + nucleus 2.35 tcache attack
```

## 经验教训

justCTF 难度比国内比赛高一档，house/nucleus 都是中高难度题。

## 标签

house-pwn、nucleus-pwn、integer-overflow、tcache-perthread、glibc-2.35、exp-craft

## 参考来源

- https://www.ctfiot.com/119315.html
- 原文件：justCTF_2023_Writeup_by_VP-Union.full.md

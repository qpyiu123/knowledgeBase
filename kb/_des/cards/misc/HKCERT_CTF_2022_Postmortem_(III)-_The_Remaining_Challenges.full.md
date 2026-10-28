---
title: "HKCERT CTF 2022 Postmortem (III): The Remaining Challenges"
category: misc
tags: ["HKCERT CTF 2022", "misc", "misc", "z3-solver", "mycraft", "java"]
signals: ["HKCERT CTF 2022 2022", "misc", "z3-solver", "mycraft", "java", "weighted-baked-model", "getRotation", "random-seed", "misc_unknown", "HKCERT", "Misc", "Minecraft", "m-1"]
difficulty: hard
source: "https://www.ctfiot.com/87574.html"
tools: ["Java", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HKCERT CTF 2022 Postmortem (III): The Remaining Challenges

> 赛事：HKCERT CTF 2022 2022 | 方向：misc | 难度：hard | 工具：Java、Z3

## 一句话总结

HKCERT 2022 Misc：z3求解Minecraft mycraft+getRotation种子

## 攻击链

1. 序列: ? 1 37 37 97 / ? 33
2. 序列: ? 1 85 85 97 / ? 85 / ? 2 2 26 97 / ? 24
3. z3求解: xs[0..m-1]整数数组
4. 约束: 严格递增+不重复+<q
5. sum[0]=xs[0], sum[i+1]=sum[i]+(i+2)*xs[i+1]
6. product[0]=xs[0], product[i+1]=product[i]*(i+2)*xs[i+1]
7. sum[m-1] % q == s, product[m-1] % q == p
8. Java getRotation: x*3129871 ^ z*116129781 ^ y
9. seed = (l*l*42317861 + l*11) >> 16
10. Random.nextLong() % 4

## 关键 payload

```
z3.Solver + xorshift seed + weighted-baked-model
```

## 经验教训

Java Random种子可由x,y,z坐标异或重建

## 标签

misc、z3-solver、mycraft、java、weighted-baked-model、getRotation、random-seed

## 参考来源

- https://www.ctfiot.com/87574.html
- 原文件：HKCERT_CTF_2022_Postmortem_(III)-_The_Remaining_Challenges.full.md

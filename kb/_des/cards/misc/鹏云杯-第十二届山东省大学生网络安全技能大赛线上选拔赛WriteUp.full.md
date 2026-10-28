---
title: "鹏云杯 第十二届山东省大学生网络安全技能大赛 WriteUp"
category: misc
tags: ["鹏云杯", "misc", "maze-game", "boss-affect", "byte-XOR", "ror-rotation"]
signals: ["鹏云杯 2025", "maze-game", "boss-affect", "byte-XOR", "ror-rotation", "swap-reverse", "RSA-power-4", "continued-fraction", "lattice-attack", "misc_unknown", "game", "XOR", "ror", "swap"]
difficulty: medium
source: "https://www.ctfiot.com/271997.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 鹏云杯 第十二届山东省大学生网络安全技能大赛 WriteUp

> 赛事：鹏云杯 2025 | 方向：misc | 难度：medium

## 一句话总结

鹏云杯 4 题：迷宫 game 字节 XOR + 3 轮 ror+swap 加密 + 4 阶 RSA 连分数攻击。

## 攻击链

1. Reverse game 迷宫: wasd 控制 + 4 个 boss 影响 enc + 固定 key
2. byte_4020[i] += 4 + byte_4060[i] ^ byte_4020[i] = flag{Th1s_1s_My_S1mpl3_Fl4g_f0r_CTF}
3. Reverse error: 3 轮加密 + 逻辑左移 round+1 位 + 奇数反转偶数相邻交换
4. key = [0x1a,0x2b,0x3c,0x4d,0x5e,0x6f,0x70,0x81,0x92,0xa3,0xb4,0xc5,0xd6,0xe7,0xf8,0x09]
5. enc[i] = ror(enc[i], round+1) ^ key[i % 16]
6. Crypto 4 阶 RSA: n = p^4 * q^4 (p, q 256-bit), phi = (p^4-1)(q^4-1)
7. d 是 230-bit 素数, e = inverse(d, phi)
8. 用连分数 (continued fraction) 攻击恢复 p, q
9. 4 阶 RSA 不像标准 RSA, phi 多项式展开要小心

## 关键 payload

```
byte_4020[i] += 4 + XOR + ror(enc[i], round+1) ^ key + 连分数 4 阶 RSA
```

## 经验教训

迷宫 + boss 影响 enc 是 CTF 出题常用套路；4 阶 RSA 分解需要连分数 + phi 多项式。

## 标签

maze-game、boss-affect、byte-XOR、ror-rotation、swap-reverse、RSA-power-4、continued-fraction、lattice-attack、Shandong-CTF

## 参考来源

- https://www.ctfiot.com/271997.html
- 原文件：鹏云杯-第十二届山东省大学生网络安全技能大赛线上选拔赛WriteUp.full.md

---
title: "【WP】2022年春秋杯春季赛 Reverse、Pwn 类题目解析"
category: reverse
tags: ["春秋杯", "reverse", "QMK-firmware", "keyboard-combo", "process_combo_event", "keymaps"]
signals: ["春秋杯 2022", "QMK-firmware", "keyboard-combo", "process_combo_event", "keymaps", "layer-keycode", "KC_TRANSPARENT-inherit", "rand-LCG", "enc-1CTED8IL", "reverse", "Reverse", "Pwn", "QMK", "Layer"]
difficulty: medium
source: "https://www.ctfiot.com/52005.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2022年春秋杯春季赛 Reverse、Pwn 类题目解析

> 赛事：春秋杯 2022 | 方向：reverse | 难度：medium

## 一句话总结

2022 春秋杯春季赛 Reverse/Pwn 2 题 WP，QMK 键盘固件逆向 + Layer keycode 继承 + LCG 还原。

## 攻击链

1. babyqmk 搜字符串找 qmk_firmware + 找 process_combo_event + 提取 key_combos/CHUNQIU 激活 Combo_1/GAME 激活 Combo_2 切 Layer/提取 keymaps 3 个 Layer 0-9A-Z 不同/formatLayer + buildLayerMap 处理 KC_TRANSPARENT 继承上层/SEED=0 LC(214013, +2531011) rand 生成表/keycodeToKey 映射查表还原 enc="1CTED8IL-BIMM-SMFP-HOKP-HOIDRZL4W6KR

## 关键 payload

```
加密 enc="1CTED8IL-BIMM-SMFP-HOKP-HOIDRZL4W6KR"  SEED=0  rand 公式 214013*x + 2531011
```

## 经验教训

QMK 是开源键盘固件，组合键 (Combo) 触发 process_combo_event；KC_TRANSPARENT (1) 继承上一层 keycode 是 QMK 关键特性；LCG SEED=0 起始 + 0x7fff 掩码是经典伪随机。

## 标签

QMK-firmware、keyboard-combo、process_combo_event、keymaps、layer-keycode、KC_TRANSPARENT-inherit、rand-LCG、enc-1CTED8IL

## 参考来源

- https://www.ctfiot.com/52005.html
- 原文件：【WP】2022年春秋杯春季赛Reverse、Pwn类题目解析.full.md

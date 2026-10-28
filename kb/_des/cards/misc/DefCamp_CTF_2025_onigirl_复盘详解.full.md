---
title: "DefCamp CTF 2025 onigirl 复盘详解"
category: misc
tags: ["DefCamp CTF 2025", "misc", "pwn", "rev", "stb_image", "pic-format"]
signals: ["DefCamp CTF 2025 2025", "pwn", "rev", "stb_image", "pic-format", "png", "distance-factor", "xor", "privilege", "stego_image", "DefCamp", "onigirl", "PIC", "PIE"]
difficulty: hard
source: "https://www.ctfiot.com/273679.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DefCamp CTF 2025 onigirl 复盘详解

> 赛事：DefCamp CTF 2025 2025 | 方向：misc | 难度：hard

## 一句话总结

DefCamp 2025 onigirl：stb_image魔改+PIC格式+像素距离变换

## 攻击链

1. PIE+Full RELRO+Canary+NX
2. 读取图片stbi_load_from_memory
3. 计算像素到中心距离
4. 距离因子distance_factor=1.8*(1.0-d/max_distance)
5. modification_parameters_1[10]应用矩阵非线性变换
6. XOR/NOT像素引入噪声
7. privilege_value*=(R&G)&B&0xF
8. 目标privilege==4919
9. stbi__pic_test Core: 头校验 53 80 f6 34
10. stbi__pic_is4(p_n4096, "PICT") 验证

## 关键 payload

```
*(double*)&modification_parameters[3*random_index] = rand()/2147483647.0*0.25+0.15
```

## 经验教训

stb_image读取+随机扰动+像素距离因子是复杂图像题常见模式

## 标签

pwn、rev、stb_image、pic-format、png、distance-factor、xor、privilege、modification-parameters

## 参考来源

- https://www.ctfiot.com/273679.html
- 原文件：DefCamp_CTF_2025_onigirl_复盘详解.full.md

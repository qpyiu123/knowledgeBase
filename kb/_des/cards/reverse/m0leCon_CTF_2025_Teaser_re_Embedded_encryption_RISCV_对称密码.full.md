---
title: "m0leCon CTF 2025 Teaser re Embedded encryption RISCV 对称密码"
category: reverse
tags: ["m0leCon", "reverse", "risc-v", "mcu", "metal-gpio", "ip-permutation"]
signals: ["m0leCon 2025", "risc-v", "mcu", "metal-gpio", "ip-permutation", "p-box", "row-column-sum", "gpio-input-pin", "custom-block-cipher", "reverse", "m0leCon", "Teaser", "RISC-V", "output"]
difficulty: hard
source: "https://www.ctfiot.com/206641.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# m0leCon CTF 2025 Teaser re Embedded encryption RISCV 对称密码

> 赛事：m0leCon 2025 | 方向：reverse | 难度：hard

## 一句话总结

m0leCon 2025 Teaser 嵌入式逆向，RISC-V 自定义分组密码 + 行列和反推 output。

## 攻击链

1. 识别 RISC-V 32 位固件
2. metal_gpio_get_input_pin 读 1 位随机种子
3. srand+rand 用内置库
4. var644[1604] 分四区: m32[32]/input[33]/m256[256]/output[256*4]
5. IP 置换表 (32 字节)
6. P 盒映射 (256 字节)
7. 重复 1337 轮
8. output[input[j]] = 1 << (31-j)
9. 行列和反推 input
10. 解密

## 关键 payload

```
1 位种子 + IP/P 盒 + 行列和反推
```

## 经验教训

当 output 矩阵每行/列只有 1 位为 1 时，行列和反推是经典线性代数问题。

## 标签

risc-v、mcu、metal-gpio、ip-permutation、p-box、row-column-sum、gpio-input-pin、custom-block-cipher

## 参考来源

- https://www.ctfiot.com/206641.html
- 原文件：m0leCon_CTF_2025_Teaser_re_Embedded_encryption_RISCV_对称密码.full.md

---
title: "天山固网 2025 网络安全技能竞赛 - 5题WP(MISC+CRYPTO+REVERSE)"
category: misc
tags: ["天山固网-2025网络安全技能竞赛", "misc", "Dvorak键盘", "二维码还原", "AES-ECB", "Pollard_p-1"]
signals: ["天山固网-2025网络安全技能竞赛 2025", "Dvorak键盘", "二维码还原", "AES-ECB", "Pollard_p-1", "p^q高/低位异或", "sage_small_roots", "IDApython", "50字符flag", "reverse", "Dvorak", "random", "RSA", "pollard"]
difficulty: medium
source: "https://www.ctfiot.com/267054.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 天山固网 2025 网络安全技能竞赛 - 5题WP(MISC+CRYPTO+REVERSE)

> 赛事：天山固网-2025网络安全技能竞赛 2025 | 方向：misc | 难度：medium

## 一句话总结

天山固网2025赛涵盖Dvorak脑洞/random种子RSA/pollard分解/p^q异或剪枝/AndroidDemo AES-ECB/50字符IDA反推5题。

## 攻击链

1. MISC:流量提取大小写→0/1→42×42二维码→Dvorak键盘解码rar密码 → CRYPTO:random.seed(0)固定shuffle+myPrime爆破→Pollard p-1分解n→RSA解密 → CRYPTO Xor_Mast3r:pq_high_xor剪枝+sage小根求低位 → REVERSE AndroidDemo:check函数AES-ECB → REVERSE You_say_i_do:输入50字符+cmp从25位开始+IDApython遍历30E0C3模式反推flag前段

## 关键 payload

```
Dvorak键盘 + random.seed(0) + Pollard_p-1 + 30E0C3字节模式 + 0x5F下划线分隔
```

## 经验教训

Dvorak键盘脑洞题需要图片描述提示;random.seed(0)固定+myPrime伪随机可预测2000个64-bit素因子;Pollard p-1分解光滑p-1的RSA;p^q高位异或泄露时用剪枝+Coppersmith small_roots求低位;Android JNI check函数常为AES-ECB;50字符flag分两段校验用IDApython反推retf前段。

## 标签

Dvorak键盘、二维码还原、AES-ECB、Pollard_p-1、p^q高/低位异或、sage_small_roots、IDApython、50字符flag、AndroidDemo、JNI、retf切换

## 参考来源

- https://www.ctfiot.com/267054.html
- 原文件：天山固网-2025网络安全技能竞赛-WriteUp.full.md

---
title: "【BuildCTF】Misc 方向 AK 全解 WP"
category: misc
tags: ["BuildCTF", "misc", "morse-code", "LSB-stego", "base64", "yangguaiqi"]
signals: ["BuildCTF 2024", "morse-code", "LSB-stego", "base64", "yangguaiqi", "fojue", "tianji", "base58", "zero-width-stego", "stego", "BuildCTF", "Misc", "OSINT", "what"]
difficulty: easy
source: "https://www.ctfiot.com/212905.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【BuildCTF】Misc 方向 AK 全解 WP

> 赛事：BuildCTF 2024 | 方向：misc | 难度：easy

## 一句话总结

BuildCTF 2024 Misc 方向 AK 全解 WP，10 道题横跨编码/隐写/图像/条形码/铁路 OSINT/二维码。

## 攻击链

1. what is this 二进制转字符串 + 摩斯密码 / 老色批 LSB 信息 base64 解 / 一念 阴阳怪气 + 佛曰 + 天书 + Base58 / 如果再来一次 图片两字节反转 + 8!67adz6 压缩包密码 + 条形码识别 / 别真给我开盒了 铁路线路 s3901 查霸州西/南站 / 四妹 图片高度调整获后半截密文 / 白白的真好看 零宽字符隐写 + Word 调色得 Flag1 + 汉信码识别 + snow 解密 Flag3 / EZ_ZIP 图片末尾压缩包 + 修改压缩大小 + 加密标志 00 / Guesscoin 全猜 0 爆破 / Black&White 黑白色块拼二维码 + Base45

## 关键 payload

```
三段拼接 BuildCTF{Th3_wh1t3_y0u_s33_1s_n0t_wh1t3}  铁路 flag: BuildCTF{津保铁路}
```

## 经验教训

LSB 隐写 + 零宽字符 + Snow 隐写 + 佛曰/天书/阴阳怪气是国内 Misc 隐写库三件套；图片两字节反转是常见处理；铁路 OSINT 看线路编号；汉信码是中国自主二维码标准；Base45 是欧洲常用编码。

## 标签

morse-code、LSB-stego、base64、yangguaiqi、fojue、tianji、base58、zero-width-stego、hanxin-code、snow-stego、ez-zip、qrcode、base45

## 参考来源

- https://www.ctfiot.com/212905.html
- 原文件：【BuildCTF】Misc方向AK全解WP.full.md

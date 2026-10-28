---
title: "2024 首届\"山石·蒙山杯\"网络安全大赛 WriteUp（凯撒+USB+CRC32 爆破）"
category: misc
tags: ["2024 首届\"山石·蒙山杯\"网络安全大赛", "misc", "蒙山杯 Misc 签到 m13c", "凯撒 shift=4 eccgxj{Nywx_e_W1qtpi_Q13g} → ayyctf{Jut_a_S1mple_M13c}", "shark USB 键盘流量 04-a 1c-y 06-c 17-t", "USB HID scan code map"]
signals: ["2024 首届\"山石·蒙山杯\"网络安全大赛 2024", "蒙山杯 Misc 签到 m13c", "凯撒 shift=4 eccgxj{Nywx_e_W1qtpi_Q13g} → ayyctf{Jut_a_S1mple_M13c}", "shark USB 键盘流量 04-a 1c-y 06-c 17-t", "USB HID scan code map", "easymisc zip 密码 4 字节可见 ASCII CRC32 爆破", "PIL Image.split() RGB LSB 隐写", "misc_unknown", "stego_image", "crypto_unknown", "Misc", "shift", "USB", "scan"]
difficulty: easy
source: "https://www.ctfiot.com/190955.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 首届"山石·蒙山杯"网络安全大赛 WriteUp（凯撒+USB+CRC32 爆破）

> 赛事：2024 首届"山石·蒙山杯"网络安全大赛 2024 | 方向：misc | 难度：easy | 工具：Python

## 一句话总结

蒙山杯 Misc 三题：凯撒 shift=4 + USB 键盘流量 scan code map + zip 4 字节密码 CRC32 爆破 + LSB 隐写。

## 攻击链

1. 签到 m13c: caesar_decrypt(eccgxj{Nywx_e_W1qtpi_Q13g}, shift=4) → ayyctf{Jut_a_S1mple_M13c}
2. shark: USB 键盘流量按键顺序 04-1c-06-17-09-2f-0b-20-0f-0f-27-2d-0e-08-1c-2d-05-27-21-15-07-30 → ayyctf{h3ll0_key_b04rd}
3. easymisc: zip 4 字节密码 CRC32 爆破 zlib.crc32 + itertools.product
4. 解压后 PIL Image.split() RGB LSB 隐写

## 关键 payload

```
caesar_decrypt(ciphertext, shift=4) → ayyctf{Jut_a_S1mple_M13c}
```

## 经验教训

USB 键盘流量 scan code → ASCII 映射：04=a, 1c=y, 06=c, 17=t, 09=f, 2f={, 0b=h, 20=3, 0f=l, 27=0, 2d=-, 0e=k, 08=e, 21=4, 15=r, 07=d, 30=}；CRC32 爆破 4 字节可见 ASCII 100^4 = 1 亿，Python 跑 30 秒。

## 标签

蒙山杯 Misc 签到 m13c、凯撒 shift=4 eccgxj{Nywx_e_W1qtpi_Q13g} → ayyctf{Jut_a_S1mple_M13c}、shark USB 键盘流量 04-a 1c-y 06-c 17-t、USB HID scan code map、easymisc zip 密码 4 字节可见 ASCII CRC32 爆破、PIL Image.split() RGB LSB 隐写

## 参考来源

- https://www.ctfiot.com/190955.html
- 原文件：2024首届“山石·蒙山杯”网络安全大赛WriteUp.full.md

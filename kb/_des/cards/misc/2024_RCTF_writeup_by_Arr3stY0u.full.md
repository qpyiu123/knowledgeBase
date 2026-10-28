---
title: "2024 RCTF writeup by Arr3stY0u"
category: misc
tags: ["RCTF", "misc", "PNG列抽样拼接", "USB键盘流量", "pwncli 2048改分", "House of Apple 2"]
signals: ["RCTF 2024", "PNG列抽样拼接", "USB键盘流量", "pwncli 2048改分", "House of Apple 2", "AES-CBC", "file_get_contents phar", "Boneh-Durfee", "XTEA delta=0x12345678", "stego_image", "pwn_unknown", "web_unknown", "crypto_rsa", "UUID"]
difficulty: hard
source: "https://www.ctfiot.com/184051.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 RCTF writeup by Arr3stY0u

> 赛事：RCTF 2024 | 方向：misc | 难度：hard

## 一句话总结

UUID列抽样+键盘流量+pwn 2048+House of Apple 2+Boneh-Durfee+32位VM hook。

## 攻击链

1. 1. flag0-9.png 每张抽 1/2 列拼成 UUID / 2. 键盘流量 USB 还原命令 / 3. pwn 2048 模拟 BFS+1024 满行合并 / 4. pwn webp House of Apple 2 stderr _wide_data 劫持 system / 5. web 注入 '||love_key regexp binary 'x' / 6. crypto XTEA delta=0x12345678 + sbox 置换 / 7. 32 位 VM add/sub/xor hook 还原 / 8. Boneh-Durfee 大 e RSA / 9. 整数解 8 字节 claripy BVS 求多组方程 / 10. AES-128-CBC + str_rot13 + sbox

## 关键 payload

```
RCTF{c4baf0eb-e5ca-543a-06d0-39d72325a0} ; niao ybufmefhui kjqillxdjwmi uizebuui ... ; _IO_wfile_jumps vtable + libc.system + chain ; Boneh-Durfee kd continued_fraction 还原 d ; XTEA delta=0x12345678
```

## 经验教训

RCTF 风格综合：pwn 改分 + webp IO_FILE + crypto XTEA 变种 delta 全方位。

## 标签

PNG列抽样拼接、USB键盘流量、pwncli 2048改分、House of Apple 2、AES-CBC、file_get_contents phar、Boneh-Durfee、XTEA delta=0x12345678、32位虚拟机、整数解 claripy、sbox置换

## 参考来源

- https://www.ctfiot.com/184051.html
- 原文件：2024_RCTF_writeup_by_Arr3stY0u.full.md

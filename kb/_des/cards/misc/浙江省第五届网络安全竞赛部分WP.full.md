---
title: "浙江省第五届网络安全竞赛部分 WP by 7coin"
category: misc
tags: ["浙江省信安赛", "misc", "mt_srand", "time-seed", "shuffle", "USB-HID"]
signals: ["浙江省信安赛 2022", "mt_srand", "time-seed", "shuffle", "USB-HID", "base64-base32", "affine-cipher", "RSA-Coppersmith", "small_roots", "rce", "USB", "HID", "Coppersmith", "ORW"]
difficulty: medium
source: "https://www.ctfiot.com/58989.html"
tools: ["PHP", "ROP", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 浙江省第五届网络安全竞赛部分 WP by 7coin

> 赛事：浙江省信安赛 2022 | 方向：misc | 难度：medium | 工具：PHP、ROP、tshark

## 一句话总结

浙江省信安赛 6 题综合：mt_srand 时间种子预测 + USB HID 字典 + 仿射密码 + Coppersmith small_roots + ORW ROP。

## 攻击链

1. Web ezphp: mt_srand(time) 预测 shuffle 后 system/ls 在数组中的下标 → 调用 system("cat /flag")
2. Misc base64-base32: 双层编码，先 base64 再 base32
3. Misc USB HID: tshark usb.capdata 提取 → normalKeys/shiftKeys 字典映射 → "mik<DEL>mae..." 输出
4. Misc m4a reversed zip: 字节反序恢复 zip 文件
5. Crypto 仿射: c = (a*x + 7) mod 37, a = n-1, ans = (num - 7) * inverse(key, 37) mod 37
6. Crypto RSA: 已知 p 高 560 bit + Coppersmith small_roots(X=2^(1024-560-i.nbits()), beta=0.4) + 2^15 迭代
7. Pwn: pop_rax=0x400a4f + syscall=0x4025ab + ROP + open(0xaf2faf="/flag") + read/write ORW
8. payload: p64(0) + pop_rax(2) + pop_rdi(0xaf2faf) + pop_rsi(0) + syscall + pop_rax(0) + read(3, buf) + pop_rax(1) + write(1, buf)

## 关键 payload

```
mt_srand(time)+shuffle 下标 + USB HID normalKeys + 仿射 inverse(key, 37) + Coppersmith small_roots + ORW ROP
```

## 经验教训

mt_srand(time) 是 PHP shuffle 预测经典套路；Coppersmith small_roots 是已知 p 部分位的 RSA 攻击方法。

## 标签

mt_srand、time-seed、shuffle、USB-HID、base64-base32、affine-cipher、RSA-Coppersmith、small_roots、ROP-ORW、7coin

## 参考来源

- https://www.ctfiot.com/58989.html
- 原文件：浙江省第五届网络安全竞赛部分WP.full.md

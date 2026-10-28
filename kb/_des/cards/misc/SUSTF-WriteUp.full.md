---
title: "SUSTF WriteUp - ChaMd5 Venom"
category: misc
tags: ["SUSTF", "misc", "lfsr-recover", "gaussian-elimination", "browser-pwn", "js-prototype-pollution"]
signals: ["SUSTF 2022", "lfsr-recover", "gaussian-elimination", "browser-pwn", "js-prototype-pollution", "uaf", "misc_unknown", "SUSCTF", "ChaMd5", "Venom", "IOT", "LFSR", "Browser", "Web"]
difficulty: medium
source: "https://www.ctfiot.com/28093.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SUSTF WriteUp - ChaMd5 Venom

> 赛事：SUSTF 2022 | 方向：misc | 难度：medium

## 一句话总结

SUSCTF 招新题库，ChaMd5 Venom IOT/工控组，涵盖 LFSR/Browser/Web 三类。

## 攻击链

1. lfsr(seed2, mask2, n2) 枚举 (2^12, 2^12) 找与 plain "Date" XOR 匹配
2. 已知 plain 头 16 字节构造方程组
3. gauss 消元解 mask1
4. browser 0day: DataView.setUint32/getUint32 注入 ArrayBuffer 调
5. leak libc1/libc2 = dataView.gu32(8/12)
6. 改 a4.setUint32(0x98, libc1+0x2f28) 触发任意读
7. 改 a5.setUint32(0, libc1-0x1967f0+0x91871) 触发任意写
8. suid find /tmp → /bin/umount 替换反弹 shell
9. web fxxkcors: report 页面 admin 访问提交 URL
10. changeapi.php 提权改用户 → admin 改自己
11. LFSR magic_box 解 2 个文件
12. TEA 解密 standard 加密字符串
13. 数据流追踪分析代码

## 关键 payload

```
lfsr(seed2, mask2, n2) gauss mask1
```

## 经验教训

LFSR 已知明文 + 短长度即可用高斯消元解掩码；浏览器 OOB 读写比传统 UAF 更具威力。

## 标签

lfsr-recover、gaussian-elimination、browser-pwn、js-prototype-pollution、uaf

## 参考来源

- https://www.ctfiot.com/28093.html
- 原文件：SUSTF-WriteUp.full.md

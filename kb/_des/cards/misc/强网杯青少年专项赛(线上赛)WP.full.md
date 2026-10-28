---
title: "强网杯青少年专项赛 线上赛 WP"
category: misc
tags: ["强网杯青少年", "misc", "QR-code-combine", "backdoor-user-kill", "GIF-multi-frame", "multi-encode"]
signals: ["强网杯青少年 2024", "QR-code-combine", "backdoor-user-kill", "GIF-multi-frame", "multi-encode", "AES-CBC", "DP-state-count", "ret2libc", "fgets-overflow", "misc_unknown", "GIF", "MISC", "flag", "youthful_and_upward"]
difficulty: medium
source: "https://www.ctfiot.com/217894.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯青少年专项赛 线上赛 WP

> 赛事：强网杯青少年 2024 | 方向：misc | 难度：medium

## 一句话总结

强网青少年 6+ 题：QR 拼图 + 后门用户删除 + GIF + 5 重编码 + AES-CBC + DP 计数 + ret2libc。

## 攻击链

1. MISC 签到漫画: 多页漫画末有二维码拼图 → 桌面 qq 钉 → 解析 → flag{youthful_and_upward}
2. MISC 删除后门用户: backdoor 用户 5 秒复活, kill 父进程 Pid22 → userdel -f backdoor → flag{943f9194-97a1-497f-80ef-0fbe530acfa9}
3. MISC white: GIF 多帧 → flag{passion_is_the_greatest_teacher}
4. Crypto Classics: base32+base64+rot13(回转 23 位)+Atbash+Vigenère(key=GAMELAB) → flag{2834d185-a1da-4fb1-8bac-59076eb6a634}
5. Crypto AliceAES: AES-CBC + 8995bee3173bb5ede17be5cfc58d762c → flag{6e80563b-21b2-4a70-a809-ec0893c18ccb}
6. Crypto easymath: DP 状态计数 + next_prime
7. PWN clock_in: fgets 缓冲区溢出 + ret2libc + puts@plt 泄 libc + system("/bin/sh")

## 关键 payload

```
QR 拼图 + kill 父进程 + GIF 多帧 + base32/64/rot13/Atbash/Vigenère + AES-CBC + DP 计数 + ret2libc
```

## 经验教训

强网青少年题覆盖 Misc 多技能 + Crypto 多重编码 + PWN 基础栈溢出；适合青少年入门。

## 标签

QR-code-combine、backdoor-user-kill、GIF-multi-frame、multi-encode、AES-CBC、DP-state-count、ret2libc、fgets-overflow、隼目安全

## 参考来源

- https://www.ctfiot.com/217894.html
- 原文件：强网杯青少年专项赛(线上赛)WP.full.md

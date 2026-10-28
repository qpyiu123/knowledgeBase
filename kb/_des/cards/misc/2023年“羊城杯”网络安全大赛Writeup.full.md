---
title: "2023 年\"羊城杯\"网络安全大赛 Writeup"
category: misc
tags: ["羊城杯 2023", "misc", "PHP反序列化", "preg_replace过滤", "字符串重组绕黑名单", "Flask_session伪造"]
signals: ["羊城杯 2023 2023", "PHP反序列化", "preg_replace过滤", "字符串重组绕黑名单", "Flask_session伪造", "pickle反序列化", "musl_libc", "ORW", "CVE-2023-28303", "deserialize", "PHP", "Flask", "session", "musl"]
difficulty: hard
source: "https://www.ctfiot.com/133282.html"
tools: ["Flask", "PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年"羊城杯"网络安全大赛 Writeup

> 赛事：羊城杯 2023 2023 | 方向：misc | 难度：hard | 工具：Flask、PHP、Python

## 一句话总结

羊城杯综合：PHP 反序列化字符串重组 + Flask session 伪造 + musl libc UAF + 零宽/LSB 隐写。

## 攻击链

1. D0n''t pl4y g4m3: php 反序列化，prohib 过滤 system/exec/passthru 等
2. syssystemtem 字符串重组绕过 preg_replace
3. Bei__destruct → Yang__call → call_user_func 链
4. Serpent: Flask session 伪造 secret_key=GWHT1GGAvNAKvF
5. pickle.loads(base64) 反序列化 + cos system bash -i 反弹 shell
6. 提权用 python3.8 SUID 读 /flag
7. ArkNights: /proc/1/environ 非预期读 secret_key
8. shellcode: 自写 ORW 汇编
9. cookieBox: musl libc UAF + FSOP + __stdin_FILE 劫持栈
10. easy_vm: 任意地址写 + exit_hook + one_gadget + 爆破 ld
11. ai 和 nia: flag2.zip 零宽隐写 + flag1.png LSB 隐写 + B 站视频定位
12. EZ_misc: Gronsfeld 密码 + CVE-2023-28303 截图恢复
13. Matryoshka: blind_watermark 解出 Watermark_is_fun + VeraCrypt 挂载

## 关键 payload

```
syssystemtem → system, secret_key=GWHT1GGAvNAKvF, /proc/1/environ
```

## 经验教训

preg_replace 可用 syssystemtem 重组绕；Flask session secret_key 可从 /proc/1/environ 拿；musl libc UAF 用 FSOP 劫持 __stdin_FILE。

## 标签

PHP反序列化、preg_replace过滤、字符串重组绕黑名单、Flask_session伪造、pickle反序列化、musl_libc、ORW、CVE-2023-28303、零宽隐写、VeraCrypt、blind_watermark

## 参考来源

- https://www.ctfiot.com/133282.html
- 原文件：2023年“羊城杯”网络安全大赛Writeup.full.md

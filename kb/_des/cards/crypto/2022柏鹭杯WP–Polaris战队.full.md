---
title: "2022 柏鹭杯 WP – Polaris 战队"
category: crypto
tags: ["2022 柏鹭杯 (Polaris)", "crypto", "柏鹭杯", "e=3-RSA", "立方根爆破", "XXE"]
signals: ["2022 柏鹭杯 (Polaris) 2022", "柏鹭杯", "e=3-RSA", "立方根爆破", "XXE", "OOB", "pwntools-shell-class", "libc-2.31", "libc-2.35", "crypto_rsa", "xxe", "pwn_unknown", "lfi", "RSA"]
difficulty: hard
source: "https://www.ctfiot.com/57173.html"
tools: ["gmpy2", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 柏鹭杯 WP – Polaris 战队

> 赛事：2022 柏鹭杯 (Polaris) 2022 | 方向：crypto | 难度：hard | 工具：gmpy2、pwntools

## 一句话总结

2022 柏鹭杯：e=3 RSA 立方根爆破 + XXE + pwn function pointer 覆盖

## 攻击链

1. Q1 e=3 RSA: c + n*k 的立方根爆破, iroot(c+n*k, 3) 还原明文
2. Q2 XXE: <!DOCTYPE test [<!ENTITY % file SYSTEM ''php://filter/read=convert.base64-encode/resource=/flag''>]> + OOB
3. Q3 PWN note1: edit_buf + edit_func + func, function pointer 覆盖, system(''/bin/sh'')
4. Q4 PWN note2: libc-2.31 → libc-2.35 PROTECT_PTR bypass, tcache poisoning, fclose hook

## 关键 payload

```
for k in range(200000000): if gmpy2.iroot(c+n*k, 3)[1] == 1: print(long_to_bytes(iroot(c+n*k, 3)[0]))
```

## 经验教训

e=3 RSA + m^3 < n 直接开根；XXE OOB 是经典；function pointer 覆盖是 pwn 入门

## 标签

柏鹭杯、e=3-RSA、立方根爆破、XXE、OOB、pwntools-shell-class、libc-2.31、libc-2.35、function-pointer-overwrite、edit_buf+func、PROTECT_PTR、edit_func

## 参考来源

- https://www.ctfiot.com/57173.html
- 原文件：2022柏鹭杯WP–Polaris战队.full.md

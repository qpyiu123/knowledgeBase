---
title: "2024 强网拟态 CFB_chall"
category: crypto
tags: ["强网拟态", "crypto", "AES-CFB 8-bit", "篡改 token", "单字节爆破", "error 区分爆破"]
signals: ["强网拟态 2024", "AES-CFB 8-bit", "篡改 token", "单字节爆破", "error 区分爆破", "block_cipher", "web_unknown", "crypto_unknown", "AES-CFB", "bit", "reset", "key", "admim", "token"]
difficulty: medium
source: "https://www.ctfiot.com/211724.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 强网拟态 CFB_chall

> 赛事：强网拟态 2024 | 方向：crypto | 难度：medium

## 一句话总结

AES-CFB 8-bit 单字节爆破 + reset 重置 iv/key 凑运气。

## 攻击链

1. 注册用户 admim 密码 a*15+11123456 → token 16 字节密文 → AES-CFB 8-bit 模式篡改第 5 字节 m→n 让 n 后面解密出 \x00 → 第 6 字节爆破 256 次让后面 admin 隔离 → 第 7 字节爆破 256 次让第 23 字节变成 \x00 拆出 123456 → reset 重置 iv/key 继续尝试（总尝试 1/512 概率）→ 登录 admin/123456 拿 flag

## 关键 payload

```
token = encrypt(f"{username}\x00{password}\x01\x02\x03", key) ; split('\x00') 切出多段时多余段归 _ ; AES CFB 8-bit 改 1 字节影响后续 16 字节
```

## 经验教训

AES CFB 8-bit 模式每个密文字节是独立流密码块，改 1 字节只影响后续；revenge 用不同 error 文案做 oracle 攻击。

## 标签

AES-CFB 8-bit、篡改 token、单字节爆破、error 区分爆破

## 参考来源

- https://www.ctfiot.com/211724.html
- 原文件：2024_强网拟态_CFB_chall.full.md

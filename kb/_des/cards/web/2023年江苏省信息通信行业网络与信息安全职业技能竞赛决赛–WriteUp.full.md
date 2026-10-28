---
title: "2023 年江苏省信息通信行业网络与信息安全职业技能竞赛决赛 – WriteUp"
category: web
tags: ["江苏信息通信行业网安竞赛 2023", "web", "php_trick_md5_substr", "control%0a绕preg_match", "str_replace_data://绕", "USB键盘流量"]
signals: ["江苏信息通信行业网安竞赛 2023 2023", "php_trick_md5_substr", "control%0a绕preg_match", "str_replace_data://绕", "USB键盘流量", "SlientEye隐写", "AES秘钥爆破", "LCG+费马小定理RSA", "花指令RE", "crypto_hash", "php_trick", "USB", "SlientEye", "AES"]
difficulty: medium
source: "https://www.ctfiot.com/147695.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年江苏省信息通信行业网络与信息安全职业技能竞赛决赛 – WriteUp

> 赛事：江苏信息通信行业网安竞赛 2023 2023 | 方向：web | 难度：medium

## 一句话总结

江苏信息通信综合 7 题：php_trick 多重绕+USB 流量+SlientEye+AES 爆破+LCG+RSA+花指令。

## 攻击链

1. Web php_trick: substr(path, 32) === md5(path) + path[] 数组绕过
2. con=control%0a 绕 /^control$/ 正则但 !==
3. flag=dadata://ta://text/plain 绕 str_replace + base64 Y3RmZXI=
4. USB 键盘流量解析 vim flag.txt + 9f0adccb...ff0c2f091e49a5dd96
5. SlientEye 隐写：flag{8a497aff3184d4b33000c44150760559}
6. AES 秘钥爆破：key 前 15 位 1016Aes128L12l2 + 末位爆破
7. LCG 6 组输出还原 a,b,m + 费马小定理分解 N
8. RE 花指令 605：patch jmp + 密文两位对调后 -32

## 关键 payload

```
flag=dadata://ta://text/plain;base64,Y3RmZXI=
```

## 经验教训

substr 数组绕过 + con %0a 绕正则 + dadata 协议绕 str_replace；LCG 6 组输出即可还原 a,b,m。

## 标签

php_trick_md5_substr、control%0a绕preg_match、str_replace_data://绕、USB键盘流量、SlientEye隐写、AES秘钥爆破、LCG+费马小定理RSA、花指令RE

## 参考来源

- https://www.ctfiot.com/147695.html
- 原文件：2023年江苏省信息通信行业网络与信息安全职业技能竞赛决赛–WriteUp.full.md

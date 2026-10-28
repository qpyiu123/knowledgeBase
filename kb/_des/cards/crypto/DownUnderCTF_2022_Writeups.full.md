---
title: "DownUnderCTF 2022 Writeups"
category: crypto
tags: ["DownUnderCTF 2022", "crypto", "crypto", "aes-ofb", "rsa-interval-oracle", "mongodb-nosqli"]
signals: ["DownUnderCTF 2022 2022", "crypto", "aes-ofb", "rsa-interval-oracle", "mongodb-nosqli", "symlink", "sqli-quine", "ast-parse", "compilerbot", "crypto_rsa", "DownUnderCTF", "writeup", "OFB", "RSA"]
difficulty: hard
source: "https://www.ctfiot.com/59624.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DownUnderCTF 2022 Writeups

> 赛事：DownUnderCTF 2022 2022 | 方向：crypto | 难度：hard | 工具：Python

## 一句话总结

DownUnderCTF 2022 14题writeup：OFB+RSA+NoSQL+Symlink+SQLi+Python

## 攻击链

1. ofb 加密：已知前缀+两次加密还原明文
2. rsa-interval-oracle-i: 区间预言机二分爆破
3. rsa-interval-oracle-ii: Manger 攻击
4. pay-to-win: 椭圆曲线阶利用multiplicative_order
5. mongo: NoSQL注入 n0sql1_is_th3_new_5qli
6. symlink web: 软链接读取/flag
7. sqli-quine: 自包含SQL注入
8. last-digit: CVE-2020-10735 hash长度截断
9. ast-parse: 编译错误信息泄露源码
10. compilerbot: 二分查找flag字符

## 关键 payload

```
ofb ct2[i] XOR ct1[i+1] = pt2[i]  # 已知前缀还原
```

## 经验教训

OFB可利用前缀+两次IV构造完整明文；RSA区间预言机二分

## 标签

crypto、aes-ofb、rsa-interval-oracle、mongodb-nosqli、symlink、sqli-quine、ast-parse、compilerbot、python、php

## 参考来源

- https://www.ctfiot.com/59624.html
- 原文件：DownUnderCTF_2022_Writeups.full.md

---
title: "FireFox Forensics：两份文件怎样配对"
category: "forensics"
kind: "writeup"
tags: ["Firefox", "NSS", "浏览器登录记录"]
signals: ["key4.db", "logins.json", "password-check"]
source: "https://ctf2.dasctf.com/dashboard/practice/b9bbb32f-f186-458f-b90b-12440c0f6aea?tab=challenges&challenge=3ba70c01-db39-4043-b9ff-91fc7c6407a6"
origin_id: "r66-firefox-forensics"
relates_to: ["forensics/browser-artifacts.md"]
verification: "DASCTF 判题通过"
also_category: ["misc"]
---

# FireFox Forensics：两份文件怎样配对

GKCTF 2021 · 杂项取证 · 2026-11-06 在 [DASCTF 练习页](https://ctf2.dasctf.com/dashboard/practice/b9bbb32f-f186-458f-b90b-12440c0f6aea?tab=challenges&challenge=3ba70c01-db39-4043-b9ff-91fc7c6407a6) 提交，站点显示回答正确。

## 先看这一步

同时找到 key4.db 和 logins.json 时，先验证主密码，再按密钥编号配对。数据库和登录字段使用的算法不同。

**适用时**：两份文件来自同一配置，且主密码校验通过。 **留意**：不同样本可能声明不同算法，不能沿用 Chromium 文件格式。

题目压缩包里的 `logins.json` 保存加密后的登录字段，`key4.db` 保存解开它们需要的密钥。只在单独目录读这两份赛题文件。

## 先核对主密码，再解登录记录

1. 打开 SQLite 数据库，读取 `metaData` 中 `id='password'` 的 `item1` 和 `item2`。前者是全局盐值，后者是加密的校验文字。盐值是参与密钥推导的一段数据。
2. 先用空主密码试校验。本题这一步解出了固定文字 `password-check`，因此可以继续。不成功时，先核对算法编号和主密码，别把错误的密钥送去解登录记录。
3. 把 `encryptedPassword` 做 Base64 解码，再按 ASN.1（用来描述二进制字段的格式）读取密钥编号、算法、初始向量和密文。用编号匹配 `nssPrivate.a102`，取同一行的 `a11`，解出 24 字节密钥。
4. 本题登录字段使用三重 DES 的 CBC 模式。用第 3 步的密钥解密并去掉填充。提交时保留解出的原始赛事前缀，不再套一层花括号。

## 本题实际用到了哪些算法

数据库中的校验字段和密钥字段都是 PBES2，也就是用主密码派生密钥后再解密。读取里面声明的盐、迭代次数和算法，按样本使用 PBKDF2-HMAC-SHA256（按次数重复派生密钥）和 AES-256-CBC。登录字段本身是另一套算法，不能拿派生出的 AES 密钥直接解。

想快速复做，可以把赛题两份文件放在同一目录，使用 [firepwd 项目的说明](https://github.com/lclevy/firepwd)指定该目录。本文用本地代码独立核对了空主密码、密钥编号和登录字段的解密。

参考：[GKCTF × DASCTF 赛事题解](https://cloud.tencent.com/developer/article/1844889)。

## 配套代码

`kb/_code/r66/firefox_sample.py`。从代码所在目录运行 `python firefox_sample.py 原附件`。依赖见脚本开头；运行后会显示核对结果。

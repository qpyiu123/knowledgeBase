---
title: "美团CTF-WriteUp"
category: pwn
tags: ["美团CTF", "pwn", "ChaMd5-Venom", "PHP-OOP", "call_user_func", "phar-deserialize"]
signals: ["美团CTF 2021", "ChaMd5-Venom", "PHP-OOP", "call_user_func", "phar-deserialize", "file_put_contents", "time-blind-sqli", "RSA-low-bits", "babyrop-pwn", "deserialize", "CTF", "WriteUp", "ChaMd5", "Venom"]
difficulty: hard
source: "https://www.ctfiot.com/16962.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 美团CTF-WriteUp

> 赛事：美团CTF 2021 | 方向：pwn | 难度：hard | 工具：PHP

## 一句话总结

美团CTF WriteUp,涵盖ChaMd5 Venom招新文+PHP OOP反序列化(Users/User/Welcome/File/Logs+call_user_func+phar触发)+时间盲注+RSA低位爆破+ret2libc babyrop。

## 攻击链

1. Web PHP反序列化:abstract Users {db, verify_user, check_user_exist, add_user, eval} + User {func, param, eval: (func)(param)}
2. phar.phar元数据反序列化触发eval
3. payload:new User("call_user_func", array("Logs","log"))触发file_put_contents
4. 用php://filter或base64前缀绕'<?php exit();'退出
5. 时间盲注:b"#G.5~1s" + i + "aa",time.time()测时间15-12s=正确
6. RSA低位爆破:n末18位+前18位+3位str(i,j,k)+factordb
7. P=p拼接p+q,PP=P+Q,QQ=Q+P,n=PP*QQ
8. babyrop ret2libc one_gadget
9. AES-CBC解密

## 关键 payload

```
PHP反序列化 + 时间盲注 + RSA低位爆破
```

## 经验教训

PHP OOP反序列化是Web经典题型,phar元数据是稳定反序列化触发点;时间盲注+1字节差是密码攻击实用技术;RSA拼接+低位爆破是新型RSA攻击面。

## 标签

ChaMd5-Venom、PHP-OOP、call_user_func、phar-deserialize、file_put_contents、time-blind-sqli、RSA-low-bits、babyrop-pwn、brute-md5、AES-CBC

## 参考来源

- https://www.ctfiot.com/16962.html
- 原文件：美团CTF-WriteUp.full.md

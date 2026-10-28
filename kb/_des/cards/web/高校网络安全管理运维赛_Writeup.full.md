---
title: "高校网络安全管理运维赛 Writeup"
category: web
tags: ["高校网络安全管理运维赛", "web", "buffer-overflow", "ret2win", "upx-unpack", "bitwise-solve"]
signals: ["高校网络安全管理运维赛 2024", "buffer-overflow", "ret2win", "upx-unpack", "bitwise-solve", "jwt-bypass", "mongodb-nosql", "python-CRLF", "redis-CRLF", "web_unknown", "PWN", "bitwise", "WEB", "JWT"]
difficulty: medium
source: "https://www.ctfiot.com/180828.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 高校网络安全管理运维赛 Writeup

> 赛事：高校网络安全管理运维赛 2024 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

高校网络安全管理运维赛WP集合,涵盖PWN栈溢出+RE bitwise爆破+WEB JWT/MongoDB/Pickle/SSRF/XXE+MISC ZIP钓鱼邮件DKIM综合,运维安全方向。

## 攻击链

1. babypwn: token+username+password 0x38字节溢出+p64(0x40117A) ret2win
2. Login: token+admin/1q2w3e4r后Core dumped回显写入ELF,第二次token+admin+\x00*0x98+p64(0x40127E)改ret
3. babyre: upx -d脱壳,4部分bitwise表达式爆破(a1+...==target)得4个数字
4. pyssrf: Python 3.7 urllib CVE-2019-9740/CVE-2019-9947 CRLF注入+redis SSRF写pickle exec
5. fileit: XXE无回显+VPS+xxe.php/xxe.xml外带
6. phpsql: admin''||1万能密码SQL注入
7. Messy Mongo: jwt登录ctfer+MongoDB updateOne $set+assert.notEqual(''admin'')+$toLower绕过
8. zip: 5字符开头flag{+token+0x7f\x7f\x7f\x7f\x7f删除前缀构payload
9. 钓鱼邮件: DKIM TXT记录查询+SPF/DMARC拼接+base64+ROT13综合
10. easyshell: bkcrack已知明文攻击+修改压缩包密码

## 关键 payload

```
admin'||1 + CVE-2019-9740 CRLF redis SET pickle exec
```

## 经验教训

高校运维赛常见考点组合:Python 3.7+urllib CRLF CVE是稳定SSRF向量,MongoDB updateOne+$toLower能绕过assert.notEqual,DKIM/DMARC/SPF DNS记录枚举是钓鱼邮件分析标配。

## 标签

buffer-overflow、ret2win、upx-unpack、bitwise-solve、jwt-bypass、mongodb-nosql、python-CRLF、redis-CRLF、pickle-exec、XXE-OOB、DKIM-verify、DNS-TXT

## 参考来源

- https://www.ctfiot.com/180828.html
- 原文件：高校网络安全管理运维赛_Writeup.full.md

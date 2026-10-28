---
title: "DataCon2020优秀解题思路分享：僵尸网络方向第一题（阿里云安全）"
category: misc
tags: ["DataCon 2020", "misc", "botnet", "honeypot", "http-log", "sql"]
signals: ["DataCon 2020 2020", "botnet", "honeypot", "http-log", "sql", "ld_preload", "xgoahead", "cgi", "malware", "misc_unknown", "DataCon2020", "HTTP", "LD_PRELOAD", "ELF"]
difficulty: medium
source: "https://www.ctfiot.com/74662.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2020优秀解题思路分享：僵尸网络方向第一题（阿里云安全）

> 赛事：DataCon 2020 2020 | 方向：misc | 难度：medium

## 一句话总结

DataCon2020僵尸网络分析：蜜罐HTTP日志+LD_PRELOAD ELF+xgoahead

## 攻击链

1. 黑名单正则过滤honeypot_http_log
2. 长度>=32的URL
3. 发现LD_PRELOAD=/proc/self/fd/0 + ELF头post data
4. xgoahead web服务器+admin/login.cgi
5. filename=2.elf+Content-Disposition
6. sub_5C4解密: chr(ord(c)-98)
7. MD5 4个ELF文件
8. passive_dns查exec.kfckiller.cc等C2域名

## 关键 payload

```
sub_5C4(c) = chr(ord(c) - 98)  # 字符减98
```

## 经验教训

蜜罐日志过滤用长URL+LD_PRELOAD+ELF头识别攻击payload

## 标签

botnet、honeypot、http-log、sql、ld_preload、xgoahead、cgi、malware

## 参考来源

- https://www.ctfiot.com/74662.html
- 原文件：DataCon2020优秀解题思路分享：僵尸网络方向第一题（阿里云安全）.full.md

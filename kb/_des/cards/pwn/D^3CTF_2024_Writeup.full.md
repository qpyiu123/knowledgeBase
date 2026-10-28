---
title: "D^3CTF 2024 Writeup"
category: pwn
tags: ["D3CTF", "pwn", "php-zend-allocator", "pwn-shell", "off-by-one", "tcache-double-free"]
signals: ["D3CTF 2024", "php-zend-allocator", "pwn-shell", "off-by-one", "tcache-double-free", "kernelland", "protosand", "pwn_unknown", "CTF", "PwnShell", "PHP", "Kernel", "Sandbox", "Pwn"]
difficulty: hard
source: "https://www.ctfiot.com/177055.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# D^3CTF 2024 Writeup

> 赛事：D3CTF 2024 | 方向：pwn | 难度：hard | 工具：PHP

## 一句话总结

D^3CTF 2024 PwnShell PHP 扩展 + Kernel Sandbox 两道 Pwn。

## 攻击链

1. /proc/self/maps 泄 libc base
2. PHP Zend off-by-one 改 node->buf
3. 任意地址读写劫持 _emalloc GOT
4. 改 system
5. bash -c reverse shell
6. 写 bash shell 写 mount 提权

## 关键 payload

```
/proc/self/maps + PHP Zend 堆 off-by-one
```

## 经验教训

PHP 扩展 off-by-one + Zend 分配器 + tcache double-free 经典利用。

## 标签

php-zend-allocator、pwn-shell、off-by-one、tcache-double-free、kernelland、protosand

## 参考来源

- https://www.ctfiot.com/177055.html
- 原文件：D^3CTF_2024_Writeup.full.md

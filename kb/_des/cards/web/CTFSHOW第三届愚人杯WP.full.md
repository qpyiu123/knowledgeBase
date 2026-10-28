---
title: "CTFSHOW 第三届愚人杯 WP"
category: web
tags: ["CTFShow", "web", "PNG CRC32反推宽高", "Ook语言", "PHP base64任意文件读", "反序列化链 w_wuw_w+gBoBg"]
signals: ["CTFShow 2023", "PNG CRC32反推宽高", "Ook语言", "PHP base64任意文件读", "反序列化链 w_wuw_w+gBoBg", "Caesar字符移位", "Flask SSTI cycler", "RSA链式加密+IP尾", "s_box+encrypt1+encrypt2", "web_unknown", "CTFSHOW", "PNG", "CRC32", "Ook"]
difficulty: medium
source: "https://www.ctfiot.com/121875.html"
tools: ["Flask", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTFSHOW 第三届愚人杯 WP

> 赛事：CTFShow 2023 | 方向：web | 难度：medium | 工具：Flask、PHP

## 一句话总结

CTFSHOW 第三届愚人杯 — 12+ 题合集: PNG CRC32 反推 + Ook 语言 + PHP base64 任意文件读 + 反序列化 4 步链 + Caesar + Flask SSTI + RSA 链式 + S_BOX 置换 + 矩阵异或。

## 攻击链

1. Misc: PNG CRC32 反推 width/height (for w/h in 4096)
2. Ook 语言: !替换！, .替换。, ?替换？
3. Web PHP: ?img=base64(file) 任意文件读
4. 反序列化: w_wuw_w __destruct → gBoBg __toString → w_wuw_w __invoke → EeE __clone → cycycycy.aaa
5. Caesar 字符移位 4 + qwertyuiopasdfghjklzxcvbnm123456789
6. Flask SSTI: g.pop.__globals__.__builtins__.__import__(''os'').popen(''ls'').read()
7. Crypto: RSA PKCS1_v1_5 链式加密 (密文1+IP2 → 密文2+IP3 → 明文+IP用户B)
8. encrypt1: 块内 16 字节 7 倍位置交换
9. encrypt2: S_BOX 置换 16 次
10. Reverse: 矩阵加密 (300*300 异或表) + 矩阵成图
11. flag 不在题面, 在加密矩阵本身

## 关键 payload

```
PNG CRC32 反推 / Ook 语言 / PHP base64 任意文件读 / 反序列化 4 步链 / Caesar 移位 4 / Flask SSTI / RSA PKCS1 链式加密 / S_BOX 置换 / 300x300 矩阵异或 / 矩阵成图
```

## 经验教训

愚人杯风格是 1 道题多种 trick 混合;PNG CRC32 反推宽高是经典;反序列化 4 步链 (destruct → toString → invoke → clone) 是 PHP 模板;S_BOX 置换 + 16 轮 encrypt1 块内交换是常见加密。

## 标签

PNG CRC32反推宽高、Ook语言、PHP base64任意文件读、反序列化链 w_wuw_w+gBoBg、Caesar字符移位、Flask SSTI cycler、RSA链式加密+IP尾、s_box+encrypt1+encrypt2、矩阵异或+线性代数、异或递推、PNG矩阵成图

## 参考来源

- https://www.ctfiot.com/121875.html
- 原文件：CTFSHOW第三届愚人杯WP.full.md

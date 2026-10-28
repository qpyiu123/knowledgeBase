---
title: "2023 NKCTF WriteUp By EDISEC"
category: web
tags: ["2023 NKCTF (南开 CTF)", "web", "NKCTF", "hard-php", "PHP-全角字符", "数学"]
signals: ["2023 NKCTF (南开 CTF) 2023", "NKCTF", "hard-php", "PHP-全角字符", "数学", "NAN-INF", "getallheaders", "phar", "unserial", "rce", "web_unknown", "jwt", "sqli", "PHP"]
difficulty: hard
source: "https://www.ctfiot.com/105824.html"
tools: ["Frida", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 NKCTF WriteUp By EDISEC

> 赛事：2023 NKCTF (南开 CTF) 2023 | 方向：web | 难度：hard | 工具：Frida、PHP

## 一句话总结

NKCTF 2023：PHP 全角字符 + PDF-RCE + ZenTao CVE + APK + BMP stego

## 攻击链

1. hard_php: PHP 全角字符算术 ０/０ = NAN, [''''==''$''] 取第一位, 增量运算还原字母, 拼函数调用
2. NKCTF=$$_[__]($$_[_]) → system(shell_exec) → echo `cat /flag`>3.txt
3. easy_php: GET/POST 传 NS[CTF.go] + cmd, PDF 内嵌 JPG SHA-1 触发
4. baby_php: 反序列化 Welcome → Happy → Hell0 → system($_POST[1])
5. Webpagetest: getallheaders() 注入 (XRay 漏洞)
6. easy_pms: 禅道 pms 已知 CVE (https://github.com/webraybtl/zentaopms_poc)
7. ez_baby_apk: jadx 找加壳, frida dump dex
8. easy_bmp: BMP 文件头修复, 像素 stego
9. blue: 蓝牙 pcap 流量分析
10. 三体: 数学建模 + 文字
11. first spam of rabbit year: 找春节相关字符串
12. easy_rgb: 像素 RGB 通道 stego

## 关键 payload

```
$_=(０/０)._;$_=$_[''=='$'];$_++;$__=$_++;$__=$_++.$__;$_++;$_++;$_='_'.$__.($_++).$_;$$_[__]($$_[_]);
```

## 经验教训

PHP 0/0=NAN + 全角字符是字符构造经典；PDF 内嵌 JPG 触发是 0day 利用；禅道 pms CVE 是国内常见

## 标签

NKCTF、hard-php、PHP-全角字符、数学、NAN-INF、getallheaders、phar、unserial、pdf-rce、baby_apk、easy_bmp、blue、三体、xiaopi、baby_music、easy_rgb

## 参考来源

- https://www.ctfiot.com/105824.html
- 原文件：2023NKCTF-WriteUp_By_EDISEC.full.md

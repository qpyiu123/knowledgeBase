---
title: "第十四届全国大学的信息安全竞赛-WriteUp"
category: web
tags: ["全国大学生信息安全竞赛", "web", "Web-SQL注入-XPath", "updatexml", "sqmap", "Web-PHP_SESSION_UPLOAD_PROGRESS"]
signals: ["全国大学生信息安全竞赛 2021", "Web-SQL注入-XPath", "updatexml", "sqmap", "Web-PHP_SESSION_UPLOAD_PROGRESS", "文件包含", "图片马", "Misc-bmp转换", "proto3-Protobuf", "sqli", "Web", "Misc", "Crypto", "Pwn"]
difficulty: medium
source: "https://www.ctfiot.com/1926.html"
tools: ["sqlmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第十四届全国大学的信息安全竞赛-WriteUp

> 赛事：全国大学生信息安全竞赛 2021 | 方向：web | 难度：medium | 工具：sqlmap

## 一句话总结

第十四届全国大学生信安赛Web/Misc/Crypto/Re/Pwn:Web updatexml盲注+SQLMAP+PHP_SESSION_UPLOAD_PROGRESS文件包含+图片马+ADFGX+proto3反序列化+proto2-RSA-共模+小指数+p高位+ECDSA-GF(p)+SMS4-AES-CBC(第8轮异或bytee)+Logistic混沌

## 攻击链

1. Web: admin'') and updatexml(0xconcat)+sqlmap|Web: PHP_SESSION_UPLOAD_PROGRESS+50KB文件POST+./var/lib/php/sessions/sess_sessid文件包含|Misc: 382张bmp RGB(233,233,233)→0|Misc: protobuf3反序列化|图片马加#define width 1 height 1|Crypto: ADFGX密文倒置密钥classic|RSA: 共模+小指数+Coppersmith/Sage求解 p高位泄露|house_of_orange+house_of_grey|SMS4-AES-CBC 第8轮异或 bytee+|ECDSA GF(p) y^2=x^3+x k,e 离散对数+Salt|混沌Logistic r=1.2 x0=0.840264 + key1,key2=169,78

## 关键 payload

```
admin') and updatexml(0,concat(0x7e,mid((select * from(select * from flag a join (select * from flag)b using(id,no))c),1,50)),0);#|PHP_SESSION_UPLOAD_PROGRESS=<?php var_dump(scandir("/etc"));?> 50KB大文件POST|RSA-共模 ext_euclid(e1,e2)→s,t组合; 小指数 iroot; Coppersmith p+GF(2^512)|M = matrix(ZZ,[[2**512,e],[0,-n]]).LLL()|xort A bytee S8|1.2, 0.840264, 169, 78|逆AES + 7轮recover + rrecover
```

## 经验教训

1) updatexml报错盲注+sqlmap dump; 2) PHP_SESSION_UPLOAD_PROGRESS条件竞争+50KB大文件+var/lib/php/sessions/sess_sessid LFI; 3) 图片马结尾加#define width 1 #define height 1绕图片处理; 4) ADFGX密文需倒置+关键词classic; 5) RSA-共模攻击ext_euclid;小指数iroot;p高位M.LLL(); 6) AES第8轮加bytee异或后,piece1=k[0,1,4,7,10,11,13,14] piece2=k[2,3,5,6,8,9,12,15]分别md5比对; 7) ECDSA GF(p) 求解y^2=x^3+x + k,e 离散对数; 8) Logistic r=1.2 x0=0.840264 + key1=169 key2=78 2bit编码(XOR/~XOR)

## 标签

Web-SQL注入-XPath、updatexml、sqmap、Web-PHP_SESSION_UPLOAD_PROGRESS、文件包含、图片马、Misc-bmp转换、proto3-Protobuf、Crypto-ADFGX、RSA共模+小指数+p高位泄露、SMS4-AES-CBC-piecesmd5、ECDSA-GF(p)、混沌Logistic、Pwn

## 参考来源

- https://www.ctfiot.com/1926.html
- 原文件：第十四届全国大学的信息安全竞赛-WriteUp.full.md

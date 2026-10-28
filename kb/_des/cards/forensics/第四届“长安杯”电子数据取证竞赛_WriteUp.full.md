---
title: "第四届\"长安杯\"电子数据取证竞赛 WriteUp"
category: forensics
tags: ["长安杯", "forensics", "取证", "Java后台", "nohup", "mysql"]
signals: ["长安杯 2022", "取证", "Java后台", "nohup", "mysql", "Frida-Hook", "Android脱壳", "Java扩展欧几里得逆向", "4字符爆破", "forensic_disk", "USTD", "Java", "Frida", "Hook"]
difficulty: medium
source: "https://www.ctfiot.com/76314.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第四届"长安杯"电子数据取证竞赛 WriteUp

> 赛事：长安杯 2022 | 方向：forensics | 难度：medium | 工具：Java

## 一句话总结

第四届长安杯电子数据取证(虚拟币交易诈骗+USTD币+HT币+勒索+Java 5服务后台+nohup日志+Frida Hook java.lang.String.equals+扩展欧几里得逆向+4字符4重爆破)

## 攻击链

1. 计算机取证: ens33网卡配置+5个java jar后台(admin-api/cloud/market/ucenter-api/exchange)+npm run dev|服务器取证: powershell历史+%USERPROFILE%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt+ wsl+service mysql start|SHOW VARIABLES LIKE ''gen%'' 显示生成列|Frida-Hook: Java.perform attach()改写java.lang.String.equals打印所有比较|手机取证: Android加固脱壳|Java逆向: OooO扩展欧几里得函数+4字符4重for爆破flag (iArr[6]={1197727043,1106668192,...}+objArr[6]={''x'',''1'','':'',''A'',''z'',''}''})

## 关键 payload

```
nohup java -jar admin-api.jar > admin-api.file 2>&1 &|SHOW VARIABLES LIKE ''gen%'';|Frida hook: HookClass = Java.classFactory.use(''java.lang.String''); HookClass.equals.implementation = function(obj){ console.log(this + '' equals '' + obj); return ret; }|private long[] OooO(long j, long j2): if j==0 return {0,1}; return {((j2/j)*OooO[0])+OooO[1], OooO[0]}; (扩展欧几里得)|int j = str.charAt(0) << 16; j = j | (str.charAt(1) << ''b''); j = j | (str.charAt(2) << 24); j = str.charAt(3) | j;|for ig1,ig2,ig3,ig4 in 33..127: 4字符爆破 OooO0O0(subStr, 5) → 验证iArr[num] - j == ((Integer)objArr[num]).intValue()
```

## 经验教训

1) Java后台取证:nohup java -jar xxx.jar启动5个微服务; 2) MySQL生成列:SHOW VARIABLES LIKE 'gen%'; 3) PSReadLine历史记录取证:ConsoleHost_history.txt路径固定; 4) Frida-Hook Java类:Java.classFactory.use+equals.implementation打印所有比较; 5) 扩展欧几里得Java逆向:OooO(j, j2)递归实现; 6) 4字符爆破:33-127 ASCII范围+扩展欧几里得比较验证

## 标签

取证、Java后台、nohup、mysql、Frida-Hook、Android脱壳、Java扩展欧几里得逆向、4字符爆破

## 参考来源

- https://www.ctfiot.com/76314.html
- 原文件：第四届“长安杯”电子数据取证竞赛_WriteUp.full.md

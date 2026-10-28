---
title: "第二届陇剑杯决赛Misc-Win"
category: forensics
tags: ["陇剑杯决赛", "forensics", "陇剑杯", "Vmware加密", "VMX加密", "rockyou爆破"]
signals: ["陇剑杯决赛 2023", "陇剑杯", "Vmware加密", "VMX加密", "rockyou爆破", "Xshell密码", "Reg注册表", "启动脚本", "forensic_disk", "win", "VMX", "pyvmx-cracker", "rockyou", "somewhere"]
difficulty: medium
source: "https://www.ctfiot.com/136503.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第二届陇剑杯决赛Misc-Win

> 赛事：陇剑杯决赛 2023 | 方向：forensics | 难度：medium | 工具：C、Python

## 一句话总结

陇剑杯决赛win场景4问:VMX加密pyvmx-cracker+rockyou爆破somewhere+Xshell 7 NetSarang Computer\7\Xshell\Sessions反序列化AES密码123456a+启动脚本注册表Environment+Startup目录+访问www.baidu.com 10次

## 攻击链

1. 1. VMX加密: 识别encryption.keySafe=vmware:key/list/(pair/...)→pyvmx-cracker.py+rockyou.txt爆破→密码somewhere|2. Xshell会话: NetSarang Computer\7\Xshell\Sessions找.xsh文件→XShellCryptoHelper.py -d -user testtt -sid SID→密码123456a|3. 启动脚本: 注册表HKEY_CURRENT_USER\Environment + Startup目录C:\Users\testtt\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup|4. 访问次数: 内存或日志检索www.baidu.com共10次

## 关键 payload

```
pyvmx-cracker.py -v VMX.vmx -d rockyou.txt|encryption.keySafe = vmware:key/list/(pair/(phrase/...))|XShellCryptoHelper.py -d -user testtt -sid S-1-5-21-1844938145-4200775270-4174914976-1000 p5orZNxx2PcH/dp8h0/0nr+yyIooYMX/TOPZSiHvt2VmrQ+Sya1X|somewhere|123456a|C:\Users\testtt\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup|10
```

## 经验教训

1) VMware加密VMX文件结构:encryption.keySafe=vmware:key/list/(pair/(phrase/PBKDF2-HMAC-SHA-1/AES-256/rounds=10000/salt=...)); 2) pyvmx-cracker.py是标准VMX密码爆破工具,搭配rockyou.txt字典; 3) Xshell 7会话存储路径C:\Users\<user>\Documents\NetSarang Computer\7\Xshell\Sessions\,XShellCryptoHelper.py解密SID+cipher; 4) 启动脚本两处:注册表HKCU\Environment(用户环境变量)和Startup目录(开始菜单启动项); 5) 日志/内存检索URL计数可用grep

## 标签

陇剑杯、Vmware加密、VMX加密、rockyou爆破、Xshell密码、Reg注册表、启动脚本

## 参考来源

- https://www.ctfiot.com/136503.html
- 原文件：第二届陇剑杯决赛Misc-Win.full.md

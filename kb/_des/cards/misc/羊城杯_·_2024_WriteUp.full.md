---
title: "羊城杯 2024 WriteUp"
category: misc
tags: ["羊城杯", "misc", "Python-pickle-WAF-bypass", "Tomcat-XML-deploy", "JSP-webshell", "0x10-stack-overflow"]
signals: ["羊城杯 2024", "Python-pickle-WAF-bypass", "Tomcat-XML-deploy", "JSP-webshell", "0x10-stack-overflow", "stack-migrate", "glibc-2.35", "largebin-attack", "_IO_list_all", "deserialize", "pickle", "WAF", "Tomcat", "XML"]
difficulty: medium
source: "https://www.ctfiot.com/201792.html"
tools: ["Python", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 羊城杯 2024 WriteUp

> 赛事：羊城杯 2024 | 方向：misc | 难度：medium | 工具：Python、ROP

## 一句话总结

羊城杯 2024 多方向：pickle 绕 WAF + Tomcat XML 部署 + 栈迁移 + largebin 劫持 stderr + Dijkstra ORW。

## 攻击链

1. WEB Lyrics For You: Python 3.10.7 目录穿越 + 读源码 + pickle (cos system S''cmd'' o.) + bypass WAF
2. WEB ntomtom2: XML 上传 + path 指定目录 + Tomcat 热部署覆盖 web.xml + JSP 解析执行
3. PWN pstack: 0x10 栈溢出 + 栈迁移到 bss 0x601a00 + ROP puts(read) + ret2libc
4. PWN TravelGraph: glibc 2.35 + 沙箱 ORW + largebin attack 写 _IO_list_all + 劫持 stderr
5. TravelGraph 需构造 Dijkstra 最短路径 > 2000 拿 edit 机会，edit 改 bk_nextsize 触发 largebin
6. show 泄 unsorted bin 残留 libc + heap 地址
7. 堆风水 mmap RWX + open/read/write shellcode
8. MISC hiden: rot13 + rot47 双重编码 + flag.txt wave 文件

## 关键 payload

```
pickle (cos\nsystem\nS\''cmd\''\no.) + Tomcat XML path + 栈迁移 bss + largebin attack stderr
```

## 经验教训

沙箱 ORW 必须先泄 libc + heap，再 largebin attack 写 _IO_list_all；Dijkstra 是出题人附加交互设计。

## 标签

Python-pickle-WAF-bypass、Tomcat-XML-deploy、JSP-webshell、0x10-stack-overflow、stack-migrate、glibc-2.35、largebin-attack、_IO_list_all、Dijkstra、modbus.func_code、rot13-rot47、wave-hiden

## 参考来源

- https://www.ctfiot.com/201792.html
- 原文件：羊城杯_·_2024_WriteUp.full.md

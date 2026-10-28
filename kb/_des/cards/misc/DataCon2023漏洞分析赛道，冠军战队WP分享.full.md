---
title: "DataCon2023漏洞分析赛道，冠军战队WP分享"
category: misc
tags: ["DataCon 2023", "misc", "vuln-audit", "codeql", "joern", "neo4j"]
signals: ["DataCon 2023 2023", "vuln-audit", "codeql", "joern", "neo4j", "cypher", "污点传播", "函数模式", "misc_unknown", "DataCon2023", "CodeQL", "Joern", "Cypher", "PCall"]
difficulty: hard
source: "https://www.ctfiot.com/151336.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2023漏洞分析赛道，冠军战队WP分享

> 赛事：DataCon 2023 2023 | 方向：misc | 难度：hard

## 一句话总结

DataCon2023漏洞分析：CodeQL/Joern+污点传播Cypher查询

## 攻击链

1. 题目1: 漏洞模式理解+审计（PCall memcpy/Base64Decode/snprintf/system/snprintf/Serialize.Deserialize）
2. 题目2: 二进制漏洞模式归纳+CodeQL/Joern查询
3. MATCH (n:identifier) WHERE n.callee="ustream_get_read_buf" AND n.index=-1
4. VQL.taintPropagation(sourceSet, sinkSet) YIELD taintPropagationPath
5. memmove dest+src 同一函数同line不在dfg
6. pcalloc+memcpy+strstr+/doc/xml+sub_F0CF0
7. sscanf+tar zxf命令注入+sprintf /dav/%s.tar.gz

## 关键 payload

```
MATCH (n:identifier) WHERE n.callee="ustream_get_read_buf" AND n.index=-1
```

## 经验教训

静态分析工具结合VQL污点传播可系统化漏洞挖掘

## 标签

vuln-audit、codeql、joern、neo4j、cypher、污点传播、函数模式

## 参考来源

- https://www.ctfiot.com/151336.html
- 原文件：DataCon2023漏洞分析赛道，冠军战队WP分享.full.md

---
title: "2023 安洵杯 WriteUp By Mini-Venom"
category: web
tags: ["安洵杯 2023", "web", "CommonsBeanutils", "PropertyUtilsBean反射", "BeanComparator", "TiedMapEntry"]
signals: ["安洵杯 2023 2023", "CommonsBeanutils", "PropertyUtilsBean反射", "BeanComparator", "TiedMapEntry", "BadAttributeValueExpException", "黑名单绕过", "Spring FreeMarker", "AES_padding_oracle", "deserialize", "Spring", "FreeMarker", "RSA", "AES"]
difficulty: medium
source: "https://www.ctfiot.com/153097.html"
tools: ["Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 安洵杯 WriteUp By Mini-Venom

> 赛事：安洵杯 2023 2023 | 方向：web | 难度：medium | 工具：Spring

## 一句话总结

6 道综合：CommonsBeanutils 反射 + Spring FreeMarker + RSA 位翻转 + AES padding oracle + CRT RSA。

## 攻击链

1. ezJava: 黑名单 (jndi/jackson/spring/JdbcRowSetImpl/SignedObject/TemplatesImpl/Runtime/ProcessBuilder/PriorityQueue) 全 ban
2. 走 PropertyUtilsBean 反射 + BeanComparator + TiedMapEntry
3. BadAttributeValueExpException.readObject → TiedMapEntry.toString → LazyMap.get → BeanComparator.compare → PropertyUtilsBean.getProperty → invoke Method → getConnection
4. PostgreSQL 攻击链
5. Spring FreeMarker: springMacroRequestContext.webApplicationContext → freeMarkerConfiguration → setNewBuiltinClassResolver
6. ${"freemarker.template.utility.Execute"?new()("id")} 模板执行
7. D0g3 RSA: 已知 p 二进制，p[i]=0 改 1 试 q = p+2^(len-i-1) 或 q0
8. gcd(q, n) 或 gcd(q0, n) 验证因式分解
9. AES padding oracle: pt[::-1] 后 N 个 num 字符结尾则 True
10. 爆破每个 ASCII 字符
11. go/kotlin: position_map 位置映射 38 字符
12. CRT RSA: p-q 已知，二次方程求 p, q, r

## 关键 payload

```
PGConnectionPoolDataSource.getPooledConnection → invoke Method
```

## 经验教训

黑名单 ban 反射 + Runtime + TemplatesImpl 改用 PropertyUtilsBean；FreeMarker 用 springMacroRequestContext 绕沙箱。

## 标签

CommonsBeanutils、PropertyUtilsBean反射、BeanComparator、TiedMapEntry、BadAttributeValueExpException、黑名单绕过、Spring FreeMarker、AES_padding_oracle、go位置映射、RSA_CRT

## 参考来源

- https://www.ctfiot.com/153097.html
- 原文件：2023安洵杯_WriteUp_By_Mini-Venom.full.md

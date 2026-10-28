---
title: "从TCTF的3rm1学习java动态代理"
category: web
tags: ["TCTF/0CTF 3rm1", "web", "Java", "动态代理", "InvocationHandler", "Proxy.newProxyInstance"]
signals: ["TCTF/0CTF 3rm1 2022", "Java", "动态代理", "InvocationHandler", "Proxy.newProxyInstance", "反射", "字段修改", "反序列化", "AOP", "deserialize", "object", "StudentInnovation", "Student", "SubmitWork"]
difficulty: medium
source: "https://www.ctfiot.com/62847.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从TCTF的3rm1学习java动态代理

> 赛事：TCTF/0CTF 3rm1 2022 | 方向：web | 难度：medium | 工具：Java

## 一句话总结

通过 Java 动态代理 + 反射修改 InvocationHandler.object 字段实现 AOP 链式攻击。

## 攻击链

1. 静态代理 StudentInnovation 包装 Student 实现 SubmitWork() 与 count++
2. JDK 动态代理 InvocationHandler.invoke 拦截所有方法
3. Proxy.newProxyInstance(classLoader, interfaces, handler) 返回代理对象
4. handler.setStudent 反射修改 object 字段切换目标
5. 嵌套代理: myProxy(backdoor) 作为 ProxyHandler.object
6. 反射 field.set(handler, proxyInstance) 替换目标为恶意 backdoor
7. proxyHello.attack() 实际调用 backdoor.exec("calc")
8. 触发动态代理链 invoke → method.invoke(object) → Runtime.exec

## 关键 payload

```
Proxy.newProxyInstance(classLoader, new Class[]{Teacher.class}, backdoorhandler)
```

## 经验教训

Java 反序列化链常与动态代理耦合，Proxy.newProxyInstance + InvocationHandler 可实现任何接口的包装；通过反射修改 handler 私有 object 字段可把任意类注入到调用链。

## 标签

Java、动态代理、InvocationHandler、Proxy.newProxyInstance、反射、字段修改、反序列化、AOP

## 参考来源

- https://www.ctfiot.com/62847.html
- 原文件：从TCTF的3rm1学习java动态代理.full.md

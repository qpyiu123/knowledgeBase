---
title: "2023 年第八届上海市大学生网络安全大赛 Writeup"
category: web
tags: ["上海大学生网安大赛 2023", "web", "Cookie窃取", "express_session_secret", "vm2_3.9.16_sandbox_escape", "Spring_原生反序列化"]
signals: ["上海大学生网安大赛 2023 2023", "Cookie窃取", "express_session_secret", "vm2_3.9.16_sandbox_escape", "Spring_原生反序列化", "AliyunCTF_2023", "easy_log_PHP_RCE", "PWN整数溢出", "KeyBox堆重叠", "esoteric", "cookie", "vm2", "sandbox", "Spring"]
difficulty: hard
source: "https://www.ctfiot.com/117690.html"
tools: ["PHP", "Python", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年第八届上海市大学生网络安全大赛 Writeup

> 赛事：上海大学生网安大赛 2023 2023 | 方向：web | 难度：hard | 工具：PHP、Python、Spring

## 一句话总结

上海大学生 8 题：cookie 窃取+vm2 sandbox+Spring 反序列化+无参数 RCE+Python 沙箱+KeyBox 整数溢出。

## 攻击链

1. CookieBack: 注释提示 send cookie to /cookie?data endpoint
2. /cookie?data=connect.sid=... 自取 cookie 再访问
3. easy_node: vm2 3.9.16 sandbox escape (Snyk SNYK-JS-VM2-5537100)
4. length 属性覆盖绕黑名单
5. Error.toString Proxy + apply 拿到 process
6. fun_java: SpringBoot 原生反序列化 (AliyunCTF 2023 bypassit1)
7. Jackson POJONode + BadAttributeValueExpException + TemplatesImpl
8. easy_log: username[]=PHP 代码 注入 + 无参数 RCE
9. getallheaders()['Tao'] = system('cat /S3cret_1S_H3re')
10. ezpython: Python 沙箱逃逸 + __builtins__[''eval'']
11. PWN KeyBox: 整数溢出 -2^63+0xc 绕 key 验证
12. 堆重叠 + 改 v9 指针为后门函数
13. ssql: 模拟 MySQL 数据库 + off-by-one + 0x291 fake size

## 关键 payload

```
vm2 沙箱逃逸: err.name = {toString: new Proxy(() => "", {apply(target, thiz, args) {...}})}
```

## 经验教训

vm2 3.9.16 用 Error+Proxy+apply 绕过；Spring Boot 原生反序列化走 AliyunCTF bypassit1 路线；无参数 RCE 用 getallheaders()。

## 标签

Cookie窃取、express_session_secret、vm2_3.9.16_sandbox_escape、Spring_原生反序列化、AliyunCTF_2023、easy_log_PHP_RCE、PWN整数溢出、KeyBox堆重叠、ssql菜单

## 参考来源

- https://www.ctfiot.com/117690.html
- 原文件：2023年第八届上海市大学生网络安全大赛Writeup.full.md

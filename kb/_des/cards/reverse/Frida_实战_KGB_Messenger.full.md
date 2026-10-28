---
title: "Frida 实战 KGB Messenger"
category: reverse
tags: ["KGB Messenger CTF App", "reverse", "frida", "android", "kgb", "russia"]
signals: ["KGB Messenger CTF App 2024", "frida", "android", "kgb", "russia", "system-getProperty", "base64", "login", "ctf-app", "reverse", "Frida", "KGB", "Messenger", "hook"]
difficulty: medium
source: "https://www.ctfiot.com/169480.html"
tools: ["Frida"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Frida 实战 KGB Messenger

> 赛事：KGB Messenger CTF App 2024 | 方向：reverse | 难度：medium | 工具：Frida

## 一句话总结

Frida闯关KGB Messenger：4关hook俄罗斯判断+base64密码+登录

## 攻击链

1. 第1关: hook System.getProperty("user.home") 强制返回"Russia
2. 第2关: hook System.getenv(String) 返回"FLAG{57ERL1NG_4RCH3R}" base64
3. 解码: base64 -d "RkxBR3s1N0VSTDFOR180UkNIM1J9Cg==" → FLAG{57ERL1NG_4RCH3R}
4. 第3关: 用户名codenameduchess登录
5. 第4关: hook LoginActivity.j() 强制true
6. 后续关卡: 算法反推+Frida hook

## 关键 payload

```
FLAG{57ERL1NG_4RCH3R}
```

## 经验教训

Frida实战CTF App：System.getProperty/Environment反俄判断

## 标签

frida、android、kgb、russia、system-getProperty、base64、login、ctf-app

## 参考来源

- https://www.ctfiot.com/169480.html
- 原文件：Frida_实战_KGB_Messenger.full.md

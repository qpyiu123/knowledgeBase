---
title: "2025 鹏城杯 Writeup by Mini-Venom"
category: web
tags: ["鹏城杯", "web", "myZoo菜单pwn", "Heartbeat_Out_of_Bounds", "MQTT hash31 auth", "Pivoting栈迁移"]
signals: ["鹏城杯 2025", "myZoo菜单pwn", "Heartbeat_Out_of_Bounds", "MQTT hash31 auth", "Pivoting栈迁移", "ez_java JWT HS512", "/download path=uploads/..%2fWEB-INF", "tar路径穿越", "web.xml覆盖jsp-file", "heap_exploit", "myZoo", "pwn", "MQTT", "Heartbeat"]
difficulty: hard
source: "https://www.ctfiot.com/286973.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 鹏城杯 Writeup by Mini-Venom

> 赛事：鹏城杯 2025 | 方向：web | 难度：hard

## 一句话总结

鹏城杯 2025 7 题 — myZoo 菜单 pwn + MQTT Heartbeat TOCTOU + Pivoting 栈迁移 + ez_java JWT HS512+tar 写 shell.xml + ez_php Session LFI + Uplssse spl_autoload 0.5s 竞争 + ezDjango pickle RCE + LCG 逆推。

## 攻击链

1. myZoo: 菜单 1/2/3 选项, payload b''a''*4+p64(0x1FB9) 触发后门, %23$p 泄栈拿 libc/heap/stack
2. Heartbeat_Out_of_Bounds: MQTT hash31 算 auth, set_vin TOCTOU 竞态 sleep(2) 期间改合法 vin
3. Pivoting: 拿到 libc 但栈低, 调高栈 + leave_ret 二次栈迁移
4. ez_java: /download?path=uploads/..%2fWEB-INF 绕, JwtUtil.class 拿 secret-secret-secret-secret-secret-secret-secret-secret-secret-secret-secret
5. jwt.encode HS512 sub=admin exp=1999999999
6. admin/upload 上传 tar, entry.getName()="/../WEB-INF/shell.xml" 写 jsp
7. 再传 web.xml 加 jsp-file 映射, 访问 /shell RCE
8. ez_php: Cookie: identification=Tzo...Session\User 走 dashboard.php?filename= 绕后缀
9. Uplssse: 恶 .inc 上传, Cookie O:4:Evil 触发 spl_autoload, 0.5s 竞争写 shell.php
10. ezDjango: str.format ssti + copy_file 写恶意 pickle 到 cache, pickle.load() RCE
11. true_or_false: LCG (A=1103515245, B=12345, MOD=2^31) 8字节块反推 seed

## 关键 payload

```
JWT HS512 secret-secret-secret-secret-secret-secret-secret-secret-secret-secret-secret / MQTT hash31 auth TOCTOU / tar /../WEB-INF 路径穿越写 shell.xml / 0.5s 竞争 .inc autoload / pickle.copy_file RCE / LCG 反推 seed
```

## 经验教训

JWT 密钥在 .class 文件中是字符串常量 (strings 命令可读)；tar 路径穿越 + JSP 映射 web.xml 的 servlet 元素是关键链；MQTT hash31 是 (31*x+ord) 累加;LCG 单块反推 seed 需先解 lcg.

## 标签

myZoo菜单pwn、Heartbeat_Out_of_Bounds、MQTT hash31 auth、Pivoting栈迁移、ez_java JWT HS512、/download path=uploads/..%2fWEB-INF、tar路径穿越、web.xml覆盖jsp-file、ez_php Session+file包含、Uplssse spl_autoload .inc 0.5s竞争、ezDjango pickle反序列化、true_or_false LCG、lcg反推seed

## 参考来源

- https://www.ctfiot.com/286973.html
- 原文件：2025鹏城杯_Writeup_by_Mini-Venom.full.md

---
title: "2025 鹏云杯山东省第十二届网络安全技能大赛总决赛"
category: web
tags: ["鹏云杯", "web", "truecrypt2john", "SecDisk", "哈希字典爆破", "MD5单字符查表"]
signals: ["鹏云杯 2025", "truecrypt2john", "SecDisk", "哈希字典爆破", "MD5单字符查表", "flag{51e13c0e21172adf1883b515f52afb80}", "?a[]=123&b[]=456参数污染", "printf fmtstr_payload", "setvbuf改system", "web_unknown", "MD5", "chars", "pcb5-printf", "fmtstr_payload"]
difficulty: medium
source: "https://www.ctfiot.com/275628.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 鹏云杯山东省第十二届网络安全技能大赛总决赛

> 赛事：鹏云杯 2025 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

鹏云杯 2025 — SecDisk truecrypt2john 字典爆破 + MD5 单字符查表 (chars 字典) + pcb5-printf fmtstr_payload 改 setvbuf=system + 0x404100 写 /bin/sh + 0x404018 ret gadget。

## 攻击链

1. SecDisk: truecrypt2john 提取 hash → john 字典爆破
2. 哈希: 单字符 MD5 字典爆破, chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~{}
3. 输出: flag{51e13c0e21172adf1883b515f52afb80}
4. pcb5: ?a[]=123&b[]=456 参数污染 (数组绕)
5. pcb5-printf: fmtstr_payload(8, {0x404038=system, 0x404070=0x404100, 0x404100="/bin/sh", 0x404018=ret_gadget}) 改 setvbuf 入口
6. pcb5-pwn: chunk 菜单 add/delete/show/edit

## 关键 payload

```
truecrypt2john SecDisk / MD5(单字符) 查表 / fmtstr_payload(8, {setvbuf=system, stdin=0x404100, 0x404100="/bin/sh", 0x404018=ret})
```

## 经验教训

fmtstr_payload 偏移从 8 起 (amd64 前 6 个 reg+retaddr)；改 setvbuf 入口是 fmt 任意写的"换点策略"；参数 ?a[]=123 是 PHP 数组绕类型检查的经典 trick。

## 标签

truecrypt2john、SecDisk、哈希字典爆破、MD5单字符查表、flag{51e13c0e21172adf1883b515f52afb80}、?a[]=123&b[]=456参数污染、printf fmtstr_payload、setvbuf改system、0x404100写/bin/sh、chunk菜单、fmtstr_payload(8、...)

## 参考来源

- https://www.ctfiot.com/275628.html
- 原文件：2025鹏云杯山东省第十二届网络安全技能大赛总决赛题解-WriteUp（山东省网络安全竞赛的净土）.full.md

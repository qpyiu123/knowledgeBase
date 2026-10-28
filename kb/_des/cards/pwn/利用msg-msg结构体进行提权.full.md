---
title: "利用msg-msg结构体进行提权"
category: pwn
tags: ["2022 D3CTF d3kheap", "pwn", "Linux内核PWN", "msg_msg", "sk_buff", "pipe_buffer"]
signals: ["2022 D3CTF d3kheap 2022", "Linux内核PWN", "msg_msg", "sk_buff", "pipe_buffer", "堆喷", "UAF", "double free", "pipe_buf_operations", "heap_exploit", "D3CTF", "d3kheap", "pipe_buf_operations-", "release"]
difficulty: hard
source: "https://www.ctfiot.com/75106.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 利用msg-msg结构体进行提权

> 赛事：2022 D3CTF d3kheap 2022 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

D3CTF d3kheap 内核提权：msg_msg+sk_buff+pipe_buffer 三结构堆喷交叉，pipe_buf_operations->release 劫持 ROP 提权。

## 攻击链

1. 题目: 2022 D3CTF d3kheap 内核 PWN
2. 漏洞: ioctl 0x1234 分配 + 0xdead 释放, 1024 字节, 可释放两次 → UAF
3. msg_msg 结构体 0x30 头部 + 用户消息, m_ts 存长度
4. msgsnd/msgrcv 分配回收, 大小 0x30~0x1000 可控
5. Step 1: 堆喷 0x60 + 0x400 msg_msg, 中途释放 kheap, 后续 0x400 占用
6. Step 2: 第二次释放, sk_buff 喷射 (1024-320=704 字节), 写伪造 msg_msg
7. Step 3: msgrcv MSG_COPY 读取所有 socketpair, 命中 kheap 释放
8. Step 4: sk_buff 改 m_ts=0x1000, oob 越界读取
9. Step 5: 伪造 msg_msg->next 任意地址读
10. Step 6: pipe_buffer 喷射命中 kheap, 读 pipe_buf_operations 泄内核基址
11. Step 7: pipe_buf_operations->release 劫持 ROP
12. 关键地址: PREPARE_KERNEL_CRED=0xffffffff810d2ac0
13. COMMIT_CREDS=0xffffffff810d25c0
14. ANON_PIPE_BUF_OPS=0xffffffff8203fe40
15. POP_RDI_RET=0xffffffff810938f0
16. PUSH_RSI_POP_RSP_POP_4VAL_RET=0xffffffff812dbede

## 关键 payload

```
msg_msg 喷射 + sk_buff 改 m_ts 越界 + pipe_buffer 泄内核基址 + release 劫持 ROP
```

## 经验教训

内核 UAF 三结构交叉堆喷是现代 Linux 内核 PWN 标准姿势：msg_msg 控制 0x400 大小块 + sk_buff 跨 320 字节头占位 + pipe_buffer 泄内核基址 + 劫持 ops->release 触发 ROP。

## 标签

Linux内核PWN、msg_msg、sk_buff、pipe_buffer、堆喷、UAF、double free、pipe_buf_operations、ROP提权、kmalloc-1k

## 参考来源

- https://www.ctfiot.com/75106.html
- 原文件：利用msg-msg结构体进行提权.full.md

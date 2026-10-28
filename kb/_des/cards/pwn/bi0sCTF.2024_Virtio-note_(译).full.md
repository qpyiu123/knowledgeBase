---
title: "bi0sCTF 2024 Virtio-note (译)"
category: pwn
tags: ["bi0sCTF", "pwn", "qemu", "virtio", "custom-device", "oob"]
signals: ["bi0sCTF 2024", "qemu", "virtio", "custom-device", "oob", "kernel", "vm-escape", "pwn_unknown", "bi0sCTF", "Pwn", "QEMU", "virtio-note", "Escape", "virtio_note_handle_req"]
difficulty: hard
source: "https://www.ctfiot.com/182595.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# bi0sCTF 2024 Virtio-note (译)

> 赛事：bi0sCTF 2024 | 方向：pwn | 难度：hard

## 一句话总结

bi0sCTF 2024 高质量 Pwn 题，QEMU 自定义 virtio-note 设备 + 越界读写实现 VM Escape。

## 攻击链

1. 解析 QEMU 自定义 virtio 设备源码
2. 识别 virtio_note_handle_req
3. 触发 cpu_physical_memory_read OOB
4. 越界读写宿主机内存
5. 构造 vm escape 链

## 关键 payload

```
越界读 / 写 cpu_physical_memory 触发 QEMU 进程 RCE
```

## 经验教训

客制化 QEMU 设备的攻击面在 virtio backend (handle_req / handle_output) + cpu_physical_memory_* 不带范围检查。

## 标签

qemu、virtio、custom-device、oob、kernel、vm-escape

## 参考来源

- https://www.ctfiot.com/182595.html
- 原文件：bi0sCTF.2024_Virtio-note_(译).full.md

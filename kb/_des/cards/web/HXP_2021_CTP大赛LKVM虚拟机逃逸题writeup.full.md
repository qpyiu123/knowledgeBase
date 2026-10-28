---
title: "HXP 2021 CTP大赛LKVM虚拟机逃逸题writeup"
category: web
tags: ["HXP 2021 CTP", "web", "pwn", "lkvm", "kvmtool", "virtio"]
signals: ["HXP 2021 CTP 2021", "pwn", "lkvm", "kvmtool", "virtio", "oob-read-write", "rop", "jop", "hypervisor-escape", "web_unknown", "HXP", "LKVM", "OOB", "JOP"]
difficulty: hard
source: "https://www.ctfiot.com/24005.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HXP 2021 CTP大赛LKVM虚拟机逃逸题writeup

> 赛事：HXP 2021 CTP 2021 | 方向：web | 难度：hard

## 一句话总结

HXP 2021 LKVM虚拟化逃逸：virtio OOB读写+JOP+execl宿主shell

## 攻击链

1. 攻击面: virtio-console/net/balloon 0xD2000000-0xD20000FF MMIO
2. 越界读/写：config结构体后0x100字节
3. 信息泄露：bln_dev指针+lkvm基址
4. 控制RIP: exit_lists数组指针覆盖
5. virtio_pci__data_out VIRTIO_PCI_QUEUE_PFN调用init_vq
6. vq=0x16 让bdev->vqs[0x16]指向exit_lists
7. echo c > /proc/sysrq-trigger 触发内核崩溃调用退出处理
8. t->init(kvm) 跳到ROP/JOP链
9. 伪init_item: 0x41填充
10. ret gadget: virtio_net_exec_script
11. 跳到 mov rax,[rbx+0x28]; mov rdi,rbx; ...
12. 最终execl("/bin/sh", "", null) 宿主机shell

## 关键 payload

```
bdev->vqs[0x16] = exit_lists指针 + echo c > /proc/sysrq-trigger
```

## 经验教训

lkvm exit_lists可被OOB覆盖+内核崩溃触发宿主RCE

## 标签

pwn、lkvm、kvmtool、virtio、oob-read-write、rop、jop、hypervisor-escape、cve-2021-45464

## 参考来源

- https://www.ctfiot.com/24005.html
- 原文件：HXP_2021_CTP大赛LKVM虚拟机逃逸题writeup.full.md

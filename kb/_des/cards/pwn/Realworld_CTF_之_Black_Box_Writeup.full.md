---
title: "Realworld CTF - Black Box Writeup (CVE-2020-14364 QEMU USB 逃逸)"
category: pwn
tags: ["Realworld CTF", "pwn", "qemu-escape", "usb-uhci", "cve-2020-14364", "vm-escape"]
signals: ["Realworld CTF 2021", "qemu-escape", "usb-uhci", "cve-2020-14364", "vm-escape", "setup_len-overflow", "do_token_setup", "s-setup_buf", "data_buf-overflow", "pwn_unknown", "Realworld", "CTF", "Black", "Box"]
difficulty: hard
source: "https://www.ctfiot.com/27566.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Realworld CTF - Black Box Writeup (CVE-2020-14364 QEMU USB 逃逸)

> 赛事：Realworld CTF 2021 | 方向：pwn | 难度：hard

## 一句话总结

Realworld CTF 之 Black Box：CVE-2020-14364 QEMU 5.15 USB UHCI 驱动 do_token_setup setup_len 用户可控 → data_buf 越界读写 → 改 UHCI frame_list 任意地址写 → 时钟劫持 → QEMU host RCE。

## 攻击链

1. QEMU 5.15.0 + x86_64 + softmmu + usb-tablet + uhci 驱动
2. CVE-2020-14364: usb_process_one → do_token_setup → s->setup_len 校验不足
3. do_token_setup: s->setup_len = (s->setup_buf[7]<<8)|s->setup_buf[6] 用户可控
4. do_token_in: len = s->setup_len - s->setup_index, 多次 IN 累加 setup_index
5. 越界读写: data_buf[0x1000] + setup_index 可控 越界 USBDevice 结构
6. s->setup_index 设为 -8 越界改 s->setup_buf[0] USB_DIR_IN
7. 越界写 setup_index 控制 USBDevice.setup_state
8. UHCI 协议: Frame List + QH + TD (Token Descriptor)
9. UHCI_TD link/ctrl/token/buffer 32 字节
10. Vf=depth first / Q=TD or QH / T=last
11. max_len = ((td->token >> 21) + 1) & 0x7ff
12. uhci_handle_td 设置 p->iov.size = max_len
13. step1: 正常 token_setup 设置 setup_state
14. step2: token_setup size=0x5000 扩大 setup_len 操作范围
15. step3: token_out 越界写 setup_index=-8
16. 改 setup_buf[0] USB_DIR_IN 标记 → do_token_in 越界读
17. 利用 pi (physical address) + virt (virtual address) 双重映射
18. data_buf 0x7fffxxxx 虚拟机地址 / device 0x5ff55xxx 物理机虚拟地址
19. g_malloc0 分配 QH/TD buffer + UHCI port 写入 s->fl_base_addr
20. uhci_port_write 0x10/0x12 端口自定义 frame_list_base
21. timer_mod_ns 触发 uhci_frame_timer → uhci_process_frame
22. 完整利用: 覆盖 timer_list + 时钟伪造 → 任意地址写 + system

## 关键 payload

```
do_token_setup(size=0x5000) + do_token_out(offset=-8) 改 setup_index + do_token_in(OOB read) 泄物理地址
```

## 经验教训

USB UHCI 协议复杂但 do_token_setup 中的 setup_len 赋值后检测是经典漏洞；data_buf 越界读写 + setup_index 整数下溢是 USB 设备逃逸经典攻击面；QEMU VM 逃逸需结合 virt+phys 双地址空间分析。

## 标签

qemu-escape、usb-uhci、cve-2020-14364、vm-escape、setup_len-overflow、do_token_setup、s-setup_buf、data_buf-overflow

## 参考来源

- https://www.ctfiot.com/27566.html
- 原文件：Realworld_CTF_之_Black_Box_Writeup.full.md

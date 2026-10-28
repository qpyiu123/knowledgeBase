---
title: "D3CTF 2024 Writeup - Polaris 战队"
category: pwn
tags: ["D3CTF", "pwn", "qemu-vm-escape", "mmio-pmio", "php-zend-allocator", "off-by-one"]
signals: ["D3CTF 2024", "qemu-vm-escape", "mmio-pmio", "php-zend-allocator", "off-by-one", "pwn-2", "proc-mem-write", "pwn_unknown", "D3CTF", "Polaris", "PWN", "QEMU", "PHP", "proc"]
difficulty: hard
source: "https://www.ctfiot.com/177070.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# D3CTF 2024 Writeup - Polaris 战队

> 赛事：D3CTF 2024 | 方向：pwn | 难度：hard | 工具：PHP

## 一句话总结

D3CTF 2024 Polaris 战队 PWN 方向三道高质量 WP：QEMU 客制化设备/PHP 扩展/proc mem 改 libc。

## 攻击链

1. D3BabyEscape: mmio 设 offset=0x100 越界
2. mmio_read 泄 srandom libc 地址
3. pmio_read(0)==666 触发 write_enable
4. mmio_write(64) 走 rand_r 路径
5. 写入 system + "/sh" 字符串
6. PwnShell: PHP Zend small allocator off-by-one
7. 修改 node->buf 为 GOT 表地址
8. editHacker 改 GOT 为 system
9. bash -c reverse shell
10. write_flag_where: 写 /proc/self/mem 改 libc code
11. 爆破偏移触发 flag 输出

## 关键 payload

```
QEMU MMIO+PMIO + PHP off-by-one + /proc/self/mem code 改写
```

## 经验教训

QEMU 客制化设备的"内容大小越界 + 双接口(MMIO/PMIO)"是 CTF PWN 新热点；PHP Zend 分配器 off-by-one 配合 small bin 错位利用很优雅。

## 标签

qemu-vm-escape、mmio-pmio、php-zend-allocator、off-by-one、pwn-2、proc-mem-write

## 参考来源

- https://www.ctfiot.com/177070.html
- 原文件：D3CTF_2024_Writeup_–Polaris战队.full.md

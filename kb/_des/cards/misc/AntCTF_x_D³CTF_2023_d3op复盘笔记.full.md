---
title: "AntCTF x D³CTF 2023 d3op 复盘笔记"
category: misc
tags: ["D³CTF", "misc", "OpenWrt 22.03.3", "gambox", "squashfs-root", "diff rootfs"]
signals: ["D³CTF 2023", "OpenWrt 22.03.3", "gambox", "squashfs-root", "diff rootfs", "base64 ubus module", "/etc/shadow $6$JlPmKq", "unauthenticated.json", "network.interface", "iot", "AntCTF", "CTF", "d3op", "OpenWrt"]
difficulty: hard
source: "https://www.ctfiot.com/116000.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AntCTF x D³CTF 2023 d3op 复盘笔记

> 赛事：D³CTF 2023 | 方向：misc | 难度：hard

## 一句话总结

AntCTF x D³CTF 2023 d3op — OpenWrt 22.03.3 固件 diff 找 base64 ubus 模块 + /etc/shadow 哈希 + /flag + network.interface 攻击面。

## 攻击链

1. 解 gambox 固件 → OpenWrt 22.03.3 r20028-43d71ad93e squashfs-root
2. 从官网下载同版本 OpenWrt 22.03.3 diff
3. diff 关键: /etc/shadow root $6$JlPmKq/ZhqQ0I6V6$ 哈希密码
4. 多了 /flag 文件
5. 多了 /usr/libexec/rpcd/base64 (ubus 模块)
6. unauthenticated.json 加 base64 encode/decode 允许未授权
7. 多了 /etc/config/network
8. 漏洞点: base64 模块 + network.interface 配置
9. 启动后 init_base64() + main 接受 list/encode/decode 命令
10. read_input(0, v6, 0xFFF) 读 stdin
11. sub_402478 解析 + sub_403C90 找 "input" 字段 + sub_4059D0 验证

## 关键 payload

```
diff rootfs / base64 ubus / unauthenticated.json / $6$ shadow / /flag / network.interface / init_base64 + check_method
```

## 经验教训

OpenWrt 固件题标准做法:官网下同版本 diff;base64 是 ubus 微系统总线模块;$6$ 是 sha512 crypt;unauthenticated.json 控制 ACL。

## 标签

OpenWrt 22.03.3、gambox、squashfs-root、diff rootfs、base64 ubus module、/etc/shadow $6$JlPmKq、unauthenticated.json、network.interface、vuln_point、init_base64、check_method

## 参考来源

- https://www.ctfiot.com/116000.html
- 原文件：AntCTF_x_D³CTF_2023_d3op复盘笔记.full.md

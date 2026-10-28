---
title: "2021 西湖论剑 IOT RW WriteUp"
category: pwn
tags: ["2021 西湖论剑 IOT (海特实验室)", "pwn", "IoT", "ARM924EJS", "AVR", "FIT-Image"]
signals: ["2021 西湖论剑 IOT (海特实验室) 2021", "IoT", "ARM924EJS", "AVR", "FIT-Image", "dfu-util", "dumpimage", "dtc", "sunloginclient", "rce", "auth_bypass", "FIT", "Image", "dts"]
difficulty: hard
source: "https://www.ctfiot.com/30841.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2021 西湖论剑 IOT RW WriteUp

> 赛事：2021 西湖论剑 IOT (海特实验室) 2021 | 方向：pwn | 难度：hard

## 一句话总结

2021 西湖论剑 IoT RW：FIT Image dts 注入 + dfu 刷回 + MQTT 协议 + USB 设备模拟

## 攻击链

1. 海特实验室开发板：ARM924EJS (Linux IoT) + AVR (单片机)
2. OTG → 网口；UART 115200 串口；TF 卡 hsqs 文件加载赛题
3. dfu-util -l 看到 5 分区: rom/kernel/env/u-boot/all
4. dfu-util -R -a kernel -U kernel.itb 导出 FIT Image
5. dumpimage -l 看 3 个子镜像: kernel / initrd / fdt
6. dtc -I dtb -O dts fdt.dtb 改 bootargs 加 rdinit=/bin/sh
7. 改 dts → 打包回 itb → dfu-util -D 刷回开发板
8. /bin/sh → 抹 /etc/shadow → /sbin/init → 完整 shell
9. MQTT 题目: mosquitto_pub -t 2022/hatlab/flag -m ''oiU7m9ipyqFdzkUFb1vfkabZ7IqiAefslrc3ovql2dA=
10. 向日葵 sunloginclient 11.0.0.36662 命令注入（CVE 复现）
11. USB Hacker: 把板子改造成 USB Mass storage 攻击目标硬件

## 关键 payload

```
bootargs = "console=ttyS0,115200 rdinit=/bin/sh
```

## 经验教训

FIT Image 是嵌入式 Linux 启动标准；dfu-util 是 IoT 调试必备；MQTT 协议是 IoT 通讯主流

## 标签

IoT、ARM924EJS、AVR、FIT-Image、dfu-util、dumpimage、dtc、sunloginclient、mqtt、mosquitto_pub、Allwinner、Linux-Embedded、USB-Hacker

## 参考来源

- https://www.ctfiot.com/30841.html
- 原文件：2021西湖论剑IOT_RW-WriteUp.full.md

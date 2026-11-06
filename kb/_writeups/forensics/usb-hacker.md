---
title: "USB Hacker：先认抓包头，再还原键盘输入"
category: "forensics"
kind: "writeup"
tags: ["PCAPNG", "USB HID", "键盘报告"]
signals: ["链路类型 220", "usbmon", "端点 0x81"]
source: "https://github.com/W4terDr0p/W4terCTF-2023/tree/main/challenges/forensics/usb-hacker"
origin_id: "r66-usb-hacker"
relates_to: ["forensics/pcap-basics.md"]
verification: "本机原附件回验"
also_category: ["misc"]
---

# USB Hacker：先认抓包头，再还原键盘输入

W4terCTF 2023 · 杂项取证 · [赛事原附件](https://github.com/W4terDr0p/W4terCTF-2023/tree/main/challenges/forensics/usb-hacker)。本机从 252 条键盘报告还原出符合题面格式的内容。

## 先看这一步

先认抓包的链路类型。本题是 Linux 的 64 字节 usbmon 头，取到键盘报告后才处理按键、Shift 和退格。

**适用时**：链路类型、端点和报告大小须与本题一致。 **留意**：Windows USBPcap 的头布局不同。

第一步读 PCAPNG 接口描述块：本题链路类型是 220，对应 Linux 的 usbmon 64 字节头。误用 Windows USBPcap 的头，会把别的字段当成长度，最后提取不到数据。

1. 对每个 USB 数据包先读方向、传输类型和已捕获长度。本题需要端点 `0x81` 的中断输入完成事件；只取 8 字节的报告，跳过发起请求和空报告。
2. 第一个字节是修饰键，第二个保留，后六字节是按键编号。先用编号映射字符，再按 Shift 和 Caps Lock（大小写锁定）决定大小写。按下 Caps Lock 时切换状态，不能只按每帧的 Shift 位判断。
3. 对相邻报告做比较，只处理新按下的键；键还按着时不要重复添字。遇到退格要删除前一字符，回车按换行处理。

本题完成后没有未识别按键。可用 Wireshark 的 USB 字段交叉核对；手写解析时，按 [Linux usbmon 格式说明](https://cdn.kernel.org/doc/html/latest/usb/usbmon.html)读本题的包头，再套键盘映射。

## 配套代码

`kb/_code/r66/misc_samples.py`。从代码所在目录运行 `python misc_samples.py usb-hacker 原附件`。依赖见脚本开头；运行后会显示核对结果。

---
title: "【2024御网杯】线下半决赛 Misc WriteUp"
category: misc
tags: ["御网杯", "misc", "0-width-stego", "xlsx-zip-mislabel", "PNG-file-append", "pyc-Rot13-base64"]
signals: ["御网杯 2024", "0-width-stego", "xlsx-zip-mislabel", "PNG-file-append", "pyc-Rot13-base64", "RTMP-pcap-extract", "tcpflow", "ffmpeg-frames", "misc_unknown", "Misc", "RTMP", "simple_analysis", "kitty", "xlsx"]
difficulty: easy
source: "https://www.ctfiot.com/212477.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【2024御网杯】线下半决赛 Misc WriteUp

> 赛事：御网杯 2024 | 方向：misc | 难度：easy | 工具：C、Python

## 一句话总结

御网杯 2024 高职组半决赛 4 题 Misc 复盘，0 宽隐写 + 文件套娃 + 多层编解码 + RTMP 抽帧。

## 攻击链

1. simple_analysis 0 宽度隐写 330k 在线工具秒解/kitty 附件 xlsx 实为 zip 包（50 4B 03 04 14 00）→解压得 kitty.xml 实为 PNG（89 50 4E 47）/aixin Mx12ItE2XjqgYEBDADA0WGEhXQI2W2I4JNIiWEJEA05So2nrlQIU 经 Rot13→Rot16→Base64→Reverse 多层解码/直播流量 pcapng 过滤 _ws.col.info == "Video Data" + tcpflow -T %T_%A%C%c.rtmp -r rtmp.pcapng 拆流 → rtmp2flv.py 转 flv → ffmpeg -vf "fps=1" frame%04d.png 抽帧

## 关键 payload

```
Mx12ItE2XjqgYEBDADA0WGEhXQI2W2I4JNIiWEJEA05So2nrlQIU  ROT13 16 次 → base64 → reverse
```

## 经验教训

0 宽度 Unicode 隐写用 330k 工具秒解；xlsx/png/zip 等格式头互转是常见套娃；RTMP 流量过滤 Video Data 后用 tcpflow 抽 + rtmp2flv + ffmpeg 三步抽帧是经典工作流。

## 标签

0-width-stego、xlsx-zip-mislabel、PNG-file-append、pyc-Rot13-base64、RTMP-pcap-extract、tcpflow、ffmpeg-frames

## 参考来源

- https://www.ctfiot.com/212477.html
- 原文件：【2024御网杯】线下半决赛Misc_WriteUp.full.md

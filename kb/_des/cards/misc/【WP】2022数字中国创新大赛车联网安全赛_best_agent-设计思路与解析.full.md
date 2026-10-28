---
title: "【WP】2022数字中国创新大赛车联网安全赛 best_agent 设计思路与解析"
category: misc
tags: ["数字中国", "misc", "car-cybersecurity", "CAN-bus-analysis", "websocket-flow", "open_right_door"]
signals: ["数字中国 2022", "car-cybersecurity", "CAN-bus-analysis", "websocket-flow", "open_right_door", "git-info-leak", "python-CRLF-CVE-2019-9947", "Apache-HTTPD-header-parse", "forensic_traffic", "best_agent", "CAN", "websocket", "git", "Python"]
difficulty: medium
source: "https://www.ctfiot.com/36300.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2022数字中国创新大赛车联网安全赛 best_agent 设计思路与解析

> 赛事：数字中国 2022 | 方向：misc | 难度：medium | 工具：Python

## 一句话总结

2022 数字中国车联网安全赛 best_agent，CAN 总线流量分析 + websocket 实时流量抓取 + git 信息泄露。

## 攻击链

1. 1. CAN 流量分析 + websocket 流量获取 + git 信息泄露 + Python CRLF 注入 CVE-2019-9947 + Apache HTTPD 请求头解析/2. 探索页面 http 触发操作 + 逃跑页面 websocket 触发操作/3. 多次调 open_left 接口 + 抓 CAN 流量 + 找重复开右车门请求/4. eventlet.monkey_patch + websocket.WebSocketApp on_message + 写入 after_{max_round}.log

## 关键 payload

```
open_left 接口 + 重复 CAN 流量 + websocket on_message
```

## 经验教训

车联网 CAN 流量分析 + websocket 实时流量是车联网 CTF 核心；多次触发同操作找重复帧是 CAN 流量特征提取标准方法。

## 标签

car-cybersecurity、CAN-bus-analysis、websocket-flow、open_right_door、git-info-leak、python-CRLF-CVE-2019-9947、Apache-HTTPD-header-parse

## 参考来源

- https://www.ctfiot.com/36300.html
- 原文件：【WP】2022数字中国创新大赛车联网安全赛_best_agent-设计思路与解析.full.md

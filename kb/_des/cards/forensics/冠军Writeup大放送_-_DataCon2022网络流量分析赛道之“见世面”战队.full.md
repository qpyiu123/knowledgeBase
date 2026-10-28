---
title: "冠军Writeup大放送 | DataCon2022网络流量分析赛道之\"见世面\"战队"
category: forensics
tags: ["DataCon2022 网络流量分析", "forensics", "DataCon", "流量分析", "挖矿检测", "智能蜜罐"]
signals: ["DataCon2022 网络流量分析 2022", "DataCon", "流量分析", "挖矿检测", "智能蜜罐", "CICFlowMeter", "TLS ChangeCIPherSpec", "OneClassSVM", "IsolationForest", "forensic_traffic", "DataCon2022", "TLS", "ChangeCIPherSpec", "Level1"]
difficulty: medium
source: "https://www.ctfiot.com/91160.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 冠军Writeup大放送 | DataCon2022网络流量分析赛道之"见世面"战队

> 赛事：DataCon2022 网络流量分析 2022 | 方向：forensics | 难度：medium | 工具：Python

## 一句话总结

DataCon2022 流量分析冠军 见世面：挖矿流量检测 (TLS ChangeCIPherSpec) + 智能蜜罐构建 Level1/2。

## 攻击链

1. 广州大学方班 (方滨兴院士班) 见世面战队 5 人
2. 第1章 挖矿流量检测: black_ssl3.pcap 自抓加密挖矿流量
3. CICFlowMeter 处理 cryptomining.pcap → 流量特征提取
4. TLS ChangeCIPherSpec 包分析: 加密挖矿特征
5. mining_check_finish.py check_stream 函数
6. 机器学习: OneClassSVM / IsolationForest 异常检测
7. 第2章 智能蜜罐 Level1: 请求重发器 datacon_l1_poc_sent.py
8. 第3章 智能蜜罐 Level2: 字符串转换+正则匹配 datacon_l2_server_clean.py
9. 工具: Suricata / Zeek / NBMiner / Xray / scan4all
10. 方班 loom 战队 2019 首届 DataCon 冠军 + 2020 复赛奖项

## 关键 payload

```
CICFlowMeter + TLS ChangeCIPherSpec + OneClassSVM + 智能蜜罐请求重发器
```

## 经验教训

加密挖矿流量检测靠 TLS ChangeCIPherSpec 包特征 + CICFlowMeter 流量特征 + OneClassSVM 异常检测；智能蜜罐靠请求重发器测试响应差异。

## 标签

DataCon、流量分析、挖矿检测、智能蜜罐、CICFlowMeter、TLS ChangeCIPherSpec、OneClassSVM、IsolationForest、Suricata、Zeek

## 参考来源

- https://www.ctfiot.com/91160.html
- 原文件：冠军Writeup大放送_-_DataCon2022网络流量分析赛道之“见世面”战队.full.md

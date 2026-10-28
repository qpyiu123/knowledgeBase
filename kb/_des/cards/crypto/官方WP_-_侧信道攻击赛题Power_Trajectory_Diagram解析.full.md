---
title: "侧信道攻击赛题Power Trajectory Diagram官方WP - 大鲲智联+信安国赛"
category: crypto
tags: ["第十七届全国大学生信息安全竞赛-创新实践能力赛初赛(2024 CISCN)", "crypto", "侧信道攻击", "功耗轨迹", "Power_Trace", "npz文件"]
signals: ["第十七届全国大学生信息安全竞赛-创新实践能力赛初赛(2024 CISCN) 2024", "侧信道攻击", "功耗轨迹", "Power_Trace", "npz文件", "numpy", "matplotlib", "皮尔逊相关系数", "corrcoef", "crypto_rsa", "CISCN", "ciscn_2024_12", "argmin", "npz"]
difficulty: medium
source: "https://www.ctfiot.com/187746.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 侧信道攻击赛题Power Trajectory Diagram官方WP - 大鲲智联+信安国赛

> 赛事：第十七届全国大学生信息安全竞赛-创新实践能力赛初赛(2024 CISCN) 2024 | 方向：crypto | 难度：medium

## 一句话总结

大鲲智联+CISCN 2024侧信道功耗分析3种思路破解_ciscn_2024_12位密码:人工作图/argmin最低峰/皮尔逊相关系数自动。

## 攻击链

1. 加载npz查看files(index/input/output/trace) → 4键值trace 520长度 → 思路1:plot每组trace人工判断正确密码(波谷X坐标异常) → 思路2:argmin(trace[i])找最低峰X坐标,max_index对应正确字符 → 思路3:corrcoef(avg_trace, trace[i])皮尔逊相关系数,阈值0.90过滤正确字符

## 关键 payload

```
40字符输入 × 13轮 × trace长度520 + corrcoef阈值0.90
```

## 经验教训

侧信道功耗分析经典三法:plot肉眼比较、argmin最低峰位置(正确密码因CPU执行不同而波谷X偏移)、corrcoef皮尔逊相关系数(正确字符与平均值corr<0.90,错误≥0.99);密码12位(题目说13位但第13位无效);npz格式含index/input/output/trace四键值。

## 标签

侧信道攻击、功耗轨迹、Power_Trace、npz文件、numpy、matplotlib、皮尔逊相关系数、corrcoef、伽玛实验场、大鲲智联、CISCN_2024、智能网联汽车

## 参考来源

- https://www.ctfiot.com/187746.html
- 原文件：官方WP_-_侧信道攻击赛题Power_Trajectory_Diagram解析.full.md

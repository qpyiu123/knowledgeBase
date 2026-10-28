---
title: "【一等奖方案】基于TPU平台实现人群密度估计赛题「SO-FAST」团队解题思路"
category: crypto
tags: ["2022 CCF BDCI SO-FAST TPU 密度估计", "crypto", "CCF BDCI", "TPU", "CSRNet", "INT8量化"]
signals: ["2022 CCF BDCI SO-FAST TPU 密度估计 2022", "CCF BDCI", "TPU", "CSRNet", "INT8量化", "4N Batch", "推理加速", "算能BM1684", "人群密度估计", "misc_math", "CCF", "BDCI", "SO-FAST", "INT8"]
difficulty: hard
source: "https://www.ctfiot.com/124006.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【一等奖方案】基于TPU平台实现人群密度估计赛题「SO-FAST」团队解题思路

> 赛事：2022 CCF BDCI SO-FAST TPU 密度估计 2022 | 方向：crypto | 难度：hard

## 一句话总结

2022 CCF BDCI TPU 密度估计冠军 SO-FAST：CSRNet + INT8 量化 + 4N Batch + 2×2 图片划分 + 推理加速。

## 攻击链

1. 第十届 CCF 大数据与计算智能大赛
2. 队伍: SO-FAST (宋礼/柯嵩宇/包锴楠) 京东/上交/西南交大
3. 任务: CSRNet 在 TPU (算能 BM1684) 平台部署
4. Step 1: 模型选择 CSRNet (FP32 vs INT8 对比)
5. Step 2: INT8 量化 (FP32 精度高但慢, INT8 平衡)
6. Step 3: 量化图片选择 (NWPU-Crowd 第 178 张, 大规模人群+广色差)
7. Step 4: 推理加速 1: 图片尺寸变换 (1 vs 4 张, 0.5s/张)
8. Step 4: 推理加速 2: 4N Batch (INT8+INT32 关系, 4 张一次 0.27s)
9. Step 5: BM1684 平台部署实测
10. 综合评分 score = (250-MAE)*0.2 + (500-RMSE)*0.1 + (0.4-NAE)*200 + (2-time)*100
11. A 榜 229.73 第一, B 榜 263.78 第一

## 关键 payload

```
CSRNet + INT8 + 4N Batch + 2x2 图片划分 + BM1684 部署第一
```

## 经验教训

TPU 部署 5 步流程: 模型选择→INT8 量化→量化图片筛选→推理加速 (尺寸+4N Batch)→部署实测; 4N Batch 利用 INT8+INT32 关系 4 张一次推理降一半时间。

## 标签

CCF BDCI、TPU、CSRNet、INT8量化、4N Batch、推理加速、算能BM1684、人群密度估计、A/B榜第一

## 参考来源

- https://www.ctfiot.com/124006.html
- 原文件：【一等奖方案】基于TPU平台实现人群密度估计赛题「SO-FAST」团队解题思路.full.md

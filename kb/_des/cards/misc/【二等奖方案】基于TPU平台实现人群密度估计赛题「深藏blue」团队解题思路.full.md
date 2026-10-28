---
title: "基于 TPU 平台实现人群密度估计 CCF BDCI 2022 二等奖方案"
category: misc
tags: ["CCF-BDCI", "misc", "TPU", "crowd-density-estimation", "VGG", "CSRNet"]
signals: ["CCF-BDCI 2022", "TPU", "crowd-density-estimation", "VGG", "CSRNet", "MCNN", "grid-search", "INT8-quantization", "BMODEL", "misc_unknown", "CCF", "BDCI", "INT8", "FP32"]
difficulty: medium
source: "https://www.ctfiot.com/123438.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 基于 TPU 平台实现人群密度估计 CCF BDCI 2022 二等奖方案

> 赛事：CCF-BDCI 2022 | 方向：misc | 难度：medium

## 一句话总结

2022 CCF BDCI TPU 人群密度估计：4 模型网格搜索 + INT8 量化对比 + 选 VGG FP32 144×192 拿 B 榜第二。

## 攻击链

1. 4 个预训练模型 CANNet/CSRNet/MCNN/VGG，FP32 vs INT8 BModel
2. 测试 FP32 vs INT8 在 (576,768)~(2048,2048) 输入的得分
3. CANNet 权重无法加载，跳过
4. 选 VGG（综合分 186.74/177.64）> MCNN > CSRNet
5. 网格搜索: 模型输入 [112×112, 144×144, 144×192, 224×224, 288×384, 576×768] + Batch Size [1,2,4,8,16] + 缩放 [224~2048]
6. 结论: Batch Size 影响小，固定 = 1
7. 选小图片尺寸 (288×384 ~ 768×768) + 小模型输入 (144×192) + Batch=1
8. INT8 量化 (200 张训练图 lmdb 校准) 分数反而低 → 放弃 INT8
9. 最终: FP32 BModel + 缩放 (288×384, 768×768) + 模型输入 144×192 + Batch=1
10. B 榜第二

## 关键 payload

```
VGG FP32 + 缩放 (288×384, 768×768) + 模型输入 144×192 + B 榜 #2
```

## 经验教训

网格搜索是模型选择标准方法；FP32 vs INT8 量化在精度敏感任务中 INT8 不一定更好。

## 标签

TPU、crowd-density-estimation、VGG、CSRNet、MCNN、grid-search、INT8-quantization、BMODEL、MAE-RMSE-NAE、CCF-BDCI

## 参考来源

- https://www.ctfiot.com/123438.html
- 原文件：【二等奖方案】基于TPU平台实现人群密度估计赛题「深藏blue」团队解题思路.full.md

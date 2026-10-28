---
title: 模型窃取与成员推理（Model Extraction / Membership Inference）
category: ai
tags: [model-extraction, membership-inference, shadow-model, api-query, privacy]
signals: [题目给了一个只返回预测结果的模型接口, 要求还原模型的参数或者结构, 问某个样本是否在训练集里, 给了预测接口和一批候选样本要求判断训练集成员, 接口返回 softmax 概率而不是硬标签, 提示说这是 membership inference 或者 shadow model]
difficulty: hard
source: "Shokri et al. Membership Inference Attacks (S&P 2017) / Tramèr et al. Stealing ML Models via Prediction APIs (USENIX 2016)"
tools: [python, pytorch, scikit-learn, numpy, transformers, requests]
updated: 2026-10-22
exec_yaml: ok
relates_to: [osint/anti-osint-privacy.md]
---

## 一、识别信号（题面长什么样）

- 题目给一个 `POST /predict` 接口，返回 `{"label": ..., "confidence": 0.93}`。
- 题面要求"判断某条记录是否属于训练集"。
- 给了大量候选样本和对应的模型输出，要求"还原决策边界"。
- 模型很大但训练集很小（过拟合），成员样本的置信度明显更高。
- 提示词出现 `shadow dataset`、`overfitting`、`query budget`。
- 接口有速率限制（"每分钟 60 次"），暗示要做查询效率优化。

## 二、原理

**成员推理（MIA）**
- 过拟合模型对训练样本给出**更高置信度**、更小的 loss。攻击者训练多个"影子模型"（结构同分布、数据来自同分布但已知成员/非成员），学习"置信度 → 是否成员"的判别器。
- 简化版（黑盒、无影子模型）：直接用置信度阈值 / 熵 / 预测类别与真实标签是否一致，作为打分函数。

**模型窃取（Model Extraction）**
- 目标是得到"近似等价的模型"。核心是**主动查询选择**：
  - 对分类器：随机/边界采样，用返回的软标签蒸馏；
  - 对线性/浅层模型：用正交基查询直接解方程；
  - 对决策树：用查询还原分割面（每个节点的阈值可通过二分逼近）。
- 查询预算有限时，**优先在边界附近采样**（不确定性采样）收益最高。

## 三、操作步骤

1. **探测接口**：输入格式、批量能力、返回是否含概率、有无速率限制。
2. **先做简单判定**：用 `max(prob)` 或 `-entropy` 当成员分数，在已知的少量样本上验证 AUC。
3. **边界探索**：对二分类采样两类之间的中点，二分逼近阈值，还原决策边界。
4. **蒸馏**：用自采查询集（输入 + 软标签）训练小模型，用温度参数匹配软标签分布。
5. **评估**：在留出集上比较"学生与教师"的一致率。
6. **限速优化**：批量请求、缓存、优先在高信息量样本上查询。

## 四、命令 / 脚本

```python
#!/usr/bin/env python3
# 成员推理：在黑盒接口上用置信度/熵打分（无需影子模型）
import math, requests

URL = "http://TARGET/predict"

def query(x):
    r = requests.post(URL, json={"x": x}, timeout=10)
    return r.json()["probs"]          # 返回各类概率

def member_score(probs, true_label=None):
    """分数越高越可能是训练集成员"""
    ent = -sum(p * math.log(p + 1e-12) for p in probs)
    confidence = max(probs)
    score = confidence - 0.02 * ent   # 置信度高 + 熵低
    if true_label is not None and probs[true_label] > 0.6:
        score += 0.3                  # 预测正确也是强信号
    return score

if __name__ == '__main__':
    samples = [(x, y) for x, y in load_candidates()]      # 题目提供
    scored = [(member_score(query(x), y), x, y) for x, y in samples]
    scored.sort(reverse=True)
    for s, x, y in scored[:20]:
        print('%.4f label=%s' % (s, y))
```

```python
#!/usr/bin/env python3
# 模型窃取：二分逼近决策边界，还原线性模型的阈值
import requests

URL = "http://TARGET/predict"

def pred(x):
    return requests.post(URL, json={"x": x}, timeout=10).json()["label"]

def bisect_boundary(lo, hi, iters=40):
    """在 lo(负类) 与 hi(正类) 之间找分界点"""
    for _ in range(iters):
        mid = [(a + b) / 2 for a, b in zip(lo, hi)]
        if pred(mid) == 1:
            hi = mid
        else:
            lo = mid
    return [(a + b) / 2 for a, b in zip(lo, hi)]

if __name__ == '__main__':
    print('边界点:', bisect_boundary([-1.0, -1.0], [1.0, 1.0]))
```

```python
#!/usr/bin/env python3
# 蒸馏：用查询来的 (输入, 软标签) 训练学生模型
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F

class Student(nn.Module):
    def __init__(self, din, dout):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(din, 128), nn.ReLU(),
                                 nn.Linear(128, 64), nn.ReLU(),
                                 nn.Linear(64, dout))
    def forward(self, x):
        return self.net(x)

def distill(X, soft, epochs=200, T=2.0):
    X = torch.tensor(X, dtype=torch.float32)
    soft = torch.tensor(soft, dtype=torch.float32)
    m = Student(X.shape[1], soft.shape[1])
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for e in range(epochs):
        logits = m(X)
        loss = F.kl_div(F.log_softmax(logits / T, 1), soft, reduction='batchmean') * T * T
        opt.zero_grad(); loss.backward(); opt.step()
        if e % 50 == 0:
            print('epoch %d loss %.4f' % (e, loss.item()))
    return m

if __name__ == '__main__':
    X = np.random.randn(2000, 16)
    soft = np.abs(np.random.randn(2000, 3)); soft /= soft.sum(1, keepdims=True)
    distill(X, soft)
```

## 五、常见坑 / 变体

- **返回硬标签时成员推理难做**：可用"预测稳定性"作替代信号——对同一样本多次加噪后查询，成员样本预测更稳。
- **温度与软标签**：接口若只给 top-1，就没有软标签可蒸馏，学生模型上限很低。
- **查询预算**：题目常限制查询次数，别一开始就均匀撒点，先做主动学习。
- **分布偏移**：影子模型必须与目标同分布，否则阈值会偏。
- **差分隐私模型**：加了 DP 噪声的模型，成员推理的 AUC 会明显下降，题目若刻意如此要换思路（侧信道/参数泄露）。
- **变体**：属性推理（推断敏感属性）、训练数据提取（让模型吐出原文）、模型指纹（判断是否同一模型）。

## 六、参考来源

- [Shokri et al.：Membership Inference Attacks Against Machine Learning Models](https://arxiv.org/abs/1610.05820)
- [Tramèr et al.：Stealing Machine Learning Models via Prediction APIs（USENIX Security 2016）](https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/tramer)
- [arXiv 版本：Stealing Machine Learning Models via Prediction APIs](https://arxiv.org/abs/1609.02943)
- [PyTorch 官方教程（知识蒸馏与 KL 散度）](https://pytorch.org/tutorials/beginner/knowledge_distillation_tutorial.html)
- [scikit-learn：ROC/AUC 评估（用于验证 MIA 效果）](https://scikit-learn.org/stable/modules/model_evaluation.html)

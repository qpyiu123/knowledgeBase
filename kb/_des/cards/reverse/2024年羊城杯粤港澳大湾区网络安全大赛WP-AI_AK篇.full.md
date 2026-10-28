---
title: "2024 年羊城杯粤港澳大湾区网络安全大赛 WP - AI AK 篇"
category: reverse
tags: ["羊城杯", "reverse", "NLP 对抗样本", "DistilBERT 三分类", "前缀加 happy/nothing/unhappy 反向", "very 加 0.7 阈值"]
signals: ["羊城杯 2024", "NLP 对抗样本", "DistilBERT 三分类", "前缀加 happy/nothing/unhappy 反向", "very 加 0.7 阈值", "AI 模型攻击", "SSIM 验证相似度", "reverse", "misc_unknown", "web_unknown", "web_rce", "DistilBERT", "very", "Sentiment_classification_model"]
difficulty: hard
source: "https://www.ctfiot.com/203028.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 年羊城杯粤港澳大湾区网络安全大赛 WP - AI AK 篇

> 赛事：羊城杯 2024 | 方向：reverse | 难度：hard

## 一句话总结

DistilBERT 情感分类对抗样本：反向情绪前缀 + very 提相似度。

## 攻击链

1. 1. 加载 Sentiment_classification_model (DistilBERT) + tokenizer / 2. verify_similarity 余弦相似度 ≥ 0.7 / 3. predict_model argmax(label) / 4. 对原始文本加前缀 happy/nothing/unhappy 反向 / 5. 加 "very" 提相似度到 0.7+ / 6. calc_accuracy ≥ 90% 拿 flag

## 关键 payload

```
data_dict_2[id] = {"text": "very " + ("happy/nothing/unhappy") + original_text} ; predict_model argmax ; verify_similarity cosine ≥ 0.7 ; calc_accuracy 79.0% → 95%+
```

## 经验教训

NLP 模型对抗样本常用策略：反向情绪关键词前缀 + 强度副词（very）保相似度。

## 标签

NLP 对抗样本、DistilBERT 三分类、前缀加 happy/nothing/unhappy 反向、very 加 0.7 阈值、AI 模型攻击、SSIM 验证相似度

## 参考来源

- https://www.ctfiot.com/203028.html
- 原文件：2024年羊城杯粤港澳大湾区网络安全大赛WP-AI_AK篇.full.md

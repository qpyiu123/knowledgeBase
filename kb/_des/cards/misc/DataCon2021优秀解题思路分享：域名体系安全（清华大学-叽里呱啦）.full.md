---
title: "DataCon2021优秀解题思路分享：域名体系安全（清华大学-叽里呱啦）"
category: misc
tags: ["DataCon 2021", "misc", "dns", "domain", "涉赌", "涉黄"]
signals: ["DataCon 2021 2021", "dns", "domain", "涉赌", "涉黄", "涉诈", "ca-cert", "html", "graph", "misc_unknown", "DataCon2021", "HTML", "Alternative", "Name"]
difficulty: medium
source: "https://www.ctfiot.com/75695.html"
tools: ["C", "C++"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2021优秀解题思路分享：域名体系安全（清华大学-叽里呱啦）

> 赛事：DataCon 2021 2021 | 方向：misc | 难度：medium | 工具：C、C++

## 一句话总结

DataCon2021域名体系安全：27万域名分类+并查集团伙分析+HTML相似度优化

## 攻击链

1. 27万黑白域名分类：涉赌/涉黄/涉诈
2. 黑产团伙关联分析
3. 7种关联边（强到弱）：CA Alternative Name/HTML IP邮箱/统计ID/动态跳转URL/统计链接/人工特征/HTML相似度
4. 并查集维护子图
5. HTML相似度：最长公共子序列+桶排序优化+O(100N)复杂度
6. C++实现+多进程

## 关键 payload

```
\b[CA证书Alternative Name]\b | \b[HTML相似度>90%]\b  # 7种关联边
```

## 经验教训

大规模域名分析需用并查集+LCS优化+多进程并行

## 标签

dns、domain、涉赌、涉黄、涉诈、ca-cert、html、graph、团伙分析

## 参考来源

- https://www.ctfiot.com/75695.html
- 原文件：DataCon2021优秀解题思路分享：域名体系安全（清华大学-叽里呱啦）.full.md

---
title: "可信度量赛题官方WP - TCM PCR寄存器+SM3摘要+可信报告防重放"
category: crypto
tags: ["全国大学生信息安全竞赛(信安国赛) + 伽玛实验场", "crypto", "可信计算", "TCM", "PCR寄存器", "可信度量"]
signals: ["全国大学生信息安全竞赛(信安国赛) + 伽玛实验场 2023", "可信计算", "TCM", "PCR寄存器", "可信度量", "SM3", "防重放", "nonce", "quote_report", "crypto_oracle", "NEX", "F1sh", "quote_report-", "external_data_store"]
difficulty: hard
source: "https://www.ctfiot.com/118196.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 可信度量赛题官方WP - TCM PCR寄存器+SM3摘要+可信报告防重放

> 赛事：全国大学生信息安全竞赛(信安国赛) + 伽玛实验场 2023 | 方向：crypto | 难度：hard

## 一句话总结

北工大胡俊老师设计信安国赛可信度量题,3队解出:东北大学NEX一血/F1sh二血/北工大三血。

## 攻击链

1. 检查quote_report->nonce == external_data_store(防重放) → 检查pcrValue == empty_digest(全0则无策略) → 遍历memdb获取4种策略(科研/生产/测试/公开)摘要值 → 16种组合(0-15,每位bit对应一策略) → SM3(oldPcrValue||digestValue)扩展 → 与quote_report->pcrValue对比 → 拼接成"策略1|策略2

## 关键 payload

```
SM3(PCR旧值||digestValue) + 2^4=16种组合 + calculate_context_sm3(buf,len,out)
```

## 经验教训

可信计算TCM PCR寄存器写入原理:newPcrValue = SM3(oldPcrValue||digestValue);4种策略(科研/生产/测试/公开)2^4=16种组合;防重放:比对external_data_store中的预期nonce与quote_report->nonce;NEX一血用VSCode Remote-SSH插件直接连环境;memdb哈希表存储与查询次序无关需按策略名排序存数组。

## 标签

可信计算、TCM、PCR寄存器、可信度量、SM3、防重放、nonce、quote_report、主动可信免疫、key_manage、4种策略组合、16种枚举、NEX、F1sh、北工大

## 参考来源

- https://www.ctfiot.com/118196.html
- 原文件：官方WP_-_关于“可信度量”赛题的设计与思考.full.md

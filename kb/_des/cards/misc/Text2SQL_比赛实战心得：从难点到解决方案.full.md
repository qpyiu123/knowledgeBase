---
title: "Text2SQL 比赛实战心得：从难点到解决方案"
category: misc
tags: ["Text2SQL 比赛心得 (LLM/NL2SQL)", "misc", "text2sql", "nl2sql", "llm_sql_generation", "vector_recall_field_simulation"]
signals: ["Text2SQL 比赛心得 (LLM/NL2SQL) 2025", "text2sql", "nl2sql", "llm_sql_generation", "vector_recall_field_simulation", "multi_level_recall", "agent_think_act_loop", "prompt_engineering", "few_shot_example", "ai_security", "Text2SQL", "Agent", "ReAct", "SQL"]
difficulty: medium
source: "https://www.ctfiot.com/240361.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Text2SQL 比赛实战心得：从难点到解决方案

> 赛事：Text2SQL 比赛心得 (LLM/NL2SQL) 2025 | 方向：misc | 难度：medium

## 一句话总结

Text2SQL 比赛实战心得，多级召回（DB→表→字段）+ 向量检索模拟问题 + 上下文重写 + Agent ReAct 循环 + 复读机熔断，覆盖自然语言到 SQL 的全流程难点。

## 攻击链

1. 数据库表数多 → LLM Token 贵 → 多级召回 (DB→表→字段) → LLM 给字段生成"模拟问题"做向量检索 → 表级聚合 + 两层筛选 Top N 表 Top M 字段 → 上下文压缩 (原对话 + 重写问题) → Agent Think/Write SQL/Execute/Think Again 多轮迭代 → 字段注释按需注入 → 少样本示例 → 最大迭代次数 + 复读机熔断 + 完整 SQL 执行反馈

## 关键 payload

```
多级召回 = LLM DB 选库 → LLM 选表 → LLM 选字段 / 向量检索 = LLM 模拟问题 → 向量化 → 用户问题 top-k / Think-Write SQL-Execute-Think Again ReAct 循环
```

## 经验教训

Text2SQL 的核心难点不是 SQL 本身，而是 schema 检索 + 上下文补全 + 多步推理；向量检索字段模拟问题比多级 LLM 召回更精准且省 Token。

## 标签

text2sql、nl2sql、llm_sql_generation、vector_recall_field_simulation、multi_level_recall、agent_think_act_loop、prompt_engineering、few_shot_example、error_recovery_loop、replan_loop_breaker

## 参考来源

- https://www.ctfiot.com/240361.html
- 原文件：Text2SQL_比赛实战心得：从难点到解决方案.full.md

# 知识图谱与跨方向检索

本模块借鉴了 `temp_newData/CTF知识库` 的《图谱架构与人工搜索工作台》设计，
只取其中可落地、且不会引入误判的部分。

## 为什么需要图谱

原有的 FTS + 向量检索只会找「字面/语义相近」的文档。但很多真实题目需要的是
**跨方向关联**：

- 格式化字符串的任意写 —— 与 EVM 存储槽覆盖是同一类抽象
- PHP 反序列化 —— 与 Java/Python 反序列化机制类似但构造完全不同
- `canary` —— AI 提示词防护和栈溢出检测，同名但毫无关系

这些关系检索算法本身发现不了，必须显式记录。

## 关系分级（核心约束）

设计文档里最关键的一条原则：**关系不能混用**。

| 关系 | 含义 | 是否提升排名 |
|---|---|---|
| `relates_to` | 弱关联，扩大阅读面 | ❌ 仅对照 |
| `analogous_to` | 类比，相似但不同，**不传递适用性** | ❌ 仅对照 |
| `differs_from` | 易混淆，用于区分 | ❌ 仅对照 |
| `requires` | 前置条件 | ✅ |
| `uses_tool` | 确实用到某工具 | ✅ |
| `illustrated_by` | 案例证据 | ✅ |

正文里出现某个词，最多只能算「提过」，**不能自动升级成 uses_tool 或 requires**。
所以本模块只从 front-matter 读关系，不做任何自动抽取。

## 怎么用

### 给文档加关系

在 front-matter 里写：

```yaml
---
title: 弱 RSA 共模攻击
category: crypto
relates_to: [crypto/rsa-wiener-attack.md, crypto/rsa-fermat-factorization.md]
differs_from: [crypto/rsa-broadcast-attack.md]
requires: [crypto/rsa-basics.md]
---
```

目标可以写完整路径、文件名或标题，建图时会自动解析。

### 建图与查看

```powershell
kb graph                # 查看统计
kb graph --build        # 从 front-matter 重建
kb graph --expand pwn/format-string-arbitrary-write.md
```

### 检索时的表现

```
$ kb search "RSA 共模攻击" -k 5

 1. 弱 RSA 共模攻击  [crypto] via=fts+vec
 2. ...
 6. RSA 维纳攻击  [crypto] via=graph:relates_to
 7. RSA Fermat 分解  via=graph:relates_to

── 图谱关联 ──
  [对照:relates_to] crypto/rsa-wiener-attack.md
```

**图谱补入的条目一律排在词面/向量结果之后**，且标出是通过哪条边来的。
这样不会污染主结果的可信度。

## 有界扩展

严格按设计文档的四条限制，任一触发都记录 `truncated`：

| 限制 | 默认值 |
|---|---|
| 跳数 | 1 |
| 节点总数 | 12 |
| 单节点扇出 | 4 |
| 耗时预算 | 120 ms |

旧记录称 26 条边的图上单次扩展约 1–3 ms（本批未复测，只作线索）。

## 数据格式

`index/graph.db`（SQLite）：

```sql
nodes(key, title, category, path)
edges(src, dst, kind, weight, evidence)
```

重建时会清空重来——因为关系全部来自 front-matter，是**可重建**的。
如果要加人工维护的关系（设计里说的 curation 库），需要另建一张表，
避免被重建覆盖。这一点本实现预留了位置，尚未做。

## 当前覆盖

- **1567 个节点 / 26 条边**（2026-10-28 直接查询 `index/graph.db` 验证）
- 边类型分布：`relates_to` 13、`differs_from` 7、`analogous_to` 4、`requires` 2
- “8 条跨方向”“17 篇手写文档带关系字段（7%）”为旧记录，本批未逐条复验

跨方向边举例：

```
pwn/format-string-arbitrary-write  --analogous_to-->  blockchain/evm-storage-slot
ai/agent-privilege-escalation      --relates_to-->    web/ssrf-internal-access
ai/system-prompt-leak              --differs_from-->  pwn/stack-canary-bypass
crypto/rsa-common-modulus-attack   --differs_from-->  crypto/rsa-broadcast-attack
```

## 局限

1. **覆盖率低**：只有 7% 的文档带关系。这部分需要人工判断，无法自动生成。
2. **导入的 266 篇没有关系**：它们来自外部语料，没有可信的跨方向标注。
3. **没有单题工作图**：设计文档里的「观察 → 候选 → 条件 → 尝试」状态机尚未实现，
   目前只有长期知识图谱这一层。
4. **没有条件表达式**：`requires` 目前是平铺列表，不支持 ALL/ANY 嵌套和
   `true/false/unknown` 三态判断。

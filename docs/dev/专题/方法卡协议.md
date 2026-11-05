# 方法卡生产协议 v2（Method Card Protocol v2）

> 本文件是 DB-Q4 及以后所有方法卡生产/验收的唯一标准。
> 示范样例：`kb/_methods/rsa_wiener_continued_fraction.md` + `kb/_methods/scripts/rsa_wiener_continued_fraction.py`。
> 题源清单：`work/q3/method_backlog.json`（53 主题）。

## 1. 卡片骨架（七栏 front-matter + 五段正文，缺一不收）

```yaml
---
title: 方法卡 · <中文名>
category: crypto|web|reverse|pwn|misc|forensics|blockchain|mobile|hardware|osint|ai
tags: [方法卡, ...4-8 个]
signals: [ ...4-8 条, 每条 <= 40 字 ]
difficulty: easy|medium|hard
source: kb/<真实存在的文档路径>   # 多个用逗号分隔, 至少 1 条
tools: [python, ...]
updated: YYYY-MM-DD
---
```

正文五段顺序固定：

1. **适用场景** —— 什么样的题面/附件/源码特征要用这张卡（用做题人视角的"看到了什么"）。
2. **前置条件** —— 需要哪些输入、参数/版本/环境限制、理论边界（如 Wiener 的 d < n^(1/4)/3）。
3. **步骤** —— 可跟着操作的 1-2-3 步，含关键代码/命令；数学生攻击给公式推导骨架。
4. **脚本** —— 指向 `kb/_methods/scripts/<同主题slug>.py`，给一行用法示例 + 核心参数说明。
   明确不适合自动化的题材（如纯手工交互题）允许"无脚本速查卡"，但须写清手工操作要点。
5. **失效场景** —— 明确列出"这卡在什么情况下会误判/失败"，至少 2 条。

## 2. signals 硬规则

- 每条是"做题人会搜的话"：特征词 + 场景，禁纯形容词（"很奇怪"之类）。
- 至少 2 条必须能在卡引用的 `source` 文档正文里找到对应片段（防臆造）。
- 写卡流程必须"先查证后下笔"：先读 source 文档与 backlog `sources`，禁止先写卡再找证据。

## 3. 脚本硬规则

- 单文件，**标准库优先**；如需第三方库，只允许仓库 `.venv` 已装依赖（numpy 等），并在卡里注明。
- 必须实现 `--selftest`：至少 4 组断言，覆盖 正常路径 / 边界拒绝 / 参数不足报错 / 可复现随机（固定 seed）。
- 全部 `--selftest` 必须 `exit 0`；`PYTHONIOENCODING=utf-8` 下无乱码输出。
- 只读、离线：默认参数不联网、不删文件、不写工作区外路径；禁绝对盘符路径、禁外部下载。

## 4. 命名与去重

- 卡：`kb/_methods/<id>.md`；脚本：`kb/_methods/scripts/<id>.py`（id 用下划线连字）。
- backlog 对应项若与已有 13 卡同主题（如 wiener）→ 标 `skipped`，不得重复建卡。

## 5. 生产纪律

- 只允许创建/修改：`kb/_methods/**`、`tests/test_method_scripts.py`（按其现有风格补测）、
  `work/dbq4/**`（进度账本）。
- **不做**：reindex、eval、图谱、git commit、`git add`、动 index/ 与服务。索引与验收由裁判统一执行。
- 每完成一卡立即更新 `work/dbq4/progress-<组名>.json`（增量落盘，防中途崩)。
- `tests/test_method_scripts.py` 若为自动 glob 脚本目录，则无需逐个补测点；
  若为枚举式，按现有风格逐个登记。

## 6. 验收（裁判执行）

1. 逐卡 front-matter 解析 + source 路径实存（0 死链）；
2. 逐脚本独立跑 `--selftest` 全 exit 0；
3. 全量 `pytest`（基线 279，只增不减）；
4. 统一 reindex 后 `eval_search --set all`：legacy/expanded 两集不得劣化（±0.005 内）；
5. 抽卡假阳性挑战：构造 signals 相似但实际不可用的输入，卡不得误判。

# DB-Q1 知识库只读质量审计

> 状态：**已完成（只读审计 + 人工抽样）**。本批**没有**运行检索评测，不声称任何召回/正确率提升。
> 产物：`tools/audit_corpus.py`、`tests/test_audit_corpus.py`；运行产物在 `work/db_quality1/`（被 gitignore，不入库）。

## 1. 这个工具做什么

对 `kb/` 做一次**只读**盘点，回答四个问题，并把答案落成可复核的文件：

1. **规模**：按索引同源规则，到底收了多少篇？（不是 `kb/**/*.md` 的数目）
2. **质量**：哪些篇目的元数据/代码围栏/图片依赖/可读性有问题？（每条规则给出"事实 / 疑似 / 仅线索"三级性质）
3. **重复**：哪些篇目是精确副本、近似副本、包含关系、同题不同解？（**只给候选，不删任何文件**）
4. **导入批**：`kb/_imported_cats/` 的 277 篇与 `work/import_cats/manifest.json` 是否对得上？

设计原则：
- **与索引同源**：文档集合直接调 `kb.parser.iter_md_paths`，不再自己写一套 rglob 规则（历史教训：`tools/kbcheck.py` 自造规则，跳过 `_` 开头目录，结论与索引对不上）。
- **不改输入**：工具只读 `kb/`，所有输出写 `--out-dir`。可用 `--hash-before` + `compare-hash` 自证。
- **不静默跳过**：解码失败、读取异常逐条进 `run_meta.json.errors` 并在报告里计数。
- **疑似不删**：近似重复只输出候选与判读，删除/合并属于后续批次的人工决策。

## 2. 怎么运行

```powershell
cd F:\CTFfiles\knowledgeBase
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe tools\audit_corpus.py --help
.\.venv\Scripts\python.exe tools\audit_corpus.py --out-dir work\db_quality1
```

只读自证（推荐每次都跑）：

```powershell
# 跑前快照 kb/ 全文件哈希
.\.venv\Scripts\python.exe tools\audit_corpus.py --out-dir work\db_quality1 --hash-before
# ...跑完后核对（退出码 0=未变，2=有变化）
.\.venv\Scripts\python.exe tools\audit_corpus.py --out-dir work\db_quality1 compare-hash --before work\db_quality1\hash_before.json
```

注意：`--project-root` / `--kb-dir` / `--out-dir` 是**主命令参数**，用 `compare-hash` 子命令时要写在子命令**之前**。

主要参数：

| 参数 | 默认 | 含义 |
|---|---|---|
| `--out-dir` | `work/db_quality1` | 产物目录（不在 `kb/` 内） |
| `--min-jaccard` | `0.7` | 近似重复的 jaccard 阈值；调低到 0.6 会让同模板不同解法的文档涌入候选 |
| `--min-containment` | `0.75` | 包含度阈值（短边 ≥50 shingle 时才采信） |
| `--max-pairs` | `200000` | 候选上限，仅作内存保险；触发时 `stats.capped=true` 并在报告里显式告警 |
| `--sample-size` / `--seed` | `24` / `20261101` | 分层抽样规模与种子（固定即完全可复现） |

## 3. 产物

| 文件 | 内容 |
|---|---|
| `inventory.jsonl` | 每篇一行：哈希、字节数、正文长度、围栏统计、front-matter 诊断、图片依赖、来源分组键 |
| `duplicate_candidates.json` | 精确副本组、近似候选对（含 jaccard/containment/判读/共有片段）、候选簇、同 URL 线索组、`stats` |
| `import_check.json` | 导入批 277 篇与 manifest 的逐条对照 |
| `sample_plan.json` | 确定性分层抽样计划（pool/algorithm/seed/strata/paths） |
| `eval_protocol.json` | 下一批（Q3/Q4）冻结评测的协议草案，**未实施** |
| `run_meta.json` | 版本、参数、耗时、错误清单、规则目录（每条规则的方法与误报边界） |
| `report.md` | 人类可读报告（规模、规则命中、重复候选、导入批、抽样、误报边界） |
| `hash_before.json` / `hash_after.json` | `kb/` 全文件 SHA-256 快照，用于自证未改写 |

## 4. 实测规模（2026-11-01，项目 `F:\CTFfiles\knowledgeBase`）

| 指标 | 值 |
|---|---|
| 收录篇数（与索引同源） | **1844**（`kb/**/*.md` 共 1845，差 1 = `kb/_index.md` 被 `_` 前缀规则排除） |
| 审计耗时 | 20.1 s（盘点 3.7 s / 去重 10.4 s），墙钟 22.4 s |
| 解析/读取异常 | 21（全部是 front-matter YAML 语法错误，无解码失败） |
| 有合法围栏代码块 | 1299 |
| 精确正文副本 | **0** 组 |
| 近似候选对 / 簇 | **230** 对 / 30 簇（分数 0.7500–0.9997） |
| 同 URL 线索组 | 3 |

方向分布：web 493、misc 405、pwn 303、reverse 263、crypto 260、forensics 62、hardware 14、mobile 14、ai 12、osint 12、blockchain 6。
顶层分布：`_des` 1060、`_imported_cats` 277、`_imported` 266，其余为正式方向目录。

## 5. 疑似问题分布（事实 vs 疑似）

| 规则 | 命中 | 性质 |
|---|---|---|
| front-matter YAML 解析失败 | 21 | 事实（语法错误，`signals` 未加引号） |
| 缺少 front-matter | 0 | 事实 |
| 缺少 `source` 字段 | 21 | 事实 |
| 缺少 `license` 字段 | 1322 | 事实（缺字段 ≠ 侵权） |
| `verification` 状态 unknown | 1567 | 事实（unknown ≠ 未复现） |
| 代码围栏未闭合 | 0 | 事实 |
| 本地图片缺失 | 8 | 事实（47 个引用，**全部**不存在） |
| 远端图片未验证 | 19 | 仅线索（本批不联网） |
| 正文疑似依图但图不可用 | 16 | 疑似（需人工） |
| 无合法围栏代码块 | 545 | 事实（`_imported_cats` 275 / `_imported` 264 / `_des` 6） |
| 不可读 / 类别越界 | 0 | 事实 |

三个**结构性**结论（都有数据支撑，不是猜测）：

1. **front-matter 缺陷是旧批遗留**：21 篇全部在 `_imported/`，全部报"第 5 行"（front-matter 第 4 行），原文形如 `signals: [[Misc] 清北问答, Git]`、`signals: [RSA? cmd5!]`。可复核后果：这 21 篇的 `source` **全部为空**，同批其余 245 篇无一为空。
2. **导入批是无代码的散文正文**：`_imported_cats` 277 篇中仅 **2 篇**有合法围栏，正文第 3 行固定声明"阶段 1，仅散文，代码段未导入"。检索命中该批不能指望给出可运行 exp。
3. **缺图风险集中在 `_des`**：8 篇缺图全在 `_des/`；190 篇正文 <700 字的**全部**在 `_des/`；抽样的 `_imported_cats` 24 篇 0 篇缺图、0 篇 YAML 错误。

## 6. 人工抽样结论

样本：`_imported_cats/` 池，按 `(category, source_host)` 分 18 层，种子 20261101，24 篇，逐篇读完，证据（正文行号 + 短引文）见 `work/db_quality1/sample_review.md`。

| 结论 | 篇数 |
|---|---|
| 内容可用、无需改动 | 6 |
| 参考/摘要类（非解题记录） | 3 |
| 空壳导读（明示"不包含完整解题步骤"） | 7 |
| 标题与正文题目不一致（题名错配） | 10 |
| 类别与来源导读所指方向矛盾 | 3 |
| 一文件合并多方向内容 | 2 |
| 正文混入博客页眉/导航噪声 | 2（同一来源站点） |
| Markdown 表格被折断 | 1 |
| 重复行 | 4 |
| `origin_license: not_declared` 却已收录正文 | 2 |

读法：**题名错配**（10 篇）会让按标题检索指向错误题目，是**疑似误检来源**；**空壳导读**不是"低质量"，它是"指向源站"的另一种资料类型，是否保留属产品决策；**标题不一致 ≠ 重复**，两者处置方式不同。

## 7. 规则误报边界（本批实际踩过并修掉的）

- **围栏识别必须剥引用前缀**：`> ``` ` 形式的引用块围栏若不剥 `> ` 会被判成"整篇无围栏 + 围栏外散落 ```"。现已支持最多 3 层 `> `，并把 4 空格缩进行的 ``` 视为缩进代码块、不计数。
- **行内代码不是围栏**：只有奇数个 ``` 才算散落标记；整行 `~~~` 才算波浪线围栏（字符画里的 `~~~` 不算）。
- **front-matter 必须区分四类**：缺失 / 未闭合 / YAML 语法错误 / 不是键值映射。早期实现把语法错误一律当"缺失"，导致 21 篇有完整元数据的文档被误报为无元数据。
- **去重候选不能按分数截断**：早期用"共享 shingle 数排名取前 4000 对"会漏掉分数最高但 shingle 池较小的对（实测漏掉 `_des/wp_summary/web/ctfshow-php特性.md` ↔ `ctfshow-命令执行wp.md`，0.9997）。现改为**逐对可证明下界过滤**（jaccard≥t ⇒ shared ≥ t/(1+t)·max(|A|,|B|)；containment≥c ⇒ shared ≥ c·min(|A|,|B|)，取较小者为可行下界），阈值以上的对**全部**评分，不再依赖截断。
- **包含度对短文档不可信**：短边 <50 shingle 时不采信包含度、只认 jaccard，并给该对打 `tiny_doc_containment_ignored`。实测 1844 篇的最小 shingle 集为 144，该保护不会排除任何真实文档，只防合成小样本假阳性。
- **同模板 ≠ 重复**：共用赛事模板（"题目描述/附件信息/环境/评分"）但解法不同的两篇，jaccard 可到 0.667；默认阈值取 0.7 而非 0.6 就是这个原因。
- **正文哈希不一致 ≠ 被篡改**：导入批 `body_sha256` 记的是**段落正文**，落盘文件含 front-matter 与来源分段标题，故 277 篇"必然不一致"。本批无法据此判断事后编辑。

## 8. 未做的事（明确记录）

- 未修改任何 `kb/` 正文、未改 `index/`、未启停服务、未下载任何图片、未联网核验源站。
- 未做语义/向量去重，只做字符 shingle。
- 未给任何文档打"低质量"标签，未删除任何文件。
- 未运行检索评测。`eval_protocol.json` 只是协议草案。

## 9. 后续批次（只计划，本批不实施）

- **Q2 — 人工确认重复与质量标签**：对 25 对 `_imported` ↔ `_imported_cats` 同题双份逐对裁决（保留哪份、是否合并）；修 21 篇 `signals` 的 YAML 引号；补 47 个缺失本地图片或改用"图不可用"标记；给"题名错配/空壳导读/方向矛盾"打结构化标签（探索 `relates_to`/`differs_from` 已有的 9/6 条先例）。**所有改动正文的动作都必须在 Q2 单独授权。**
- **Q3 — 冻结检索评测后试验分块排序**：先建冻结查询集（协议见 `eval_protocol.json`：固定查询来源、固定相关性标注规则、固定 k 与指标、标注者间一致性检查），在**不改语料**的前提下比较切块/排序策略，用同一查询集前后对照。**指标提升必须由冻结集给出，不预告数值。**
- **Q4 — SQLite 一致性备份验证**：`index/` 内 `fts.db` / `graph.db` / `vectors.db` 的备份必须走 SQLite 在线备份 API 或 `VACUUM INTO`，并验证备份可打开、行数与主库一致、FTS/GEXF 索引完整；不允许直接 `copy` 正在被写入的库文件。

# Des-CTF-Knowledge 整合报告

**日期**：2026-10-24
**来源**：`temp_newData/Des-CTF-Knowledge-main/`（1279 文件，38 MB）
**导入脚本**：`work/des_import.py`
**质量审查**：`work/audit_des.py` / `audit_des2.py` / `audit_des3.py`

---

## 一、先审查，后导入

### 分区质量差异

| 分区 | 篇数 | 体积 | 代码块 | 格式 | 处置 |
|---|---|---|---|---|---|
| 顶层主题文档 | 16 | 681 KB | 1072 | ✅ 94% | **全量导入** |
| WP汇总 | 14 | 304 KB | 601 | ✅ 93% | **全量导入** |
| 工具使用 | 6 | 58 KB | 72 | ✅ 100% | **全量导入** |
| 比赛 WP (articles) | 1027 | 25.6 MB | 1038 | ⚠️ 降质 | **只抽思路卡** |

**核心判据**：681 KB 的主题文档有 1072 个代码块，而 25.6 MB 的 WP 只有 1038 个
——代码密度差 37 倍。WP 的价值在元数据，不在正文。

### 审查发现

| 检查项 | 结果 |
|---|---|
| 语料内部重复 | 0（1027 篇全唯一） |
| 与现有 KB 重叠 | 0（标题、正文均不重） |
| 图片被删 | **100%**（`images_removed: true`） |
| 正文引用已删的图 | 848 篇（83%） |
| 命令粘连 | 仅 1 篇 |
| 占位符 xxx/XXXX/TODO | **全是误报**（反编译 `loc_xxxxxx`、PoW `sha256(XXXX+`） |

结论：**articles 正文不可用（图没了），但 `one_liner` / `lesson` /
`attack_chain` / `tags` 是高质量思路数据，且完全不受图片丢失影响。**

---

## 二、导入结果

### 数量

| 类型 | 目录 | 篇数 |
|---|---|---|
| 主题文档 | `kb/_des/topics/` | 13 |
| WP汇总 | `kb/_des/wp_summary/` | 14 |
| 工具使用 | `kb/_des/tools/` | 6 |
| 比赛 WP 思路卡 | `kb/_des/cards/` | 1027 |
| **合计** | | **1060 篇，3.28 MB** |

### 索引变化

| 指标 | 导入前 | 导入后 |
|---|---|---|
| 文档 | 507 | **1567** |
| 分块 | 4,898 | **14,139** |
| 图谱节点 | 507 | **1567** |
| 索引耗时 | — | 394 秒 |

方向分布：web 447 / misc 321 / pwn 265 / reverse 215 / crypto 199 /
forensics 62 / 其他 58

---

## 三、思路卡的构造方式

每条比赛 WP 压成一张卡，保留可复用的部分，丢掉降质正文：

```markdown
# SUCTF 2025 Writeup - XMCVE-Polaris

> 赛事：SUCTF 2025 | 方向：web | 难度：medium | 工具：Python

## 一句话总结
PHP 反序列化新链 + Solidity 签名复用 + 内置服务器源码泄露。

## 攻击链
1. SU_OSS: ls 找 oss 旧版本文件
2. SU_POP: 入口 /ser?ser=base64 → RejectedPromise __destruct
...

## 经验教训
CakePHP 链子 fix 时只改头/尾，中间常被保留；找链应优先按中间环节搜索。
```

`signals` 由 tags + vuln_type + one_liner 技术词 + attack_chain 关键词拼成，
保证检索能命中。

---

## 四、修复的一个 Bug

初版导入时用 `re.M` 匹配 `^#\s+` 取标题，结果把代码块里的
PHP 注释 `# -*- coding: utf-8 -*-` 当成了标题，导致 10 篇文档标题被污染，
检索结果首条显示成代码注释。

修复：新增 `first_heading()`，逐行扫描并跳过围栏代码块。

| 查询 | 修复前 | 修复后 |
|---|---|---|
| ctfshow 命令执行绕过 | `-*- coding: utf-8 -*-` | `ctfshow-命令执行wp` |
| 文件上传 绕过 | `其中的download.jpg...` | `ctfshow-文件上传wp` |
| 图片 LSB 隐写 | 碎片 | `图片隐写` |

---

## 五、检索验证

| 查询 | 首条结果 | 判定 |
|---|---|---|
| SSTI 模板注入 常用 payload | SSTI 模板注入（Jinja2 / Twig / Freemarker） | ✅ |
| SQL 联合注入 报错注入 | SQL | ✅ |
| JWT 弱密钥 伪造 | JWT 伪造（none 算法 / 密钥爆破） | ✅ 第2条 |
| ssrf gopher 协议 打内网 | SSRF 服务端请求伪造（内网穿透 / gopher 打 Redis） | ✅ |
| Solidity calldata tuple head overflow | 0CTF/TCTF 2022 NFT Market | ✅ |
| 内存取证 volatility | 基于volatility2构建新版本内核profile指南 | ✅ |
| Python 沙箱逃逸 pyjail | Python 沙箱逃逸（pyjail） | ✅ 旧条目仍命中 |
| RSA 共模攻击 | 弱 RSA 共模攻击 | ✅ 旧条目仍命中 |

新内容能命中，旧条目没被挤掉。

**未命中一例**：`CakePHP 反序列化 链子` 没命中那张 SUCTF 卡
（卡标题是多题合并的赛事名，CakePHP 只在 tags/攻击链里）。
多题合并的 WP 天然不好按单题检索，属于可接受的局限。

---

## 六、已知局限

1. **1027 张卡里，一卡可能覆盖多题**（如一场比赛一篇 WP），按单题检索会漏
2. **原文图片 100% 丢失**，卡片里不保留正文，因此不受影响；
   但主题文档里如果原本有图，仍是缺的
3. **未导入 `CTF常用脚本及工具/`**（148 个脚本/二进制），
   那些是可执行代码而非知识，按需再议
4. 主题文档的准确性未做逐条技术复核（抽样看 SQL/SSTI 的 payload 是标准写法）

---

## 七、如何回退

```powershell
# 删除导入内容，重建索引
Remove-Item -Recurse -Force F:\CTFfiles\knowledgeBase\kb\_des
cd F:\CTFfiles\knowledgeBase
.\.venv\Scripts\python.exe tools\cli.py index
.\.venv\Scripts\python.exe tools\cli.py graph --build
```

因为隔离在 `kb/_des/`，不影响手写条目和 `_imported/`。

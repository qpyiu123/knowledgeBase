---
title: "Python pickle.loads：加载过程不是普通解析（reference）"
category: misc
tags: ["Python", "pickle", "loads", "反序列化", "不可信输入", "对象", "origin_tag:imported_cats"]
signals: ["Python", "pickle", "loads"]
difficulty: medium
source: "https://docs.python.org/3.12/library/pickle.html"
tools: []
origin: imported_cats
origin_id: "fn-python-pickle"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "489da3ea4e17db6c4d26b9fca041b314b83cbd34cf4fb5ff8345ecd24b801a43"
origin_body_sha256: 999f044da2a83eb8143056e50527aa49a80bb45fcd0c2f51819c5d95973ec097
origin_title: "Python pickle.loads：加载过程不是普通解析（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6206]
  content_sha256: "489da3ea4e17db6c4d26b9fca041b314b83cbd34cf4fb5ff8345ecd24b801a43"
  domain: "languages"
  id: "fn-python-pickle"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-python-pickle.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://docs.python.org/3.12/library/pickle.html"
  tags: ["Python", "pickle", "loads", "反序列化", "不可信输入", "对象"]
  title: "Python pickle.loads：加载过程不是普通解析"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# Python pickle.loads：加载过程不是普通解析（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://docs.python.org/3.12/library/pickle.html
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：489da3ea4e17db6c4d26b9fca041b314b83cbd34cf4fb5ff8345ecd24b801a43
> - 导入 ID：fn-python-pickle
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-python-pickle.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://docs.python.org/3.12/library/pickle.html

## 正文

pickle 用于 Python 对象序列化，恢复数据可能执行对象相关代码。官方明确警告不要加载不可信或被篡改的数据。此库不运行用户片段，也不用 pickle 保存索引；资料结构使用 JSON 与 SQLite。片段识别时区分 pickle、JSON 及只处理字面量的解析器。

---
title: "Python hashlib：摘要对象与文本表示（reference）"
category: misc
tags: ["Python", "hashlib", "sha256", "md5", "update", "digest", "hexdigest", "哈希", "摘要", "origin_tag:imported_cats"]
signals: ["Python", "hashlib", "sha256"]
difficulty: medium
source: "https://docs.python.org/3.12/library/hashlib.html"
tools: []
origin: imported_cats
origin_id: "fn-python-hashlib"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "7d366bced08626573b3a2445c2d6301a7d6d8476692f7981ace52d2ae34d0981"
origin_body_sha256: ceb68d8e7bb188dae106ab55d2b0e4a5b131674f04ac46b3ae170ffcd88c970f
origin_title: "Python hashlib：摘要对象与文本表示（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6205]
  content_sha256: "7d366bced08626573b3a2445c2d6301a7d6d8476692f7981ace52d2ae34d0981"
  domain: "languages"
  id: "fn-python-hashlib"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-python-hashlib.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://docs.python.org/3.12/library/hashlib.html"
  tags: ["Python", "hashlib", "sha256", "md5", "update", "digest", "hexdigest", "哈希", "摘要"]
  title: "Python hashlib：摘要对象与文本表示"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# Python hashlib：摘要对象与文本表示（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://docs.python.org/3.12/library/hashlib.html
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：7d366bced08626573b3a2445c2d6301a7d6d8476692f7981ace52d2ae34d0981
> - 导入 ID：fn-python-hashlib
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-python-hashlib.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://docs.python.org/3.12/library/hashlib.html

## 正文

hashlib 以统一接口提供多种摘要算法，update 接收字节数据；digest 返回摘要字节，hexdigest 返回十六进制文本表示。阅读片段要区分输入编码、摘要计算和输出表示。哈希不是可逆加密，固定长度十六进制文本也不能唯一确定是哪种算法。

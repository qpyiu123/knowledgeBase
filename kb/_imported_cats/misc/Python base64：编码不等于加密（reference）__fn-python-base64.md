---
title: "Python base64：编码不等于加密（reference）"
category: misc
tags: ["Python", "base64", "b64decode", "validate", "urlsafe", "编码", "字节", "origin_tag:imported_cats"]
signals: ["Python", "base64", "b64decode"]
difficulty: medium
source: "https://docs.python.org/3.12/library/base64.html"
tools: []
origin: imported_cats
origin_id: "fn-python-base64"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "7b442a71683c048dcd68d0471d63caa58b50b98a002934ea9ba113d81fcf4b7c"
origin_body_sha256: b07b254559070efd211cf5031509824a788398f8e546217fb3fbb321bcf2283f
origin_title: "Python base64：编码不等于加密（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6204]
  content_sha256: "7b442a71683c048dcd68d0471d63caa58b50b98a002934ea9ba113d81fcf4b7c"
  domain: "languages"
  id: "fn-python-base64"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-python-base64.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://docs.python.org/3.12/library/base64.html"
  tags: ["Python", "base64", "b64decode", "validate", "urlsafe", "编码", "字节"]
  title: "Python base64：编码不等于加密"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# Python base64：编码不等于加密（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://docs.python.org/3.12/library/base64.html
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：7b442a71683c048dcd68d0471d63caa58b50b98a002934ea9ba113d81fcf4b7c
> - 导入 ID：fn-python-base64
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-python-base64.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://docs.python.org/3.12/library/base64.html

## 正文

base64 模块在二进制与可打印 ASCII 表示之间转换，不提供保密性。Python 3.12 的 b64decode 返回 bytes；validate 参数影响是否严格拒绝非字母表字符，URL 安全变体的字母表也不同。判断短片段时同时检查输入类型、字母表、填充和后续处理，不因一行解码就认定完整算法。

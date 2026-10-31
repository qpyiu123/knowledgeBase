---
title: "PHP strcmp：结果是符号，不是布尔值（reference）"
category: misc
tags: ["PHP", "strcmp", "字符串", "比较", "大小写", "返回零", "8.2", "origin_tag:imported_cats"]
signals: ["PHP", "strcmp", "字符串"]
difficulty: medium
source: "https://www.php.net/manual/en/function.strcmp.php"
tools: []
origin: imported_cats
origin_id: "fn-php-strcmp"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "24610c4dfe9b9188b93075fd01ac43a5444da4b91fc5ad0213c38b1dc859de81"
origin_body_sha256: d9bd133f7c26f50e2307c1e9f5190e4398e400182f0c6482b2051b18088f22df
origin_title: "PHP strcmp：结果是符号，不是布尔值（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6200]
  content_sha256: "24610c4dfe9b9188b93075fd01ac43a5444da4b91fc5ad0213c38b1dc859de81"
  domain: "languages"
  id: "fn-php-strcmp"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-php-strcmp.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://www.php.net/manual/en/function.strcmp.php"
  tags: ["PHP", "strcmp", "字符串", "比较", "大小写", "返回零", "8.2"]
  title: "PHP strcmp：结果是符号，不是布尔值"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# PHP strcmp：结果是符号，不是布尔值（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://www.php.net/manual/en/function.strcmp.php
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：24610c4dfe9b9188b93075fd01ac43a5444da4b91fc5ad0213c38b1dc859de81
> - 导入 ID：fn-php-strcmp
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-php-strcmp.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://www.php.net/manual/en/function.strcmp.php

## 正文

strcmp 是二进制安全、区分大小写的字符串比较。相等返回 0，大小关系用返回值的正负表示，不能依赖绝对数值；PHP 8.2 调整了不同长度字符串返回值的保证。阅读题目时核对调用者如何比较返回值、传入类型和实际 PHP 版本；不能从函数名直接认定存在绕过。

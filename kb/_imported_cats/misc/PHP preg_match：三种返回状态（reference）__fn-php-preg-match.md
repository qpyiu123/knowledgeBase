---
title: "PHP preg_match：三种返回状态（reference）"
category: misc
tags: ["PHP", "preg_match", "正则", "返回值", "锚点", "PCRE", "0", "false", "origin_tag:imported_cats"]
signals: ["PHP", "preg_match", "正则"]
difficulty: medium
source: "https://www.php.net/manual/en/function.preg-match.php"
tools: []
origin: imported_cats
origin_id: "fn-php-preg-match"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "e5f34bbbccb600b207645f702716e990b60c512494c7893f8fccc3740842b19b"
origin_body_sha256: 0186b68de7030e86310313da5d87033cce7d33cbd0c82f931ed1fd133c9bb66c
origin_title: "PHP preg_match：三种返回状态（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6203]
  content_sha256: "e5f34bbbccb600b207645f702716e990b60c512494c7893f8fccc3740842b19b"
  domain: "languages"
  id: "fn-php-preg-match"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-php-preg-match.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://www.php.net/manual/en/function.preg-match.php"
  tags: ["PHP", "preg_match", "正则", "返回值", "锚点", "PCRE", "0", "false"]
  title: "PHP preg_match：三种返回状态"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# PHP preg_match：三种返回状态（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://www.php.net/manual/en/function.preg-match.php
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：e5f34bbbccb600b207645f702716e990b60c512494c7893f8fccc3740842b19b
> - 导入 ID：fn-php-preg-match
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-php-preg-match.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://www.php.net/manual/en/function.preg-match.php

## 正文

preg_match 找到匹配时返回 1，未找到返回 0，错误时返回 false。应分别处理未匹配与执行错误，并核对正则是否要求整串匹配；仅出现一次匹配不代表整个输入满足条件。具体模式、修饰符和版本仍需结合参考核对。

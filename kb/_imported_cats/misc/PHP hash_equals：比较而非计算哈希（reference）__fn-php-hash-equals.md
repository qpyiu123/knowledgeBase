---
title: "PHP hash_equals：比较而非计算哈希（reference）"
category: misc
tags: ["PHP", "hash_equals", "哈希", "恒定时间", "字符串", "参数", "签名", "origin_tag:imported_cats"]
signals: ["PHP", "hash_equals", "哈希"]
difficulty: medium
source: "https://www.php.net/manual/en/function.hash-equals.php"
tools: []
origin: imported_cats
origin_id: "fn-php-hash-equals"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "7183f3a8ead84f5bd43f2bb9df68f36a6391cbdb5f3048ce5e63f92d4e632100"
origin_body_sha256: 546d05c48f697eebe7f1c47fff785fce5f3ba06fd413f151619f959ef72f805e
origin_title: "PHP hash_equals：比较而非计算哈希（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6201]
  content_sha256: "7183f3a8ead84f5bd43f2bb9df68f36a6391cbdb5f3048ce5e63f92d4e632100"
  domain: "languages"
  id: "fn-php-hash-equals"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-php-hash-equals.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://www.php.net/manual/en/function.hash-equals.php"
  tags: ["PHP", "hash_equals", "哈希", "恒定时间", "字符串", "参数", "签名"]
  title: "PHP hash_equals：比较而非计算哈希"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# PHP hash_equals：比较而非计算哈希（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://www.php.net/manual/en/function.hash-equals.php
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：7183f3a8ead84f5bd43f2bb9df68f36a6391cbdb5f3048ce5e63f92d4e632100
> - 导入 ID：fn-php-hash-equals
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-php-hash-equals.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://www.php.net/manual/en/function.hash-equals.php

## 正文

hash_equals 比较两个字符串是否相等，旨在减少比较过程泄露的时间信息；它本身不生成摘要。官方要求已知秘密串在前、用户提供串在后。分析场景时分清摘要计算、输入规范化和最终比较三个环节。这里只说明函数用途，不据此证明整体认证逻辑安全。

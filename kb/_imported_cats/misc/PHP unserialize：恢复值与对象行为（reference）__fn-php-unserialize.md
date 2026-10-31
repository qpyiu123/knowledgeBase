---
title: "PHP unserialize：恢复值与对象行为（reference）"
category: misc
tags: ["PHP", "unserialize", "反序列化", "对象", "魔术方法", "allowed_classes", "origin_tag:imported_cats"]
signals: ["PHP", "unserialize", "反序列化"]
difficulty: medium
source: "https://www.php.net/manual/en/function.unserialize.php"
tools: []
origin: imported_cats
origin_id: "fn-php-unserialize"
origin_domain: "languages"
origin_family: "official_function_reference"
origin_event: ""
origin_year: ""
origin_license: "reference_only_no_redistribution_license_asserted"
origin_attribution: ""
origin_verification: "documentation_based_not_runtime_tested"
origin_content_sha256: "db992bb18885ba5250047bdaa92c847e02320d1aef267cd6376ff471c11e8c81"
origin_body_sha256: c6cd97af1f38d3f21f444fd2fb2d95e12a269b1e55adaed9891b94fa26591cd2
origin_title: "PHP unserialize：恢复值与对象行为（reference）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6202]
  content_sha256: "db992bb18885ba5250047bdaa92c847e02320d1aef267cd6376ff471c11e8c81"
  domain: "languages"
  id: "fn-php-unserialize"
  kind: "function_reference"
  language: "zh"
  license: "reference_only_no_redistribution_license_asserted"
  local_path: "61_中文赛事资料/函数参考/fn-php-unserialize.md"
  scope_note: "依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。"
  source_family: "official_function_reference"
  source_revision: "reference_page_checked_2026-10-23"
  source_url: "https://www.php.net/manual/en/function.unserialize.php"
  tags: ["PHP", "unserialize", "反序列化", "对象", "魔术方法", "allowed_classes"]
  title: "PHP unserialize：恢复值与对象行为"
  translation_kind: "short_original_chinese_summary_not_full_copy"
  verification_status: "documentation_based_not_runtime_tested"
  year: ""
updated: 2026-10-31
---
# PHP unserialize：恢复值与对象行为（reference）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://www.php.net/manual/en/function.unserialize.php
> - 许可：reference_only_no_redistribution_license_asserted
> - 署名：（未提供）
> - 文档族：official_function_reference
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：documentation_based_not_runtime_tested
> - 正文 sha256：db992bb18885ba5250047bdaa92c847e02320d1aef267cd6376ff471c11e8c81
> - 导入 ID：fn-php-unserialize
> - 原 domain：languages
> - 本地快照：61_中文赛事资料/函数参考/fn-php-unserialize.md
> - 源修订：reference_page_checked_2026-10-23
> - 收录说明：依据链接官方参考写成的简短中文摘要，未转载完整网页。Python 条目限定 3.12 文档；PHP 说明仍需结合具体版本。无解题代码或自动执行。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://www.php.net/manual/en/function.unserialize.php

## 正文

unserialize 将序列化表示恢复为 PHP 值，涉及对象时还需考虑类与恢复过程的行为。官方警告不要把不可信输入交给它，即使指定 allowed_classes 也不能视作完整安全措施。题目检索应关联类定义、运行版本和数据流，而不是假定所有序列化字符串都有同一条调用链。

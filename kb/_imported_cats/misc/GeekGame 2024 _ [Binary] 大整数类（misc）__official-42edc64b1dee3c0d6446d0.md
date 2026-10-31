---
title: "GeekGame 2024 / [Binary] 大整数类（misc）"
category: misc
tags: ["GeekGame 2024", "[Binary] 大整数类", "cases", "官方资料", "official_writeup/binary-bigint/README.md", "origin_tag:imported_cats"]
signals: ["GeekGame 2024", "[Binary] 大整数类", "cases"]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md"
tools: []
origin: imported_cats
origin_id: "official-42edc64b1dee3c0d6446d0"
origin_domain: "cases"
origin_family: "official_event_archive"
origin_event: "GeekGame 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "7e215f35c58e4b2b767a6d5d50945d3ea2b1f42d54c50083765aa778b3ac122e"
origin_body_sha256: 622ec64bdd2d98b2713d16578f77d3fa2ad226536bc338e929053beadb59611c
origin_title: "GeekGame 2024 / [Binary] 大整数类（misc）"
origin_meta:
  asset_refs: [{"downloaded_bytes": 93172, "kind": "attachment", "local_path": "62_官方赛事题库/objects/c825485c2d601e8cd5801de941de1c02e1ae4150450c8336e94156f3e5abacd1.blob", "owner_id": "official-42edc64b1dee3c0d6446d0", "policy": "reference_only_no_execution", "relative_path": "official_writeup/binary-bigint/attachment/binary-bigint.zip", "sha256": "c825485c2d601e8cd5801de941de1c02e1ae4150450c8336e94156f3e5abacd1", "source_url": "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/attachment/binary-bigint.zip"}, {"downloaded_bytes": 146044, "kind": "attachment", "local_path": "62_官方赛事题库/objects/6a94718ff080b11b99530fbea5645247ff6a8a23fca6ddec8621d8ea218e859a.blob", "owner_id": "official-42edc64b1dee3c0d6446d0", "policy": "reference_only_no_execution", "relative_path": "official_writeup/binary-bigint/attachment/binary-bigint-new.zip", "sha256": "6a94718ff080b11b99530fbea5645247ff6a8a23fca6ddec8621d8ea218e859a", "source_url": "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/attachment/binary-bigint-new.zip"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "geekgame2024:official_writeup/binary-bigint"
  chunk_ids: [7320]
  content_sha256: "7e215f35c58e4b2b767a6d5d50945d3ea2b1f42d54c50083765aa778b3ac122e"
  domain: "cases"
  domain_basis: "unclassified_not_inferred_from_code"
  event: "GeekGame 2024"
  external_links_not_followed: 0
  id: "official-42edc64b1dee3c0d6446d0"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/a1c191bde058dd38a4c17ec9a22aa859d043a8382aa6aae8bb76eed81c2ded78.blob"
  official_evidence: "https://github.com/PKU-GeekGame/geekgame-4th"
  original_path: "official_writeup/binary-bigint/README.md"
  revision: "a21d7f7387512ec7ef77720e998d60efa16f2353"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md"
  tags: ["GeekGame 2024", "[Binary] 大整数类", "cases", "官方资料", "official_writeup/binary-bigint/README.md"]
  title: "GeekGame 2024 / [Binary] 大整数类"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# GeekGame 2024 / [Binary] 大整数类（misc）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：GeekGame 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：7e215f35c58e4b2b767a6d5d50945d3ea2b1f42d54c50083765aa778b3ac122e
> - 导入 ID：official-42edc64b1dee3c0d6446d0
> - 原 domain：cases
> - 本地快照：62_官方赛事题库/objects/a1c191bde058dd38a4c17ec9a22aa859d043a8382aa6aae8bb76eed81c2ded78.blob
> - 源修订：a21d7f7387512ec7ef77720e998d60efa16f2353
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-42edc64b1dee3c0d6446d0", "relative_path": "official_writeup/binary-bigint/attachment/binary-bigint.zip", "local_path": "62_官方赛事题库/objects/c825485c2d601e8cd5801de941de1c02e1ae4150450c8336e94156f3e5abacd1.blob", "downloaded_bytes": 93172, "source_url": "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/attachment/binary-bigint.zip", "sha256": "c825485c2d601e8cd5801de941de1c02e1ae4150450c8336e94156f3e5abacd1", "kind": "attachment", "policy": "reference_only_no_execution"}, {"owner_id": "official-42edc64b1dee3c0d6446d0", "relative_path": "official_writeup/binary-bigint/attachment/binary-bigint-new.zip", "local_path": "62_官方赛事题库/objects/6a94718ff080b11b99530fbea5645247ff6a8a23fca6ddec8621d8ea218e859a.blob", "downloaded_bytes": 146044, "source_url": "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/attachment/binary-bigint-new.zip", "sha256": "6a94718ff080b11b99530fbea5645247ff6a8a23fca6ddec8621d8ea218e859a", "kind": "attachment", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md

## [Binary] 大整数类

- 命题人：debugger
- Flag 1：350 分
- Flag 2：300 分

## 题目描述

**[【附件：下载题目附件（binary-bigint.zip）】](attachment/binary-bigint.zip)**

**[【附件：下载带符号的题目附件（binary-bigint-new.zip）】](attachment/binary-bigint-new.zip)**

## 预期解法

此题是一个用Pascal写的大整数模板，实际上是用从网上随便找的一个版本简单改写得到的。

预期需要选手完成以下步骤：
* 找到主函数（通过搜索字符串即可知道主函数）。
* 知道字符串的存储格式（第一个字节表示长度）。
* 因为没有符号，选手需要区分哪个函数是内置的库函数，哪个是真正用来处理字符串的函数。
* 知道了处理字符串的函数之后，分析出哪个是大整数比较、加法、减法、乘法的函数，以及字符串转大整数的过程。注意没有用于判断相等的函数，而是用x<=y且y<=x来判断x和y是否相等。
* 还原出程序的大整数操作。

Flag 1会把输入的flag拆成3个部分，然后每个部分转成整数都调用一个函数，三个调用都返回true则返回Flag正确。而checkflag1函数会计算一个大整数的三次函数，三次方程有三个根，选手需要把系数提取出来，然后有众多工具（SageMath、sympy、Mathematica均可）可以得到方程的根。

Flag 2会把flag转成整数后自乘16次再和flag相乘，每步操作后都和一个常数m取余，最后把结果和另一个常数v比较。这里实现了一个RSA。使用<a target="_blank" rel="noopener noreferrer" href="https://github.com/RsaCtfTool/RsaCtfTool">RsaCtfTool</a>可以把m分解。此后还原回flag是显然的。

本题旧版本还有一个Flag 3（后来因为flag太多而且程序也无法给出反馈删了），输入flag后会计算flag^2+m，然后直接退出。实际上m可以分解成两个素数k+flag和k-flag的积，如果你输入的flag是正确的计算出来的结果会是平方数，但是这个模板没有开平方根的功能。这也是Fermat分解方法的原理：当两个素数大小接近时，你可以先找到比m大的最小平方数，然后减去m，如果得到的是平方数，那么m是两个平方数的差，因此可以分解。

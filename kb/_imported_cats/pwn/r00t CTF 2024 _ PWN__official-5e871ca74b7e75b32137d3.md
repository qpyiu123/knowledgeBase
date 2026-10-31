---
title: "r00t CTF 2024 / PWN"
category: pwn
tags: ["r00t CTF 2024", "PWN", "pwn", "官方资料", "Pwn/EZCANARY&CHECKIN.md", "origin_tag:imported_cats"]
signals: ["r00t CTF 2024", "PWN", "pwn"]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/EZCANARY%26CHECKIN.md"
tools: []
origin: imported_cats
origin_id: "official-5e871ca74b7e75b32137d3"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "r00t CTF 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "c81411ae1b3a30dec1bf86ed2854cbec39d0d644bce31e6073421f3098c7e31d"
origin_body_sha256: e4828134fd9c17f05d51022a73dcabc577cce1ff2045899a0a8c14fee2544884
origin_title: "r00t CTF 2024 / PWN"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "rtctf2024:Pwn"
  chunk_ids: [7743]
  content_sha256: "c81411ae1b3a30dec1bf86ed2854cbec39d0d644bce31e6073421f3098c7e31d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "r00t CTF 2024"
  external_links_not_followed: 0
  id: "official-5e871ca74b7e75b32137d3"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/1de08541e0868128cea3e67c896e57224addce44e64493eb8dd191928cdfed72.blob"
  official_evidence: "https://github.com/r00t-security-lab/rtctf2024"
  original_path: "Pwn/EZCANARY&CHECKIN.md"
  revision: "a273041a04a5dd1eed3e5f49c9345719923a8e9f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/EZCANARY%26CHECKIN.md"
  tags: ["r00t CTF 2024", "PWN", "pwn", "官方资料", "Pwn/EZCANARY&CHECKIN.md"]
  title: "r00t CTF 2024 / PWN"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# r00t CTF 2024 / PWN

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/EZCANARY%26CHECKIN.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：r00t CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：c81411ae1b3a30dec1bf86ed2854cbec39d0d644bce31e6073421f3098c7e31d
> - 导入 ID：official-5e871ca74b7e75b32137d3
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/1de08541e0868128cea3e67c896e57224addce44e64493eb8dd191928cdfed72.blob
> - 源修订：a273041a04a5dd1eed3e5f49c9345719923a8e9f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Pwn/EZCANARY%26CHECKIN.md

## CheckIn

属于pwn的签到，放入IDA后分析发现逻辑为输入一个shell后即可拿到一个shell，可谓打开就送。

## EZCANARY

经典的格式化字符串与栈溢出与canary，通过格式化字符串泄露canary，构造payload将返回地址覆盖为后门即可拿到shell。

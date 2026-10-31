---
title: "r00t CTF 2024 / 5num_secret.jpg"
category: misc
tags: ["r00t CTF 2024", "5num_secret.jpg", "misc", "官方资料", "Misc/5num_secret.md", "origin_tag:imported_cats"]
signals: ["r00t CTF 2024", "5num_secret.jpg", "misc"]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Misc/5num_secret.md"
tools: []
origin: imported_cats
origin_id: "official-c0670ef8388253753d6f9e"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "r00t CTF 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "afb0f9d78b182854942f5d3f48bc5909436bea48adbdf22beade76e699e468f9"
origin_body_sha256: 2438ba622003015e4499f1c1921eff07b381bae6d4f169b4d6fab0a1a7cb826e
origin_title: "r00t CTF 2024 / 5num_secret.jpg"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "rtctf2024:Misc"
  chunk_ids: [7728, 7729]
  content_sha256: "afb0f9d78b182854942f5d3f48bc5909436bea48adbdf22beade76e699e468f9"
  domain: "misc"
  domain_basis: "repository_path"
  event: "r00t CTF 2024"
  external_links_not_followed: 0
  id: "official-c0670ef8388253753d6f9e"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/af93d4eaf0d11df22f98866a27e65d19c0f2a06467fb1f228dc561597b890311.blob"
  official_evidence: "https://github.com/r00t-security-lab/rtctf2024"
  original_path: "Misc/5num_secret.md"
  revision: "a273041a04a5dd1eed3e5f49c9345719923a8e9f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Misc/5num_secret.md"
  tags: ["r00t CTF 2024", "5num_secret.jpg", "misc", "官方资料", "Misc/5num_secret.md"]
  title: "r00t CTF 2024 / 5num_secret.jpg"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# r00t CTF 2024 / 5num_secret.jpg

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Misc/5num_secret.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：r00t CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：afb0f9d78b182854942f5d3f48bc5909436bea48adbdf22beade76e699e468f9
> - 导入 ID：official-c0670ef8388253753d6f9e
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/af93d4eaf0d11df22f98866a27e65d19c0f2a06467fb1f228dc561597b890311.blob
> - 源修订：a273041a04a5dd1eed3e5f49c9345719923a8e9f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Misc/5num_secret.md

## 5num_secret.jpg

题目提示密码是 5 位的数字，放进 binwalk 分离，可以看到有个 zip 文件，或者 010 看到末尾的 zip 标志，分离出来，有密码，可以用 kali 自带的 fcrackzip 进行解密

`fcrackzip -b -c '1' -l 5-5 -u 1DCDF7.zip` 或者其他方式爆破出来密码，密码是 `12138` ，爱情公寓忠实粉丝

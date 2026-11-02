---
title: "CISCN 2024 Qual Writeup / reverse"
split_from: "_imported_cats/crypto/CISCN 2024 Qual Writeup _ crypto__cn-blog-ciscn-swizzer-1.md"
category: crypto
tags: ["crypto", "中文题解", "origin_tag:imported_cats"]
signals: ["crypto", "中文题解", "origin_tag:imported_cats"]
difficulty: medium
source: "https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/"
tools: []
origin: imported_cats
origin_id: "cn-blog-ciscn-swizzer-1"
origin_domain: "crypto"
origin_family: "chinese_blog"
origin_event: "CISCN 2024 初赛"
origin_year: 2024
origin_license: "CC-BY-4.0"
origin_attribution: "CISCN 2024 Qual Writeup 的原作者（见原文署名）"
origin_verification: "author_report_not_reproduced"
origin_content_sha256: "513c31fd2d741e4b64a54b6240fc5dddaa08f86563c48bcaa3729ab83441453b"
origin_body_sha256: 03ad2906fe83bd27772317525559e62c7d42d5f1a85dabd159e7a0a0bbc708ad
origin_title: "CISCN 2024 Qual Writeup / crypto"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [5881, 5882, 5883]
  content_sha256: "513c31fd2d741e4b64a54b6240fc5dddaa08f86563c48bcaa3729ab83441453b"
  domain: "crypto"
  event: "CISCN 2024 初赛"
  id: "cn-blog-ciscn-swizzer-1"
  kind: "licensed_blog_wp_prose"
  language: "zh"
  license: "CC-BY-4.0"
  license_evidence_urls: ["https://creativecommons.org/licenses/by/4.0/"]
  local_path: "61_中文赛事资料/博客授权正文/ciscn-swizzer.md"
  scope_note: "已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。"
  source_author: "CISCN 2024 Qual Writeup 的原作者（见原文署名）"
  source_family: "chinese_blog"
  source_url: "https://blog.swizzer.cc/blog/ciscn-2024-qual-writeup/"
  tags: ["crypto", "中文题解"]
  title: "CISCN 2024 Qual Writeup / crypto"
  verification_status: "author_report_not_reproduced"
  year: 2024
updated: 2026-10-31
---

## 正文

Reverse#

asm_re#

三脚猫水平的我也只能做做Re签到了（

三脚猫水平的我也只能做做Re签到了（

汇编很长，不想看的话直接丢给GPT，GPT大概率会告诉你这玩意儿的主体逻辑的位置。稍微审计一下发现就是个仿射+异或，直接逆回去就行。

python

注意提取目标的数组的时候调一下分组大小和端序就行。

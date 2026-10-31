---
title: "NewStar CTF 2024 / title: 故事新编"
category: crypto
tags: ["NewStar CTF 2024", "title: 故事新编", "crypto", "官方资料", "docs/wp/2024/week3/crypto/gushixinbian.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "title: 故事新编", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/gushixinbian.md"
tools: []
origin: imported_cats
origin_id: "official-daa244397946a64f0ddd31"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "1afeeb6e3f4452ccb4028d44167b5d4e69229117be3675009f20507b5c502b2a"
origin_body_sha256: 98240e2daeee06f31550bac6d823990f138f914cea16f885d49605449ff1a9dc
origin_title: "NewStar CTF 2024 / title: 故事新编"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/crypto/gushixinbian"
  chunk_ids: [8984, 8985]
  content_sha256: "1afeeb6e3f4452ccb4028d44167b5d4e69229117be3675009f20507b5c502b2a"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 2
  id: "official-daa244397946a64f0ddd31"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/0c2738eafb358e28629fd19faafa3714c9d2314883a101be5be9e86aa7b95e04.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/crypto/gushixinbian.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/gushixinbian.md"
  tags: ["NewStar CTF 2024", "title: 故事新编", "crypto", "官方资料", "docs/wp/2024/week3/crypto/gushixinbian.md"]
  title: "NewStar CTF 2024 / title: 故事新编"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / title: 故事新编

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/gushixinbian.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：1afeeb6e3f4452ccb4028d44167b5d4e69229117be3675009f20507b5c502b2a
> - 导入 ID：official-daa244397946a64f0ddd31
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/0c2738eafb358e28629fd19faafa3714c9d2314883a101be5be9e86aa7b95e04.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/gushixinbian.md

## title: 故事新编

titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## 故事新编 1

维吉尼亚密码的加密算法，只要认出来就可以秒。如果你有认真了解过维吉尼亚的加密算法，那么你应该会觉得这段加密非常眼熟；如果你熟练掌握了 AI 的使用，你也可以直接问 AI 这段加密算法像什么。

对于维吉尼亚密码的解密，这里方法并不单一，仅给出一个[可用网址](https://www.guballa.de/vigenere-solver)，用于爆破维吉尼亚密码。

## 故事新编 2

自动密钥密码，与故事新编 1 相类似。在阅读代码之后应该会发现这和维吉尼亚密码非常相似，可以去搜索一下维吉尼亚密码的变种；当然你也可以依靠 AI.

对于自动密钥密码的解密，可以依靠上面的网址修改 Cipher Variant 为 autokey，也可以在网络上找到脚本手撕。

参考链接：[Cryptanalysis of the Autokey Cipher](http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-autokey-cipher/)

---
title: "NewStar CTF 2025 / 欧皇的生日"
category: crypto
tags: ["NewStar CTF 2025", "欧皇的生日", "crypto", "官方资料", "docs/wp/2025/week3/crypto/lucky-birthday.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "欧皇的生日", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/lucky-birthday.md"
tools: []
origin: imported_cats
origin_id: "official-b519ef40a465249cbb175f"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 3d81eb051e7845409579f17712e28cf3efb6fb27a51176d736d18704afc858e2
origin_title: "NewStar CTF 2025 / 欧皇的生日"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/crypto/lucky-birthday"
  chunk_ids: [10928, 10929]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-b519ef40a465249cbb175f"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/51e59baf6c414350115cb4426bed71ba3dca3a72833c1e3b4da5996243c6172d.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/crypto/lucky-birthday.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/lucky-birthday.md"
  tags: ["NewStar CTF 2025", "欧皇的生日", "crypto", "官方资料", "docs/wp/2025/week3/crypto/lucky-birthday.md"]
  title: "NewStar CTF 2025 / 欧皇的生日"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 欧皇的生日

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/lucky-birthday.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-b519ef40a465249cbb175f
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/51e59baf6c414350115cb4426bed71ba3dca3a72833c1e3b4da5996243c6172d.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/lucky-birthday.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 欧皇的生日

本题考查生日攻击。

题目脚本比较简单，就不分析了。

简单来说我们需要提交两个数 $x_1,x_2$ 使得两数哈希值相同，如果不相同，会返回这两数的哈希值。这里的哈希函数是一个自定义的模二次式。

参数： $m=2^{22},t=5000$
也就是说我们要在 $[0,2^{22}-1]$ 范围内找到一对**碰撞**，我们有 5000 次尝试次数。

理论计算可以知道，5000 次绰绰有余。

实际交互时，我们可以把我们提交的数和返回的哈希值用字典存起来，直到发生碰撞。

> [!NOTE] 如何交互？
>
> 先安装 pwn 包。
>
> ```bash
> pip install pwn
> ```
>
> 然后编写脚本：
>
> ```python
> from pwn import remote
> HOST,PORT = "??.??.??.??",?????
> io=remote(HOST,PORT)  #连接靶机，端口。这里 io 可以看成一个交互的实例
> print(io.recvline())  #打印靶机输出的提示信息，类型是 byte
> io.sendline(f"{x1} {x2}")  #向靶机发送数字。注意如果你提交的不是 byte 格式，程序会提醒你（
>
> ```

> [!NOTE]- 非预期
> 理论上你可以把$a,b,c$求出来，然后本地找碰撞。

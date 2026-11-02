---
title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / misc"
split_from: "_imported_cats/pwn/网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 _ pwn__cn-blog-csdn-wangding-1.md"
category: pwn
tags: ["pwn", "中文题解", "栈", "origin_tag:imported_cats"]
signals: ["pwn", "中文题解", "栈"]
difficulty: medium
source: "https://blog.csdn.net/qq_66013948/article/details/143415199"
tools: []
origin: imported_cats
origin_id: "cn-blog-csdn-wangding-1"
origin_domain: "pwn"
origin_family: "chinese_blog"
origin_event: "网鼎杯 2024"
origin_year: 2024
origin_license: "CC-BY-SA-4.0"
origin_attribution: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 的原作者（见原文署名）"
origin_verification: "author_report_not_reproduced"
origin_content_sha256: "935f767875eff56e67b792b0051dfdbbd71e2c9d660513e623a19e3468daa63a"
origin_body_sha256: fe501d347c7b25a472f7aa008877340e85b065be9e3c72ab6bdd2adb7d84c7ce
origin_title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [6051, 6052, 6053]
  content_sha256: "935f767875eff56e67b792b0051dfdbbd71e2c9d660513e623a19e3468daa63a"
  domain: "pwn"
  event: "网鼎杯 2024"
  id: "cn-blog-csdn-wangding-1"
  kind: "licensed_blog_wp_prose"
  language: "zh"
  license: "CC-BY-SA-4.0"
  license_evidence_urls: ["http://creativecommons.org/licenses/by-sa/4.0/"]
  local_path: "61_中文赛事资料/博客授权正文/csdn-wangding.md"
  scope_note: "已核对页面CC许可，离线收录说明正文；代码和图片在此正文中省略，未复现。保留原作者未解决或不确定的表述，抽取可能损失公式排版。"
  source_author: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 的原作者（见原文署名）"
  source_family: "chinese_blog"
  source_url: "https://blog.csdn.net/qq_66013948/article/details/143415199"
  tags: ["pwn", "中文题解", "栈"]
  title: "网鼎杯2024青龙组官方资格赛wp_网鼎杯wp-CSDN博客 / pwn"
  verification_status: "author_report_not_reproduced"
  year: 2024
updated: 2026-10-31
---

## 正文

misc03：

**第一步：**打开流量包，根据协议排序发现了两种有用的协议，一个TCP，一个HTTP，察觉可能是个网站，然后过滤HTTP：

**第二步：**过滤HTTP后发现了个疑似危险ip：39.144.218.183，有爆破目录的可能：

**第三步：**根据很多请求响应对，发现很多都是404，404的状态长度比较短，根据Length排序，从最大的和最小的开始选，找出与众不同的一批流量，发现了木马和访问木马的ip：

**第四步：**跟踪这个流，发现了危险的payload，确定这个就是攻击者：

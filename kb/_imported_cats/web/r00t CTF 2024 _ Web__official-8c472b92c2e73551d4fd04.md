---
title: "r00t CTF 2024 / Web"
category: web
tags: ["r00t CTF 2024", "Web", "web", "官方资料", "Web/ezphp.md", "origin_tag:imported_cats"]
signals: ["r00t CTF 2024", "Web", "web"]
difficulty: medium
source: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/ezphp.md"
tools: []
origin: imported_cats
origin_id: "official-8c472b92c2e73551d4fd04"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "r00t CTF 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "41679bd4f136985b7ce728068a0c15e063ba167491535475f183486a57493b0e"
origin_body_sha256: 2d3c967bd6cadd83e6798fc72ae98a5f7de704a4facfcf2c16a915906c48f5fa
origin_title: "r00t CTF 2024 / Web"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "rtctf2024:Web"
  chunk_ids: [7847, 7848, 7849]
  content_sha256: "41679bd4f136985b7ce728068a0c15e063ba167491535475f183486a57493b0e"
  domain: "web"
  domain_basis: "repository_path"
  event: "r00t CTF 2024"
  external_links_not_followed: 0
  id: "official-8c472b92c2e73551d4fd04"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/bcc54403abb35961fb7ea9d631c53d2a46e66778e5fba02bdf663985ddf71ecf.blob"
  official_evidence: "https://github.com/r00t-security-lab/rtctf2024"
  original_path: "Web/ezphp.md"
  revision: "a273041a04a5dd1eed3e5f49c9345719923a8e9f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/ezphp.md"
  tags: ["r00t CTF 2024", "Web", "web", "官方资料", "Web/ezphp.md"]
  title: "r00t CTF 2024 / Web"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# r00t CTF 2024 / Web

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/ezphp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：r00t CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：41679bd4f136985b7ce728068a0c15e063ba167491535475f183486a57493b0e
> - 导入 ID：official-8c472b92c2e73551d4fd04
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/bcc54403abb35961fb7ea9d631c53d2a46e66778e5fba02bdf663985ddf71ecf.blob
> - 源修订：a273041a04a5dd1eed3e5f49c9345719923a8e9f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/r00t-security-lab/rtctf2024/blob/a273041a04a5dd1eed3e5f49c9345719923a8e9f/Web/ezphp.md

## 正文

提示：或许你能找到我不小心传上去的源代码~

可以用dirsearch扫也可以猜一猜www.zip

拿到源码

拿到源码

+ php弱类型比较：当字符串与数字比较时会将字符串前面的数字拿出来与数字比较，那么让b=abc（任意字母开头即可）

+ preg_match在接收到数组时会返回false，那么num[]=123就可以了

+ md5碰撞，php会将"0e1234"类似的字符串视为0（科学计数法），所以构造两个md5加密后为该格式即可，可以直接搜索md5碰撞

>  MMHUWUV 0e701732711630150438129209816536
  >
  > MAUXXQC 0e478478466848439040434801845361
  >
  > IHKFRNS 0e256160682445802696926137988570
  >
  > GZECLQZ 0e537612333747236407713628225676
  >
  > GGHMVOE 0e362766013028313274586933780773
  >
  > GEGHBXL 0e248776895502908863709684713578
  >
  > EEIZDOI 0e782601363539291779881938479162
  >
  > DYAXWCA 0e424759758842488633464374063001

然后就可以文件上传了

php一句话木马：`<?php eval($_GET['cmd'])?>`这段代码可以执行你给cmd传入的命令，发现放在了同一目录，可以直接file_get_contents，也可以用system（）函数rce，还可以直接打印环境变量中的flag

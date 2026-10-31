---
title: "信息蒐集技術"
category: misc
tags: ["misc", "ctf-wiki", "zh-tw", "recon.md", "origin_tag:imported_cats"]
signals: ["misc", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-c13c475988f4ec"
origin_domain: "misc"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "bbefc109b8a4a5e0252a1c56fe722d959a200bd1cee360ecd4e01c052ef09df8"
origin_body_sha256: b1ea4a30d361b26c746dd443657cd3ff3436c0039d244efedd4294fac2a1ee9f
origin_title: "信息蒐集技術"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1834]
  content_sha256: "bbefc109b8a4a5e0252a1c56fe722d959a200bd1cee360ecd4e01c052ef09df8"
  domain: "misc"
  fetched_at_utc: "2026-10-22T17:53:59.669849+00:00"
  id: "ctf-wiki-c13c475988f4ec"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/recon.md"
  response_sha256: "c2ad0fdde9843f22677fcab4b0ff353bbc3f061289962da1688e5d452e630ac9"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md"
  tags: ["misc", "ctf-wiki", "zh-tw", "misc", "recon.md"]
  title: "信息蒐集技術"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 信息蒐集技術

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：bbefc109b8a4a5e0252a1c56fe722d959a200bd1cee360ecd4e01c052ef09df8
> - 导入 ID：ctf-wiki-c13c475988f4ec
> - 原 domain：misc
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/recon.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:59.669849+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/recon.md

## 網絡信息蒐集技巧

-   公開渠道
-   目標 Web 網頁、地理位置、相關組織
-   組織結構和人員、個人資料、電話、電子郵件
-   網絡配置、安全防護機制的策略和技術細節
-   通過搜索引擎查找特定安全漏洞或私密信息的方法
-   [Google Hacking Database](https://www.exploit-db.com/google-hacking-database/)
-   科學上網

## 基本搜索技巧

-   Google 基本搜索與挖掘技巧
-   保持簡單明瞭的關鍵詞
-   使用最可能出現在要查找的網頁上的字詞
-   儘量簡明扼要地描述要查找的內容
-   選擇獨特性的描述字詞
-   社會公共信息庫查詢
-   個人信息：人口統計局
-   企業等實體：YellowPage、企業信用信息網
-   網站、域名、IP：whois 等

## 地圖和街景搜索

-   國外：Google Map、Google Earth、Google Street View
-   國內：百度地圖、衛星地圖、街景
-   從網絡世界到物理世界：IP2Location
-   whois 數據庫
-   GeoIP
-   IP2Location
-   純真數據庫（QQ IP 查詢）

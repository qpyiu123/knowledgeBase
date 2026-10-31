---
title: "雜項簡介"
category: misc
tags: ["misc", "ctf-wiki", "zh-tw", "introduction.md", "origin_tag:imported_cats"]
signals: ["misc", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-4ae0f8198c522c"
origin_domain: "misc"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "bfaeed4344f97d12c05698a99c60634ea618138ca1917bb24e7ed669380e0457"
origin_body_sha256: 8d47ae4c1c7a510224fbf59bb48904a7125634eb03cfd65322c1bbb151ccbf92
origin_title: "雜項簡介"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1800, 1801, 1802]
  content_sha256: "bfaeed4344f97d12c05698a99c60634ea618138ca1917bb24e7ed669380e0457"
  domain: "misc"
  fetched_at_utc: "2026-10-22T17:53:58.580580+00:00"
  id: "ctf-wiki-4ae0f8198c522c"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/introduction.md"
  response_sha256: "3d15452a2010f423f7ff26c150fec3541bcd87bbb4a6a5e91aa33fed237c6673"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md"
  tags: ["misc", "ctf-wiki", "zh-tw", "misc", "introduction.md"]
  title: "雜項簡介"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 雜項簡介

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：bfaeed4344f97d12c05698a99c60634ea618138ca1917bb24e7ed669380e0457
> - 导入 ID：ctf-wiki-4ae0f8198c522c
> - 原 domain：misc
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/introduction.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:58.580580+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/introduction.md

## 雜項簡介

Misc 是英文 Miscellaneous 的前四個字母，雜項、混合體、大雜燴的意思。

Misc 在國外的比賽中其實又被具體劃分爲各個小塊，有

-   Recon
-   Forensic
-   Stego
-   Misc
-   ……

在國內的比賽中，被統一劃分入 Misc 領域，有時 Crypto（尤其是古典密碼）也被劃入其中。

在 Misc 這一章節中，將從以下幾個方面介紹這一塊的知識：

-   Recon（信息蒐集）

-   Recon（信息蒐集）

-   Encode（編碼轉換）

-   Forensic && Stego（數字取證 && 隱寫分析）

CTF 中 Misc 與現實中的取證不同，現實中的取證很少會涉及巧妙的編碼加密，數據隱藏，被分散嵌套在各處的文件字符串，或是其他腦洞類的
Challenge。很多時候是去精心恢復一個殘損的文件，挖掘損壞硬盤中的蛛絲馬跡,或者從內存鏡像中抽取有用的信息。

現實的取證需要從業者能夠找出間接的惡意行爲證據：攻擊者攻擊系統的痕跡，或是內部威脅行爲的痕跡。實際工作中計算機取證大部分是從日誌、內存、文件系統中找出犯罪線索，並找出與文件或文件系統中數據的關係。而流量取證比起內容數據的分析，更注重元數據的分析，也就是當前不同端點間常用 TLS 加密的網絡會話。

Misc 是切入 CTF 競賽領域、培養興趣的最佳入口。Misc 考察基本知識，對安全技能的各個層面都有不同程度的涉及，可以在很大程度上啓發思維。

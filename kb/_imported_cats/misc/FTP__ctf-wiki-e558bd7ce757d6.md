---
title: "FTP"
category: misc
tags: ["misc", "ctf-wiki", "zh-tw", "traffic", "protocols", "ftp.md", "origin_tag:imported_cats"]
signals: ["misc", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-e558bd7ce757d6"
origin_domain: "misc"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "7df5b35b3faf428a9a61c4eeacb958d099c9c86752c1ef25e13a43b791aea137"
origin_body_sha256: d9c4990a193c63ac5b61c112166ad75aee0465976cc9f34057b288cc94ea1747
origin_title: "FTP"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [2146, 2147]
  content_sha256: "7df5b35b3faf428a9a61c4eeacb958d099c9c86752c1ef25e13a43b791aea137"
  domain: "misc"
  fetched_at_utc: "2026-10-22T17:54:07.257919+00:00"
  id: "ctf-wiki-e558bd7ce757d6"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/traffic/protocols/ftp.md"
  response_sha256: "c4f1f7800aa62d5c657523d887af820c2cb1fc2f708edcebd37faf6329b0042b"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md"
  tags: ["misc", "ctf-wiki", "zh-tw", "misc", "traffic", "protocols", "ftp.md"]
  title: "FTP"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# FTP

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：7df5b35b3faf428a9a61c4eeacb958d099c9c86752c1ef25e13a43b791aea137
> - 导入 ID：ctf-wiki-e558bd7ce757d6
> - 原 domain：misc
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/misc/traffic/protocols/ftp.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:54:07.257919+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/ftp.md

## FTP

`FTP` ( `File Transfer Protocol` ，即文件傳輸協議)是 `TCP/IP` 協議組中的協議之一。 `FTP` 協議包括兩個組成部分，其一爲 `FTP` 服務器，其二爲 `FTP` 客戶端。其中 `FTP` 服務器用來存儲文件，用戶可以使用 `FTP` 客戶端通過 `FTP` 協議訪問位於 `FTP` 服務器上的資源。在開發網站的時候，通常利用 `FTP` 協議把網頁或程序傳到 `Web` 服務器上。此外，由於 `FTP` 傳輸效率非常高，在網絡上傳輸大的文件時，一般也採用該協議。

默認情況下 `FTP` 協議使用 `TCP` 端口中的 `20` 和 `21` 這兩個端口，其中 `20` 用於傳輸數據， `21` 用於傳輸控制信息。但是，是否使用 `20` 作爲傳輸數據的端口與 `FTP` 使用的傳輸模式有關，如果採用主動模式，那麼數據傳輸端口就是 `20` ；如果採用被動模式，則具體最終使用哪個端口要服務器端和客戶端協商決定。

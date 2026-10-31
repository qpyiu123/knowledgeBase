---
title: "簡介"
category: crypto
tags: ["crypto", "ctf-wiki", "zh-tw", "attack-summary", "attack-mode.md", "origin_tag:imported_cats"]
signals: ["crypto", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-835956aeca48fd"
origin_domain: "crypto"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "943d07744a2664388d4ed5a2167ba56a5fb33fc822507e6eecfe6f1fdbc7c210"
origin_body_sha256: a1d628b25f3ff21f8b0ee971725baa1c8ec63b902715ec6e4c58e53e9cdbc98f
origin_title: "簡介"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1027, 1028, 1029]
  content_sha256: "943d07744a2664388d4ed5a2167ba56a5fb33fc822507e6eecfe6f1fdbc7c210"
  domain: "crypto"
  fetched_at_utc: "2026-10-22T17:53:38.176626+00:00"
  id: "ctf-wiki-835956aeca48fd"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md"
  response_sha256: "4a662406b50c682e829df48b432488ee7502e4998874a3850cd8e053680b6f2c"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md"
  tags: ["crypto", "ctf-wiki", "zh-tw", "crypto", "attack-summary", "attack-mode.md"]
  title: "簡介"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# 簡介

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：943d07744a2664388d4ed5a2167ba56a5fb33fc822507e6eecfe6f1fdbc7c210
> - 导入 ID：ctf-wiki-835956aeca48fd
> - 原 domain：crypto
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:38.176626+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/attack-summary/attack-mode.md

## 攻擊模式

在我們攻擊一個密碼學系統時，我們或多或少會得到關於這個系統的一些信息。根據得到信息量的不同，我們可以採用的方法就可能不同。在當今的密碼學分析時，一般我們都會假設攻擊者知道密碼學算法，這個假設是合理的，因爲歷史上有很多保密的算法最後都被人所知，比如 RC4。被知道的方式多重多樣，比如間諜，逆向工程等。

這裏我們根據攻擊者獲取密碼學系統的信息的多少將攻擊模式分爲以下幾類

- **唯密文攻擊**：攻擊者僅能獲得一些加密過的密文。
- **已知明文攻擊**：攻擊者有一些密文對應的明文。
- **選擇明文攻擊**：攻擊者在開始攻擊時可以選擇一些明文，並獲取加密後的密文。如果攻擊者在攻擊中途可以根據已經獲取的信息選擇新的明文並獲取對應的密文，則稱爲適應性選擇明文攻擊。
- **選擇密文攻擊**：攻擊者在開始攻擊之前可以選擇一些密文，並獲取解密後的明文。如果攻擊者在攻擊圖中可以根據已經獲取的信息選擇一些新的密文並獲取對應的明文，則稱爲適應性選擇密文攻擊。
- **相關密鑰攻擊**：攻擊者可以獲得兩個或多個相關密鑰的加密或解密後的密文或明文。但是攻擊者不知道這些密鑰。

## 常見攻擊方法

根據不同的攻擊模式，可能會有不同的攻擊方法，目前常見的攻擊方法主要有

- 暴力攻擊
- 中間相遇攻擊
- 線性分析
- 差分分析
- 不可能差分分析
- 積分分析
- 代數分析
- 相關密鑰攻擊
- 側信道攻擊

## 參考文獻

- https://zh.wikipedia.org/wiki/%E5%AF%86%E7%A0%81%E5%88%86%E6%9E%90

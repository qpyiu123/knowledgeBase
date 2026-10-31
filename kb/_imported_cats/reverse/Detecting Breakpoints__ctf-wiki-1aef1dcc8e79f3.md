---
title: "Detecting Breakpoints"
category: reverse
tags: ["reverse", "ctf-wiki", "zh-tw", "platform", "linux", "detect-bp.md", "origin_tag:imported_cats"]
signals: ["reverse", "ctf-wiki", "zh-tw"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-1aef1dcc8e79f3"
origin_domain: "reverse"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "f7a272d4ca99bd77b2227832688c4053110f9fa5ff6ea17bdab98bd68ce3712a"
origin_body_sha256: 35e7590e7ec37a0bb806cc1c9739acb1a093840e51719e72e192cf7235c035a1
origin_title: "Detecting Breakpoints"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [1513, 1514, 1515]
  content_sha256: "f7a272d4ca99bd77b2227832688c4053110f9fa5ff6ea17bdab98bd68ce3712a"
  domain: "reverse"
  fetched_at_utc: "2026-10-22T17:53:55.734144+00:00"
  id: "ctf-wiki-1aef1dcc8e79f3"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md"
  response_sha256: "270529eeeaa30770576edcb7e72427cdfba289732914e22c577a186567825765"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md"
  tags: ["reverse", "ctf-wiki", "zh-tw", "reverse", "platform", "linux", "detect-bp.md"]
  title: "Detecting Breakpoints"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# Detecting Breakpoints

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：f7a272d4ca99bd77b2227832688c4053110f9fa5ff6ea17bdab98bd68ce3712a
> - 导入 ID：ctf-wiki-1aef1dcc8e79f3
> - 原 domain：reverse
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:53:55.734144+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/linux/detect-bp.md

## Detecting Breakpoints

gdb通過替換目標地址的字節爲`0xcc`來實現斷點, 這裏給出一個簡單的檢測`int 3`斷點的示例:

正常運行程序會輸出Hello, 但是如果之前有在`foo`函數這裏設置`cc`斷點並運行, gdb則無法斷下, 並會輸出`BREAKPOINT`.

這個要繞過也很簡單, 那就是需要閱讀彙編代碼並注意設置斷點不要在`foo`函數入口處. 實際情況就要看檢測斷點的位置是哪裏.

這種監視斷點的反調試技術, 關鍵不在於如何繞過它, 而是在於如何檢測它. 在這個示例中可以很輕鬆的發現, 程序也有打印出相應的信息. 在實際情況中, 程序不會輸出任何信息, 斷點也無法輕易地斷下. 我們可以使用`perl`腳本過濾反彙編代碼中有關`0xcc`的代碼出來進行檢查.

我們可以使用perl腳本過濾反彙編代碼中有關0xcc的代碼出來進行檢查

顯示結果

顯示結果

檢測到後, 既可以將0xcc修改成0x00或0x90, 也可以做任何你想做的操作.

改變0xcc也同樣可能帶來問題, 就如上篇介紹一樣, 程序如果有進行文件校驗, 那麼我們的改變是會被檢測到的. 可能的情況下, 程序也不只是對函數入口點進行檢測, 也會在一個循環裏對整個函數進行檢測.

因此你也可以用十六進制編輯器手動放置一個`ICEBP(0xF1)`字節到需要斷下的位置(而非`int 3`). 因爲`ICEBP`也一樣能讓gdb斷下來.

> Reference: [Beginners Guide to Basic Linux Anti Anti Debugging Techniques](http://www.stonedcoder.org/~kd/lib/14-61-1-PB.pdf)

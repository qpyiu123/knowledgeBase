---
title: "Misc"
category: pwn
tags: ["pwn", "ctf-wiki", "linux", "kernel-mode", "defense", "access-control", "misc.md", "origin_tag:imported_cats"]
signals: ["pwn", "ctf-wiki", "linux"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-12dddcc01efefb"
origin_domain: "pwn"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "bb9d97901248f1d8e0c24224d5f0340398c6710093f4bd545d20afd57c0ea890"
origin_body_sha256: 9d7bd79c1f4d11129891348fca0698652c6eb045781393a68a92de5ff492a483
origin_title: "Misc"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [692]
  content_sha256: "bb9d97901248f1d8e0c24224d5f0340398c6710093f4bd545d20afd57c0ea890"
  domain: "pwn"
  fetched_at_utc: "2026-10-22T17:52:43.394712+00:00"
  id: "ctf-wiki-12dddcc01efefb"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md"
  response_sha256: "b9e29fffe0a2e24df84329fe2a6aad899a6f52156e270e90b9477381494bfbee"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md"
  tags: ["pwn", "ctf-wiki", "linux", "kernel-mode", "defense", "access-control", "misc.md"]
  title: "Misc"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# Misc

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：bb9d97901248f1d8e0c24224d5f0340398c6710093f4bd545d20afd57c0ea890
> - 导入 ID：ctf-wiki-12dddcc01efefb
> - 原 domain：pwn
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:52:43.394712+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/linux/kernel-mode/defense/access-control/misc.md

## 介紹

Linux 內核中有很多數據都只會在 `__init` 階段被初始化，而且之後不會被改變。使用 `__ro_after_init` 標記的內存，在 init 階段結束後，不能夠被再次修改。

## 攻擊

我們可以使用 `set_memory_rw(unsigned long addr, int numpages)` 來修改對應頁的權限。

## mmap_min_addr

mmap_min_addr 是用來對抗 NULL Pointer Dereference 的，指定用戶進程通過 mmap 可以使用的最低的虛擬內存地址。

## 參考

- https://lwn.net/Articles/676145/
- https://lwn.net/Articles/666550/
- https://lore.kernel.org/patchwork/patch/621386/

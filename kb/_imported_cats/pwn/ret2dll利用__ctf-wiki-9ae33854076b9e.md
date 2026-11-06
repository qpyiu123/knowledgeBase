---
title: "ret2dll利用"
category: pwn
tags: ["pwn", "ctf-wiki", "windows", "user-mode", "stackoverflow", "ret2dll.md", "origin_tag:imported_cats"]
signals: ["pwn", "ctf-wiki", "windows"]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md"
tools: []
origin: imported_cats
origin_id: "ctf-wiki-9ae33854076b9e"
origin_domain: "pwn"
origin_family: "ctf-wiki"
origin_event: ""
origin_year: ""
origin_license: "CC-BY-NC-SA-4.0"
origin_attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md"
origin_verification: "source_document_not_reproduced"
origin_content_sha256: "3e52149d46c77a5e0f9845d261a9eca4acdef22d9065141376247b7c3a73cd6f"
origin_body_sha256: 3df83a3128679a12f1f68f1f9b578d58b17e091a8ab8f00d29fbb61b3ff52208
origin_title: "ret2dll利用"
origin_meta:
  asset_refs: []
  attribution: "ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md"
  basis: "original_prose_not_runtime_verified"
  chunk_ids: [672, 673]
  content_sha256: "3e52149d46c77a5e0f9845d261a9eca4acdef22d9065141376247b7c3a73cd6f"
  domain: "pwn"
  fetched_at_utc: "2026-10-22T17:52:43.381156+00:00"
  id: "ctf-wiki-9ae33854076b9e"
  kind: "licensed_chinese_reference"
  language: "zh"
  license: "CC-BY-NC-SA-4.0"
  license_local_path: "61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt"
  local_path: "61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md"
  response_sha256: "2711af863d73a67339c1bdc7e05e538d19bca0d63c2a20cfab24ef93cb4c4dec"
  scope_note: "开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。"
  source_family: "ctf-wiki"
  source_revision: "e225ddfcd420a7f54a5940f47336ebdf8c29b875"
  source_url: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md"
  tags: ["pwn", "ctf-wiki", "pwn", "windows", "user-mode", "stackoverflow", "ret2dll.md"]
  title: "ret2dll利用"
  verification_status: "source_document_not_reproduced"
  year: ""
updated: 2026-10-31
---
# ret2dll利用

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md
> - 许可：CC-BY-NC-SA-4.0
> - 署名：ctf-wiki/ctf-wiki contributors; original at https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md
> - 文档族：ctf-wiki
> - 赛事：（无）
> - 年份：（无）
> - 核验状态：source_document_not_reproduced
> - 正文 sha256：3e52149d46c77a5e0f9845d261a9eca4acdef22d9065141376247b7c3a73cd6f
> - 导入 ID：ctf-wiki-9ae33854076b9e
> - 原 domain：pwn
> - 许可文件：61_中文赛事资料/来源与许可/ctf-wiki/LICENSE.txt
> - 本地快照：61_中文赛事资料/开源正文快照/ctf-wiki/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md
> - 源修订：e225ddfcd420a7f54a5940f47336ebdf8c29b875
> - 抓取时间：2026-10-22T17:52:43.381156+00:00
> - 收录说明：开源中文文档正文。原作者与版本已保留；检索正文省略代码块、缩进代码和图片，完整 Markdown 另存；未复现。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/windows/user-mode/stackoverflow/ret2dll.md

## ret2dll利用

原理與linux下的ret2libc類似，不過需要手動提取地址，目前pwntools不能提取exe文件地址。
源代碼如下
使用gcc(MinGW-W64 x86_64-ucrt-posix-seh)在windows下編譯

`gcc "-Wl,--disable-reloc" -g -o ret2dll.exe ret2dll.c`

## 搭建臨時環境

使用ncat
`ncat -l 8080 --keep-open --exec ".\ret2dll.exe"`
使用win_server
win_server ./ret2dll.exe 8080

exp如下

效果如下

## 原文配图

![ret2dll-1.png](../../_assets/images/530e354703fe6b5e309d387ca503d84bddaa771909afd830cb89ecfab53566fb.png)

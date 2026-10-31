---
title: "NewStar CTF 2024 / One Last B1te"
category: pwn
tags: ["NewStar CTF 2024", "One Last B1te", "pwn", "官方资料", "docs/wp/2024/week3/pwn/one-last-b1te.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "One Last B1te", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/one-last-b1te.md"
tools: []
origin: imported_cats
origin_id: "official-e78ea411fd12e5d15a3153"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 6544569a9891034285d96ed235afa12175e49a54e2c73b1a5fefeb9f6d8d831c
origin_title: "NewStar CTF 2024 / One Last B1te"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/pwn/one-last-b1te"
  chunk_ids: [9060]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-e78ea411fd12e5d15a3153"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/cd0343caa0054d26387bdb0190152fd25e842bbe21900194a33623637dea9144.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/pwn/one-last-b1te.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/one-last-b1te.md"
  tags: ["NewStar CTF 2024", "One Last B1te", "pwn", "官方资料", "docs/wp/2024/week3/pwn/one-last-b1te.md"]
  title: "NewStar CTF 2024 / One Last B1te"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / One Last B1te

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/one-last-b1te.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-e78ea411fd12e5d15a3153
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/cd0343caa0054d26387bdb0190152fd25e842bbe21900194a33623637dea9144.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/one-last-b1te.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## One Last B1te

先查保护和沙箱：

没有 PIE，没有 anary，Partial RELRO，意味着存在延迟绑定 + GOT 表可写。

有一次任意地址写的机会。

有一次任意地址写的机会。

程序在新版 Ubuntu 24 下编译，优化掉了 CSU，此时我们很难利用 ELF 的 gadget 来 ROP.

我们想办法泄露 libc 地址或者 ld 地址然后利用 libc/ld 中的 gadget 来 ROP，执行 open + read + write 来输出 flag 文件内容。

程序中只有 `write` 函数可以进行输出，我们可以利用一个字节任意地址写的机会，把 `close` 函数的 GOT 表的数值改为`write`函数的 PLT 表的地址（因为存在延迟绑定，`close` 在第一次调用之前指向的是 PLT 中的表项，我们很容易利用修改最低一个字节的方法来使其指向 `write` 函数的 PLT 表）。

之后由于 `close(1)` 设置第一个参数为 1，同时 `read(0, v5, 0x110uLL);` 会残留第 2、3 个参数，我们修改 `close` 的 GOT 表之后相当于执行 `write(1,v5,0x110uLL);`，就可以泄露栈上的内容，正好能泄露 libc 地址，之后利用栈溢出再次启动 `main` 函数栈溢出 ROP 即可。

由于 glibc 2.39 版本不容易控制 rdx 寄存器，我们可以使用 `pop rax` + `xchg eax, edx` 的方法来设置 rdx 寄存器的数值。

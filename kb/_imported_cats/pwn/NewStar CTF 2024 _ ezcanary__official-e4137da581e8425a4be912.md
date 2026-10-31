---
title: "NewStar CTF 2024 / ezcanary"
category: pwn
tags: ["NewStar CTF 2024", "ezcanary", "pwn", "官方资料", "docs/wp/2024/week3/pwn/ezcanary.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "ezcanary", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/ezcanary.md"
tools: []
origin: imported_cats
origin_id: "official-e4137da581e8425a4be912"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: cc28b260579db06889cbf62a95849b10db58108872f6059e47f73400391d6f27
origin_title: "NewStar CTF 2024 / ezcanary"
origin_meta:
  asset_refs: [{"downloaded_bytes": 115495, "kind": "image", "local_path": "62_官方赛事题库/objects/94f9fdd279ed641f5c02efc309e363acb0dfd458c355f8f4672d953e30bcbb70.blob", "owner_id": "official-e4137da581e8425a4be912", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week3/ezcanary_1.png", "sha256": "94f9fdd279ed641f5c02efc309e363acb0dfd458c355f8f4672d953e30bcbb70", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week3/ezcanary_1.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/pwn/ezcanary"
  chunk_ids: [9047]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-e4137da581e8425a4be912"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/d4d6dfa2a427a7131c9b7063ffb34200786ad2ea627672e01022e985bf1c90ef.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/pwn/ezcanary.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/ezcanary.md"
  tags: ["NewStar CTF 2024", "ezcanary", "pwn", "官方资料", "docs/wp/2024/week3/pwn/ezcanary.md"]
  title: "NewStar CTF 2024 / ezcanary"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / ezcanary

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/ezcanary.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-e4137da581e8425a4be912
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/d4d6dfa2a427a7131c9b7063ffb34200786ad2ea627672e01022e985bf1c90ef.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-e4137da581e8425a4be912", "relative_path": "docs/assets/images/wp/2024/week3/ezcanary_1.png", "local_path": "62_官方赛事题库/objects/94f9fdd279ed641f5c02efc309e363acb0dfd458c355f8f4672d953e30bcbb70.blob", "downloaded_bytes": 115495, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week3/ezcanary_1.png", "sha256": "94f9fdd279ed641f5c02efc309e363acb0dfd458c355f8f4672d953e30bcbb70", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/ezcanary.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## ezcanary

文件到手先 checksec 一下，看一下是 64 位程序，除了 PIE 其他保护全开

给了后门地址，因为没有开PIE所以可以直接利用

再看 `main` 函数

再看 `main` 函数

很明显的有三个 `read` 都可以栈溢出，程序是 do while 的循环，当第二次输入为 `cat flag\n` 时结束循环并读取第三次输入

但是由于程序开启了 Canary 保护，所以并不能直接 ret2backdoor，而需要先想办法绕过 Canary 才能成功修改返回地址

不管是 `fork()` 函数还是最后 `puts` 的 `one_by_one_bruteforce` 都在提示本题可用逐字节爆破的方式获得 Canary

:::tip

`fork()` 函数具有以下两个特点：

1. 由于子进程和父进程的栈结构是完全相同的，因此保存在子进程栈上的随机数与保存在父进程栈上的随机数完全相同。换句话说，所有子进程和父进程共享同一个 Canary
2. 子进程的崩溃不会导致父进程崩溃

这两个特点意味着当程序调用 `fork()` 函数创建了足够多的子进程时，我们可以不断访问子进程，直到找到一个不会使子进程崩溃的随机数，这个随机数也就是真正的 Canary

:::

64 位要爆破 7 个字节，运气不好的话要多等会

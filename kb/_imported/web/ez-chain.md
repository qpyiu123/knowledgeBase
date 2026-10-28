---
title: "ez-chain"
category: web
tags: [NewStar CTF 2025, wp prose]
signals: [ez-chain]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/ez-chain.md"
tools: []
origin: imported
origin_id: official-708f59ceed7009ec7592da
origin_sha256: a77ebaf1eafc68f86efe55a00e0f09acb821b9d73528c5a209d94b9d89729f76
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / ez-chain

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/ez-chain.md

# ez-chain

> 碎碎念：本来想考 `filter_chain` 所以才取这个名字，大改之后其实不需要多个过滤器组成 chain 来着……


通读一下本题的代码逻辑：输入一个文件名，然后读取文件。

重点：`filter()` 在对 **原始 GET 参数**（还没 `urldecode`）做黑名单检测；而在 `file_get_contents` 之后，`filter_output()` 会检验并对输出做 **重复的 base64_decode**。

搜索一下被过滤掉的关键词：filter php，可以知道本题考的是PHP的伪协议。

题目里 `filter()` 检测了一堆 **关键词**（`php`、`filter`、`base64`、`/`、`:`、`flag` 等），这些都是字母或符号，普通的 URL 编码（浏览器/工具自动的）不会把字母全部编码，所以它们仍会在 `filter()` 的原始字符串里出现并被匹配到。如果我们把整条伪协议（包括字母）**逐字符变为 `%hh`**（例如 `p`->`%70`，`h`->`%68`，`p`->`%70`），那么原始 GET 参数里就不再包含 `php` / `filter` / `base64` / `:` / `/` 等可检测的文本，就能绕过 `filter()`。服务器随后执行 `urldecode()`（一次），把 `%70%68%70%3A%2F%2F...` 还原成 `php://filter/...`，`file_get_contents` 正常工作。

但是，我们知道flag{}一直都包含f，而且base64的包装也没用（会被反复解开），那怎么办？

聪明的小朋友们应该会发现，平台的动态 flag 的内部其实是一个UUID，**它的字符范围永远是 0-f (16进制)**

而 php filter 里面有一个包装器是**rot13**。

0-f 和 flag 经过 rot13 之后就不存在 f 了。所以可以直接绕过过滤。

所以payload就是：


编码后：


得到的 flag 再次 rot13 即可

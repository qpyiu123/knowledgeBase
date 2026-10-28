---
title: "wireshark_checkin"
category: misc
tags: [NewStar CTF 2024, wp prose]
signals: [wireshark_checkin, Wireshark]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/wireshark-checkin.md"
tools: []
origin: imported
origin_id: official-feff48445f53f10bc6fcf3
origin_sha256: c0452b7d2772a6342ba53dfe99818eef45ef92cf7c2bf2dc32a1a7caf00cd2fe
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / wireshark_checkin

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/wireshark-checkin.md

import SVGTCPStart from '@docs/assets/images/wp/2024/TCP_start.svg?component'
import SVGTCPFin from '@docs/assets/images/wp/2024/TCP_fin.svg?component'

# wireshark_checkin

这么多数据包，先快速找到主要部分。

〔原图省略〕

标绿色的是 HTTP 协议相关的，鼠标左键点击 `GET /reverse.c` 这个条目，看 Wireshark 界面左下角，写着一个 `Port: 7070`，这个是 HTTP 服务器的开放端口。

〔原图省略〕

接下来点击最上面的搜索框，输入 `tcp.port == 7070`，这样就可以快速过滤出所有有关这个端口的 TCP 报文

〔原图省略〕

::: tip
HTTP 协议是建立在 TCP 协议之上的，这里的 `tcp.port == 7070` 是过滤出所有有关这个端口的 TCP 报文，而 HTTP 在这个端口之上，因此也相当于过滤出了所有有关这个端口的 HTTP 报文。
:::

这样变得好看多了，但是还不够清晰，因为这里包含了所有有关这个端口的 TCP/HTTP 请求和响应，假如只想看其中一个 HTTP 请求的流程：看 `GET /flag.txt` 这个条目

〔原图省略〕

有一个 `Src port: 33751`，所以过滤器写 `tcp.port == 33751`，因为同一个 HTTP 请求和响应的客户端用的是同一个端口。这样就能只看有关 `flag.txt` 的这次请求和响应的所有过程。

〔原图省略〕

这就是 3 次握手和四次挥手。

::: info 关于 TCP 的 3 次握手和 4 次挥手

3 次握手


4 次挥手


:::

但是下面这个，只有一个 FIN，怎么回事？

〔原图省略〕

因为还有一个 FIN 在 `HTTP/1.1` 这里面，发送完响应后，就立刻第一次挥手了。

〔原图省略〕

flag 在右下角。

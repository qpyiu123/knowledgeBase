---
title: 方法卡 · 文件上传绕过（后缀变体 / 图片马 / .htaccess / 条件竞争）
category: web
tags: [文件上传, 后缀绕过, htaccess, 条件竞争, 图片马, 二次渲染]
signals: [存在上传功能且提示只允许图片, 上传后返回可访问的文件路径, 前端 accept 校验但后端只管后缀, 上传成功却被随机重命名, 上传目录可直接 GET, 提示图片马或竞争或二次渲染]
difficulty: medium
source: kb/web/file-upload-bypass.md, kb/web/upload-race-and-image-polyglot.md
tools: [burpsuite, python, requests]
updated: 2026-11-03
---

# 方法卡 · 文件上传绕过（后缀变体 / 图片马 / .htaccess / 条件竞争）

## 适用场景

- 有上传功能且提示"只允许图片""不能传 php"；
- 上传后返回文件路径（可访问）或落到固定目录，`upload/`、`uploads/`、`static/img/` 能直接 GET；
- 前端有 `accept="image/*"` 校验，后端只管后缀或 `Content-Type`；
- 上传成功但被随机重命名 / 二次渲染 → 需要 `.htaccess`、`.user.ini` 或条件竞争；
- 关键词：upload、上传、shell、绕过、.htaccess、竞争。

## 前置条件

- 确认上传接口的**判据**：只查后缀（黑名单/白名单）、查 Content-Type、还是 `getimagesize()` 查文件头；
- 确认落地后**是否可访问**：先在返回路径 GET 一次，404 说明改名/二次渲染/删除；
- 目标 Web 服务器类型：Apache 才吃 `.htaccess`（需 `AllowOverride All`），Nginx 不看 `.htaccess`，PHP-FPM 可用 `.user.ini`；
- 本卡脚本**离线**：生成字节、配置文本与竞争脚本文本，不发包、不删除任何文件。

## 步骤

1. **绕后缀**：`--exts` 出全清单（`phtml`/`pht`/`phar`/`PHP`/`php.`/`php::$DATA`/`php%00.jpg`/`php.jpg` 多后缀）。
2. **绕 Content-Type**：抓包把 `Content-Type` 改成 `image/jpeg`，不要依赖前端。
3. **绕文件头**：`--png out.png` 生成 CRC 合法的 PNG（PHP 塞在 `tEXt` 块），或 `--polyglot out.gif` 出 `GIF89a` + PHP；`getimagesize` 只读头部 12 字节。
4. **改解析**：`--htaccess addtype --ext jpg` 出 `AddType application/x-httpd-php .jpg`，先传 `.htaccess` 再传 `shell.jpg`；PHP-FPM 环境用 `--user-ini`。
5. **条件竞争**：`--race <上传URL> <落地URL>` 出双线程脚本文本，payload 用 `file_put_contents("pwns.php", ...)` 落地**永久** shell，避免只抢到一次性执行。
6. **验证**：`?c=id`；失败时用 `--judge '<上传后的现象>'` 得到下一步建议。

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/file_upload_bypass.py --exts
.\.venv\Scripts\python.exe kb/_methods/scripts/file_upload_bypass.py --png shell.png
.\.venv\Scripts\python.exe kb/_methods/scripts/file_upload_bypass.py --htaccess addtype --ext jpg
```

## 脚本

脚本路径：`kb/_methods/scripts/file_upload_bypass.py`（纯标准库，离线）

- `ext_variants(stem, ext)`：黑名单/白名单常见绕过后缀（大小写、多后缀、末尾点、尾随空格、NTFS 流、空字节、目录形式）；
- `build_png(php, chunk="tEXt"|"IDAT"|"both", size)`：结构合法、块 CRC 正确、`getimagesize` 能过的 PNG 图片马；
- `build_polyglot(kind, php)` / `check_magic(data, kind)`：GIF/JPG/PNG 图片马与头部判定模拟；
- `htaccess(kind, ext)` / `USER_INI` / `race_script(upload_url, shell_url)` / `judge(text)`；
- `--selftest`：6 组固定断言（含逐块 CRC 校验），退出码 0 才算过。

## 失效场景

- **落地不可执行**：上传目录被 `php_admin_flag engine off`、被 `open_basedir` 隔开、或落在 CDN/对象存储，任何后缀与图片马都无效。
- **二次渲染且是有损 JPEG**：payload 被重编码抹掉，必须改用 PNG 无损像素位、GIF 帧注释，或走 `.htaccess`/`.user.ini`。
- **`.htaccess` 不生效**：`AllowOverride None` 或 Nginx 环境，`AddType` 全废，只能找 LFI/include 解析点。
- **临时文件路径随机**：`/tmp/phpXXXXXX` 不可知，竞争只能打 `move_uploaded_file` 的目标路径。
- **文件名校验严格（白名单 + 随机 uuid + 强类型）**：后缀变体全部失效，只能考虑覆盖配置文件或 ZIP/SVG 类别的二次利用。
- **竞争窗口太窄**：单线程 requests 打不中，需要 raw socket 并发或只保留"先落永久 shell"的 payload。

## 相关文档

- `kb/web/file-upload-bypass.md`（后缀清单、`.htaccess` 与图片马生成、条件竞争原始脚本）
- `kb/web/upload-race-and-image-polyglot.md`（二次渲染原理、EXIF/IDAT 保活、`upload_progress` 变体）

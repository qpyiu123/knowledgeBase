---
title: "sqlupload"
category: web
tags: [NewStar CTF 2025, wp prose]
signals: [sqlupload, MySQL, Nginx, PHP, Burp, Docker]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/sqlupload.md"
tools: []
origin: imported
origin_id: official-5c81f53a2a10f917df5e26
origin_sha256: 55590037bb0dc1b0e668e62715c6863084dc738ae84c26150a2b7066938516c9
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / sqlupload

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/sqlupload.md

# sqlupload

## 代码审计

拿到题目源码后，我们重点关注两个文件：`src/upload.php` 和 `src/getFileList.php`。

### 文件上传

通常我们做上传题，会尝试上传 `.php` 后缀的文件。但查看 `upload.php` 的源码：


我们发现：

1. 用户上传的文件内容（content）和文件名（filename）被直接存入了 MySQL 数据库，而不是保存在 Web 服务器的磁盘目录中。
2. 既然文件在数据库里，Apache/Nginx 就无法直接访问和解析它。这意味着我们就算上传了木马，也没法直接通过 URL 访问来触发执行。

### SQL 注入（`getFileList.php`）

既然无法直接上传 Webshell，我们需要寻找其他突破口。查看 `getFileList.php`：


这里 `preg_match("/upload_time|id/", $order)` 这个正则表达式的意思是：只要字符串中 **包含** `upload_time` 或 `id` 就能通过检查。

这意味着我们可以构造 `upload_time; [恶意SQL]`，只要保留 `upload_time` 这个关键词，后面就可以跟随任意 SQL 语句，达成 SQL 注入。

## 利用 SQL 写文件

在 MySQL 中，有一个特殊的语法 `SELECT ... INTO OUTFILE 'file_path'`，它可以将查询结果导出到一个文件中。

如果我们能控制查询结果中的内容，并且利用这个注入漏洞把结果导出为 `.php` 文件，就能生成 Webshell。

**攻击链条**：

1. **数据投毒**：利用 `upload.php`，将我们的 Webshell 代码伪装成 **文件名** 存入数据库。
2. **导出文件**：利用 `getFileList.php` 的注入点，执行 `INTO OUTFILE`，将包含 Webshell 代码的数据库记录导出到 Web 目录下的 `.php` 文件中。
3. **Get Flag**：访问生成的 PHP 文件，执行系统命令。

## 攻击

### 将文件名改为 Webshell

我们需要上传一个文件，让它的文件名变成 PHP 代码。由于电脑文件系统不支持特殊字符（如 `?`, `<`, `>`），我们需要用 Burp Suite 抓包修改。

### 利用注入写入 Webshell

我们需要构造一个 payload，触发数据库导出操作。

**确定路径**：
题目是 Docker 环境，Web 根目录通常是 `/var/www/html/`。我们打算把文件写入到 `/var/www/html/shell.php`。

**构造 Payload**：
我们要执行的 SQL 逻辑是：
`SELECT ... ORDER BY upload_time INTO OUTFILE '/var/www/html/shell.php'`

根据正则要求（必须包含 `upload_time`），URL 参数应为：
`?order=upload_time INTO OUTFILE '/var/www/html/shell.php'`

### Exploit


如果页面没有报错，说明 SQL 执行成功。此时 MySQL 会把整张表的数据（包含我们刚才上传的恶意文件名）全部写入到 `shell.php` 中。

此时即可利用 `shell.php` 运行 `/readFlag` 拿到 FLAG。

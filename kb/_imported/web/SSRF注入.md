---
title: "SSRF注入"
category: web
tags: [licensed chinese reference]
signals: [SSRF注入, PHP]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/ssrf.md"
tools: []
origin: imported
origin_id: helloctf-e5c4729d8797c5
origin_sha256: d5b98eeb9c9ea2b910c1d0bc4c584730d681b2436711696331bfeafebd183023
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# SSRF注入

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/ssrf.md

---
comments: true

---

# SSRF注入

### file 伪协议读取任意文件


〔原图省略〕

打开网页有登录有注册

〔原图省略〕

访问 robots.txt 发现有个不可访问文件

〔原图省略〕

下载下来拿到源码


重点是这段代码，先初始化 cURL 会话并返回一个 cURL 句柄

设置 cURL 选项，指定要请求的 URL，1 表示开启执行 curl_exec() 时

返回响应内容而不是直接输出，这里就存在 SSRF 漏洞


回头去注册一个账号

〔原图省略〕

看到名字是蓝色的，点击

〔原图省略〕

来的一个新页面，注意 URL 参数有一个 no

〔原图省略〕

改为 2 居然报错了

〔原图省略〕

加一个 ' 报数据库的错误，那这里就存在 SQL 注入，加了单引号和双引号都相同的错误

〔原图省略〕

不加引号直接 or 1=1 # 回显正常

〔原图省略〕

order by 5 报错，再次测试 4 没有报错，说明只有 4 列

〔原图省略〕

直接 -1 union select 1,2,3,4 # 被过滤空格应该是

〔原图省略〕

使用 /**/ 代替空格绕过

〔原图省略〕

接下来爆库、表、字段

〔原图省略〕

最后发现 data 是个序列化的值

〔原图省略〕

结合之前的备份代码，我们可以设置 blog 为 file 伪协议来读取 flag 文件，然后反序列化传入到第四个字段

〔原图省略〕

构造 payload 执行

〔原图省略〕

右键查看源代码可以看到文件

〔原图省略〕

打开再查看源代码拿到 flag

〔原图省略〕


### @指定域名绕过


〔原图省略〕

给出提示，URL 参数的值中必须包含有 `http://notfound.ctfhub.com`

可以采用 @，也就是  HTTP  基本身份认证绕过

HTTP 基本身份认证允许 Web 浏览器或其他客户端程序在请求时提供用户名和口令形式的身份凭证的一种登录验证方式

也就是：`http://www.xxx.com@www.yyy.com`  形式


〔原图省略〕


### IP 转十六进制绕过


〔原图省略〕

尝试将 `127.0.0.1` 转换为 **十六进制** 形式，也就是 `0x7f000001`

构造题目有所需 Payload：`?url=0x7f000001/flag.php`

〔原图省略〕


### localhost 代替 IP 绕过


〔原图省略〕

使用 `localhost` 代替 `127.0.0.1` 绕过

〔原图省略〕


### DNS 重绑定绕过


〔原图省略〕

**🔍 什么是 DNS 重绑定（DNS Rebinding）？**

DNS 重绑定是一种攻击手法，通过操控域名解析结果，使浏览器访问原本受同源策略保护的内网地址或本地服务

攻击者注册一个域名 → 利用 DNS 控制域名解析结果 → 浏览器认为是同源 → 访问受保护资源

**🧠 攻击流程简图**


[打开网站](https://lock.cmpxchg8b.com/rebinder.html)

〔原图省略〕

复制下面那块代码拿到 flag

〔原图省略〕


### 域名代替 IP 绕过


〔原图省略〕

打开网页不让 F12 以及右键

〔原图省略〕

Ctrl + U 发现有个 PHP 文件

〔原图省略〕

访问页面后再次查看源码给出了提示

〔原图省略〕

[安装工具](https://github.com/s0md3v/Arjun?tab=readme-ov-file)


〔原图省略〕

执行命令


可以发现有个 `shell` 参数

〔原图省略〕

传入参数给出了新提示

〔原图省略〕

扫描目录发现有个 `secret.php`

〔原图省略〕

只允许本地访问

〔原图省略〕

结合提示以为是要伪造 XFF 或者 Client-IP，试过了都不行

利用 `shell` 参数构造 SSRF


无果

〔原图省略〕

使用域名跳转绕过


〔原图省略〕

访问拿到源码

〔原图省略〕


第一关就是传入给出的 Key，但是需要用到 `data` 伪协议

〔原图省略〕

第二关是一个 `md4` 的弱比较绕过，其实可以通过科学计算法比较绕过

也就是说要找一个明文是一个科学计算法 0e 开头的，然后其加密也是 0e 开头后面都是数字


最后一关就是 `md5` 强比较绕过，都为数组即可

〔原图省略〕


### 302 跳转绕过


〔原图省略〕

访问环境时显示 url 不存在

〔原图省略〕

构造 url 测试

〔原图省略〕

〔原图省略〕

发现可以访问百度，根据题目提示说

〔原图省略〕

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `localhost`

利用服务器构造 302 跳转绕过

在自己的服务器构建 `302.php`


〔原图省略〕


### 127.0.0.x 代替 IP 绕过


〔原图省略〕

访问环境时显示 url 不存在

〔原图省略〕

构造 url 测试

〔原图省略〕

〔原图省略〕

发现可以访问百度，根据题目提示说

〔原图省略〕

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `localhost`

采用 `127.0.0.x` 的形式绕过，x 为 `2~255`

〔原图省略〕


### 0.0.0.0 代替 IP 绕过


〔原图省略〕

访问环境时显示 url 不存在

〔原图省略〕

构造 url 测试

〔原图省略〕

〔原图省略〕

发现可以访问百度，根据题目提示说

〔原图省略〕

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `localhost`

采用 `0.0.0.0` 的形式绕过

〔原图省略〕


### 端口扫描


〔原图省略〕

url 参数存在 SSRF 漏洞

〔原图省略〕

使用 BurpSuite 抓包遍历端口做扫描

〔原图省略〕

8255 长度不一样，推测端口开着的，看响应拿到 flag

〔原图省略〕


### gopher 协议伪造 HTTP 请求


〔原图省略〕

老样子直接访问 `127.0.0.1/flag.php`，回显一个输入框

〔原图省略〕

查看源码拿到一个 Key 值

〔原图省略〕

输入后回车，提示仅限 `127.0.0.1` 查看

〔原图省略〕

我们尝试用 file:// 读取文件,得到如下代码：


再读取 `flag.php` 的


我们知道只要往 `flag.php` 传 key 值就可以得到 flag

而 `index.php` 可以利用 curl 传 url

那么我们可以用 gopher 协议在 `index.php` 中构造 POST 请求包往 `flag.php` 传 Key 值，以此获取 flag

所以我们通过 gopher 协议构造一个请求，配合 SSRF 模拟成内网用户去访问提交数据

构造这样的一个请求

〔原图省略〕

直接 curl 后接 gopher 协议就先 URL 编码一次

关键的换行符是 CRLF（\r\n），而不是 LF（\n）单独使用

因为 **gopher://** 协议是 **模拟原始 TCP 字节流**，而 HTTP 的协议报文换行是 `\r\n`，不能只用 `\n`

先把换行 `\r\n` 写成 **百分号编码**（url encode）：

- `\r` => `%0D`
- `\n` => `%0A`

于是变成：


我这里思路是先跳到内网的 `index.php` 中再传入 POST 请求

所以要 URL 编码两次（在向服务器发送请求时，首先浏览器会进行一次 URL解码，因为有两个 ?url，所以会解码两次，其次服务器收到请求后，在执行 `curl` 功能时，进行第三次 URL解码）

最终使用 **gopher 协议 + 端口伪造请求**：


最终 payload：


〔原图省略〕


### FastCGI 协议 RCE


〔原图省略〕

**1️⃣ FastCGI 简介**

FastCGI 是一种用于加速 Web 与后端程序（如 PHP-FPM）通信的协议，常见端口 `9000`

如果服务器错误暴露了 FastCGI 服务，攻击者可以伪造协议请求，**让 PHP 直接解释任意文件或执行恶意代码**

**2️⃣ SSRF 打 FastCGI 的核心原理**

利用 SSRF 请求内网 `127.0.0.1:9000` 或其他 PHP-FPM 地址，通过 **gopher://** 伪造 **FastCGI 二进制协议数据包**，让服务器解析指定文件或恶意 payload

**效果**：

- 解析任意本地 `.php` 文件（任意文件包含效果）
- 配合可控日志或 Session 写入恶意 PHP 代码实现 RCE

3️⃣ 典型利用流程

| 步骤 | 动作                                                         |
| ---- | ------------------------------------------------------------ |
| 1️⃣    | SSRF（gopher）打本地 9000 端口                               |
| 2️⃣    | 伪造 FastCGI 请求，指定 `SCRIPT_FILENAME` 指向日志、session、/proc/self/environ 等可以伪造内容的地方 |
| 3️⃣    | 让 PHP-FPM 执行恶意代码                                      |
| 4️⃣    | 成功远程命令执行                                             |

本文要利用一个脚本 [gopherus.py](https://github.com/tarunkant/Gopherus/tree/master)，这个脚本可以对 SSRF 漏洞进行利用，可以直接生成 payload 造成远程代码执行 RCE


我们选择 fastcgi 的


〔原图省略〕

然后输入 `/var/www/index.php`，运行一下 ls

〔原图省略〕

得到 payload

〔原图省略〕


再做一次 URL 编码（因为走的是 `?url`）


可以看到有个 `index.php`

〔原图省略〕

重新跑一下脚本拿 flag

〔原图省略〕

成功拿到 flag

〔原图省略〕


### Redis 协议 RCE


〔原图省略〕

#### 1️⃣ SSRF 与 Redis 结合的核心思路

利用 **SSRF**（Server-Side Request Forgery，服务端请求伪造），让服务器主动去请求攻击者指定的 Redis 服务（或内网未授权的 Redis 服务），并向 Redis 写入恶意 payload，从而进一步实现 **远程命令执行（RCE）**

**2️⃣ SSRF Redis RCE 常见利用链**

| 阶段   | 动作                                                         |
| ------ | ------------------------------------------------------------ |
| 第一步 | SSRF 控制目标服务请求 Redis（通常使用 `gopher://` 协议，可以伪造 TCP payload） |
| 第二步 | 向 Redis 发送写入命令，修改其配置，如 `dir` 和 `dbfilename`  |
| 第三步 | 向 Redis 写入 **恶意 SSH 公钥** 或 **计划任务脚本** 到 Web 根目录或 `.ssh/authorized_keys` |
| 第四步 | 触发 Redis 保存（`SAVE`），将 payload 写入磁盘，造成任意代码执行或提权 |

本题依然可以使用 gopherus 实施攻击

〔原图省略〕

再 URL 编码一次


〔原图省略〕

---
title: "SQL 注入"
category: web
tags: [licensed chinese reference]
signals: [SQL 注入, Burp, MySQL]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh/docs/web/sqli.md"
tools: []
origin: imported
origin_id: ctf-wiki-2e2f18d5dea538
origin_sha256: 9b82a2350460f41303c10293a65916fa96975d9c3a4fbade2a11c5466f534eb4
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# SQL 注入

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh/docs/web/sqli.md

# SQL 注入

## 基本概念

-   SQL 注入是一种将 SQL 代码插入或添加到应用（用户）的输入参数中，之后再将这些参数传递给后台的 SQL 服务器加以解析并执行的攻击。
-   攻击者能够修改 SQL 语句，该进程将与执行命令的组件（如数据库服务器、应用服务器或 WEB 服务器）拥有相同的权限。
-   如果 WEB 应用开发人员无法确保在将从 WEB 表单、cookie、输入参数等收到的值传递给 SQL 查询（该查询在数据库服务器上执行）之前已经对其进行过验证，通常就会出现 SQL 注入漏洞。

## 常用工具

-   Burp Suite：[Burp Suite 使用介绍](http://drops.xmd5.com/static/drops/tools-1548.html)
-   Tamper Data (Firefox addon)
-   HackBar (Firefox addon)
-   sqlmap：[sqlmap 用户手册](http://drops.xmd5.com/static/drops/tips-143.html)

## 注入常见参数

-   `user()`：当前数据库用户
-   `database()`：当前数据库名
-   `version()`：当前使用的数据库版本
-   `@@datadir`：数据库存储数据路径
-   `concat()`：联合数据，用于联合两条数据结果。如 `concat(username,0x3a,password)`
-   `group_concat()`：和 `concat()` 类似，如 `group_concat(DISTINCT+user,0x3a,password)`，用于把多条数据一次注入出来
-   `concat_ws()`：用法类似
-   `hex()` 和 `unhex()`：用于 hex 编码解码
-   `load_file()`：以文本方式读取文件，在 Windows 中，路径设置为 `\\`
-   `select xxoo into outfile '路径'`：权限较高时可直接写文件

## 语法参考与小技巧

### 行间注释

-   `--`


-   `#`


### 行内注释

-   `/*注释内容*/`


-   `/*! MYSQL专属 */`


### 字符串编码

-   `ASCII()`：返回字符的 ASCII 码值
-   `CHAR()`：把整数转换为对应的字符

## 后台万能密码

-   `admin' --`
-   `admin' #`
-   `admin'/*`
-   `' or 1=1--`
-   `' or 1=1#`
-   `' or 1=1/*`
-   `') or '1'='1--`
-   `') or ('1'='1--`
-   以不同的用户登陆 `' UNION SELECT 1, 'anotheruser', 'doesnt matter', 1--`

## 注入语句备忘

### 数据库名


### 表名

-   union 查询


-   盲注


-   报错


### 列名

-   union 查询


-   盲注


-   报错


-   利用 `PROCEDURE ANALYSE()`


### 根据列名查询所在的表


### 绕过引号限制


### 绕过字符串黑名单


使用 `CONCAT()` 时，任何个参数为 null，将返回 null，推荐使用 `CONCAT_WS()`。`CONCAT_WS()`函数第一个参数表示用哪个字符间隔所查询的结果。

### 条件语句

`CASE`, `IF()`, `IFNULL()`, `NULLIF()`.


### 延时函数

`SLEEP()`, `BENCHMARK()`.


### order by 后的注入

`order by` 由于是排序语句，所以可以利用条件语句做判断，根据返回的排序结果不同判断条件的真假。一般带有 `order` 或者 `order by` 的变量很可能是这种注入，在知道一个字段的时候可以采用如下方式注入：

原始链接：`http://www.test.com/list.php?order=vote`

根据 `vote` 字段排序。找到投票数最大的票数 `num` 然后构造以下链接：


看排序是否变化。还有一种方法不需要知道任何字段信息，使用 `rand` 函数：


以上两个会返回不同的排序，判断表名中第一个字符是否小于 128 的语句如下：


### 宽字节注入

国内最常使用的 GBK 编码，这种方式主要是绕过 `addslashes` 等对特殊字符进行转移的绕过。反斜杠 `\` 的十六进制为 `%5c`，在你输入 `%bf%27` 时，函数遇到单引号自动转移加入 `\`，此时变为 `%bf%5c%27`，`%bf%5c`
在 GBK 中变为一个宽字符「縗」。`%bf` 那个位置可以是 `%81-%fe` 中间的任何字符。不止在 SQL 注入中，宽字符注入在很多地方都可以应用。

### DNSLOG注入

**DNS在解析的时候会留下日志，通过读取多级域名的解析日志，来获取信息。简单来说就是把信息放在高级域名中，传递到自己这，然后读取日志，获取信息。**

dnslog平台：[http://ceye.io/](http://ceye.io/)

〔原图省略〕

## 参考资料

-   [SQL 注入速查表](http://drops.xmd5.com/static/drops/tips-7840.html)
-   [MySQL 注入技巧](http://drops.xmd5.com/static/drops/tips-7299.html)
-   [MySQL 注入科普](http://drops.xmd5.com/static/drops/tips-123.html)
-   [MySQL 注入总结](http://www.91ri.org/4073.html)
-   [《SQL 注入攻击与防御》](http://product.dangdang.com/23364650.html)

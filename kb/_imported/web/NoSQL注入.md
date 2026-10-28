---
title: "NoSQL注入"
category: web
tags: [licensed chinese reference]
signals: [NoSQL注入, PHP, Python]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/nosql.md"
tools: []
origin: imported
origin_id: helloctf-cc72f88011f633
origin_sha256: 519a1ea9bee14f2fc279237b6c4f654b373ab7b27a79a245f36f424d22a78a09
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# NoSQL注入

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/nosql.md

---
comments: true
---

# NoSQL注入

### 简介

在「SQL注入」一章里我们已经知道：注入的本质是 **用户输入被当成了查询语句的一部分来解析**。这个思路不只属于关系型数据库——只要后端把可控输入拼进（或传进）数据库查询，注入就存在。

NoSQL（Not Only SQL）是一类非关系型数据库的统称，CTF 里最常见的是 **MongoDB**。它没有 SQL 语法，查询是用结构化的对象（BSON/JSON 风格）描述的，因此攻击方式也完全不同：我们不再拼接字符串，而是想办法让查询条件里多出几个 **操作符**，比如 `$ne`（不等于）、`$gt`（大于）、`$regex`（正则匹配）。

本章路线：先用最少篇幅搞懂 MongoDB 的查询方式 → 理解操作符注入的原理 → 看 PHP + MongoDB 的典型漏洞代码与利用 → 用 Python 写盲注爆破脚本 → 完整做一道 CTF 题。

### NoSQL 与 MongoDB 极简入门

够用即止，你只需要记住三组对应关系：


一个 `users` 集合里的文档长这样：


#### 基本查询语法

MongoDB 的查询条件是一个对象，键是字段名，值是要匹配的内容：


字段的值还可以是一个 **操作符对象**，以 `$` 开头的键就是操作符：


常用操作符，记住这几个就够打 CTF 了：

- `$ne`：不等于。条件成立范围最大，登录绕过首选。
- `$gt` / `$lt`：大于 / 小于。对字符串按字典序比较。
- `$regex`：正则匹配。配合 `^` 可以逐位确认前缀，盲注核心。
- `$or` / `$and`：逻辑或 / 逻辑与。

再补一句 PHP 侧的知识：PHP 的 MongoDB 驱动里，查询条件就是一个 PHP 数组。比如：


这行 PHP 等价于上面第二条 MongoDB 查询。**记住"查询条件就是数组"这一点，后面的注入全靠它。**

### 注入原理

#### 从字符串拼接到操作符注入

SQL 注入是往字符串里塞语法，NoSQL 注入则是往 **结构** 里塞操作符。典型场景是登录：


如果 `$user` 和 `$pass` 是攻击者可控的，并且能传入 **数组** 而不是字符串，查询就会变成：


翻译成人话：找一个 username 不等于空、password 也不等于空的用户——数据库里随便哪个用户都满足，于是直接以第一个用户（通常是 admin）的身份登录成功。这就是 NoSQL 注入最经典的 **登录绕过**。

#### PHP 中怎么把参数传成数组

PHP 的 GET/POST 参数有个特性：参数名后面加 `[]` 就能构造数组（详见「PHP特性与常见绕过」一章）。比如请求：


PHP 解析后：


如果后端代码把这个值原样塞进 MongoDB 查询数组，注入就成立了。

对于 `application/json` 的接口更直接，JSON 本身就能表达嵌套对象：


后端 `json_decode` 之后直接传给 MongoDB 驱动，效果一样。

注意区分：这和「SQL注入」里 `" or 1=1 --` 的思路不同，MongoDB 查询不是字符串拼接出来的，**闭合引号、注释符那一套在这里没用**；我们要做的是改变查询条件的"类型"——把字符串换成操作符对象。

#### 盲注原理

有些场景没有登录绕过可用（比如目标字段是 flag 而不是密码），但查询结果会区分"有没有匹配到文档"（页面显示登录成功/失败、用户存在/不存在）。这时可以用 `$regex` 逐位爆破：


每次请求只问一个"是/否"问题，根据回显判断对错，对就把前缀加长一位再猜下一个字符。思路和「SQL注入」里的布尔盲注完全一致，只是工具从 `substr()` 换成了 `$regex`。

### PHP + MongoDB 漏洞代码示例

一个典型的有漏洞的登录页面 `login.php`：


正常用法下传入 `username=admin&password=xxx`，查询是精确匹配，没问题。问题在于 `$username` / `$password` 没有强制转成字符串，攻击者可以传数组。

#### 利用一：登录绕过


查询条件变成"用户名不等于 xxx 且密码不等于 xxx"，匹配到库里第一个用户，直接登录成功。

如果知道管理员用户名是 `admin`，想精确绕过他的密码：


#### 利用二：判断字段值（盲注入口）

假设登录成功页面和失败页面内容不同，而我们想知道 `password`（或某个 `flag` 字段）的值：


返回"登录成功"则前缀猜对，继续猜下一位；返回"用户名或密码错误"则换字符重试。这就是下面要自动化的过程。

#### 修复方式（顺带一提）

防御很简单：强制类型转换 + 拒绝数组输入。


在「PHP代码审计」一章的视角下，看到 MongoDB 查询条件的值直接来自 `$_GET`/`$_POST`/`$_REQUEST` 且没有 `is_string` 或 `(string)` 处理，基本就可以断定存在 NoSQL 注入。

### Python 盲注爆破脚本

逐位手测太慢，写个脚本自动化（Python 脚本的一般写法可以参考「Python脚本」一章的思路，这里直接给完整实现）。目标是爆破 `admin` 用户的 `password` 字段，以"登录成功"字样作为判断依据：


几个要点：

- `password[$regex]` 是 POST 表单的字段名，PHP 解析后得到 `['$regex' => '^...']`，与漏洞代码的查询数组拼在一起就构成了操作符注入。
- 每次只确认一个字符，确认后立即扩展前缀——这就是"逐位"的含义。
- 一轮循环没有任何字符命中时结束，避免死循环。
- 如果题目是 JSON 接口，把 `requests.post(URL, data=...)` 换成 `json={"username": "admin", "password": {"$regex": "^" + prefix}}` 即可，逻辑不变。

### CTF 例题：easy_nosql

来看一道完整的入门题。题目描述：一个 MongoDB 写的登录框，提示"管理员好像把 flag 设成了自己的密码"，给出源码：


**第一步：信息收集与判断注入点。**

题目明确说是 MongoDB，且源码显示 `$_POST` 参数直接进查询、数组没被拦住。先试试经典绕过：


返回 `welcome, admin`——注入确认，并且拿到了管理员用户名 `admin`。

**第二步：确认不能直接绕过拿 flag。**

页面只回显 `username`，不回显 `password`，而 flag 就是密码。所以登录绕过本身拿不到 flag，需要盲注把 `password` 逐位爆出来。

**第三步：手动验证盲注可行性。**


返回 `welcome, admin`，说明第一个字符是 `f`。再试 `^fl`、`^fla`……都成立，基本可以断定密码就是 `flag{...}` 格式。

**第四步：上脚本爆破。**

用上一节的脚本，把判断依据改成 `welcome`：


运行后输出逐位增长：


提交 `flag{n0sql_1nj3ct10n_1s_fun}`，解题完成。

**复盘**：本题完整走了一遍 NoSQL 注入的标准流程——识别 MongoDB → PHP 数组传参注入操作符 → `$ne` 绕过确认漏洞 → `$regex` 逐位盲注拿数据。真实题目可能的变化无非几种：参数走 JSON 接口、过滤了 `$` 开头的键（可以考虑换 `$where` 等其他注入面，或利用框架解析差异绕过）、回显差异更隐蔽（用响应时间或状态码做判断）。核心思路不变：**把字符串输入变成操作符对象，让数据库替你回答问题。**

### 小结

- MongoDB 查询条件是结构化对象，`$ne`、`$gt`、`$regex` 等操作符是注入的武器。
- PHP 中参数名加 `[]` 可传数组（见「PHP特性与常见绕过」），后端不校验类型就会形成注入。
- 登录绕过用 `$ne`，拿数据用 `$regex` 逐位盲注，配合 Python 脚本自动化。
- 防御：强制 `(string)` 类型转换，拒绝数组输入。

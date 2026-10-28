---
title: "PHP 代码审计"
category: web
tags: [licensed chinese reference]
signals: [PHP 代码审计, PHP, Python]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/php_code_audit.md"
tools: []
origin: imported
origin_id: helloctf-6e1c7bc1c530fb
origin_sha256: 471b453c20a1b32b263d23d4b22e04112d403cd966fad7f55f5974bd984bffa7
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# PHP 代码审计

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/php_code_audit.md

---
comments: true

---

# PHP 代码审计

### PHP 字符串序列化


〔原图省略〕

打开网页登录界面，题目说登录不进去，尝试找找其他线索

〔原图省略〕

在 CSS 文件中找到注释

〔原图省略〕

URL 跟上参数拿到源码

我们在 Cookie 的 BUGKU 参数中传入序列化后的值

〔原图省略〕

找个在线生成的网站即可

〔原图省略〕

BurpSuite 拦截抓包修改拿到 flag

〔原图省略〕


### PHP 反序列化之 __toString() 魔术方法


〔原图省略〕

打开网页给出源码

〔原图省略〕


让 `$data->username == 'ZeroZone'`，并让 `$data->password`

由于 `__destruct()` 会输出 `$data->password`，如果能让 `$data->password` 为一个 `ZeroZone` 对象，并且触发 `__toString()`，就可以执行任意代码


〔原图省略〕


### PHP & 引用相同内存


〔原图省略〕

打开靶场给出源码


md5 绕过很简单，科学计数法及数组绕过都可以

这才来到最关键的地方，如何在序列化前让 `$this->correct === $this->input`  呢？

我们创建 BUU 类后，重新给 $this->correct 赋值成 $this->input 的值

在 PHP 中，`&` 表示 **引用赋值**，效果是：

 两个变量或者属性同时指向同一块内存，**任何一方变化，另一方立刻同步变化**


〔原图省略〕


### PHP POP 链


〔原图省略〕


首先传入 Year 中的 $key="happy new year"

条件成立调用 firecrackers 方法

但 Rabbit 中 wish 不存在，所以调用 get 魔法方法

此时 $name() 对象被当成函数访问，类型实际上是 Rabbit 对象

但 invoke 方法实际上是调用了 Nevv

因为 check() 是个方法不存在，所以调用了 call 方法

$a 和 $b 是两个 Year 对象，$c 是一个 Rabbit 对象

它的构造函数接受 $b（另一个 Year 对象）作为参数

这意味着 Rabbit 对象 $c 会持有 $b 对象

$e 是一个 Happy 对象用于执行系统命令

将 Rabbit 对象 $c 赋值给 $a->rabbit

将 Nevv 对象 $d 赋值给 $b->rabbit

将 Nevv 对象 $d 赋值给 $b->rabbit

Year 对象的 $rabbit 属性会被赋值为 Rabbit 对象

而 Rabbit 对象的 $aspiration 属性会被赋值为 Year 对象，依此类推


拿到 flag

〔原图省略〕


### PHP 个数不等绕过__wakeup()


〔原图省略〕

打开网页给出了备份提示

〔原图省略〕

扫后台发现 ZIP 文件

〔原图省略〕

下载下来打开 index.php 拿到源码（flag.php 是假的）

〔原图省略〕

看到了反序列化，接下来去看 class.php


我们需要传入 username = admin，password = 100，于是构造反序列化


还没有结束，因为类的两个属性声明为 private，只在所声明的类中可见，在该类的子类和该类的对象实例中均不可见

所以要在此基础上补上 %00 的空字符


最后是绕过 __wakeup()

当反序列化中对象属性的个数和真实的个数不等时，__wakeup() 就会被绕过，所以修改使其不相等即可


〔原图省略〕


### PHP 反序列化字符逃逸


〔原图省略〕

打开网页拿到源码


首先让参数f等于 “phpinfo”，因为题目提示说这里可能会找到些东西

〔原图省略〕

很明显是要读取这个文件，代码里读取文件的地方在这里


**反序列化字符串逃逸的原理：**


首先康康反序列化结果长啥样


那么我们如果想要读取 `d0g3_f1ag.php` 文件的内容就需要令反序列化后的


则初步反序列化内容


再看到 `$serialize_info = filter(serialize($_SESSION));`

先经过序列化，然后在进行 `filter` 函数，也就是过滤替换操作

这样的话就很有可能会造成序列化字符串逃逸的问题

首先默认的序列化数据是


这里可以控制的部分是 user 和 function 的内容

于是要利用过滤，用 user 吃掉后面的，加 `;` 闭合掉前面的键值 `function`


之后在 function 的部分便可以写入数据控制后面的内容了

要吃掉的数据一共是 22 个，于是 user 的值为 phpphpphpphpphpphpflag

_SESSION[function] 的值为


这里要保证数组内的个数相等，所以要传入两个值，于是构造利用 payload


由于 `_SESSION` 数组有 3 个值，则需要在后面补充随便一个值即可

传入后 `$serialize_info` 的就为以下值


随后再读取 `s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";`

随后大括号闭合

后面的 `";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}` 值丢弃

读取到 `d0g3_f1ag.php` 内容为


再依法读取 `/d0g3_fllllllag` 即可


〔原图省略〕


### Python Pickle 反序列化之 subprocess


〔原图省略〕

提示了源码在 /src 目录，直接访问

〔原图省略〕


- `/ppicklee` 路由只支持 `POST` 方法。
- 从表单中获取 `data` 字段，并进行 Base64 解码。
- 通过 `sys.modules` 禁用 `os` 和 `sys` 模块。
- 检查反序列化数据中是否包含黑名单中的关键字，如果包含则返回错误信息。
- 如果数据通过检查，则尝试反序列化数据，成功返回 `success pickle`，失败返回 `fail pickle`

因为题目告诉了我们 flag 在 /flag下，且其 src 路由会读取文件 app.py 内容并输出

因为禁用了 os 和 sys 模块，所以我们使用另一个模块 **subprocess** 执行系统命令


〔原图省略〕

访问 src 目录拿到 flag

〔原图省略〕


### Python Pickle 反序列化之 commands


〔原图省略〕

打开网页给出提示

〔原图省略〕

网页太多了，用脚本去找


〔原图省略〕

找到后购买钱不够，修改前端代码的折扣

〔原图省略〕

购买后显示只能 admin 访问

〔原图省略〕

查看 Cookies 发现有 JWT

〔原图省略〕

使用工具破解密钥

〔原图省略〕

去在线网站生成 admin 的 JWT

〔原图省略〕

替换掉刷新网页

〔原图省略〕

点击后没反应，查看源代码有压缩文件

〔原图省略〕

下载后拿到源码


become 参数存在 Pickle 反序列化漏洞


替换为脚本生成的序列化代码拿到 flag

〔原图省略〕


### PHP Create_function() 反序列化


〔原图省略〕

打开网页给出了源码


首先，反序列化不调用构造函数

因为反序列化时通过读取对象的字节流来恢复对象的状态，而不是通过调用对象的构造函数来创建对象

所以直接来看析构函数


但是空的函数不能执行，所以我们要构造一个

这里要利用 `Create_function()` 函数


`create_function` 实际上会在内部执行以下操作：

1. 生成一个唯一的函数名(如 `__lambda_func`)
2. 用给定的参数和代码体创建一个新函数
3. 返回这个函数名以便后续调用

构造序列化代码


这样相当于


实际创建的代码为


得到


需要注意因为是 `private` 属性，所以不能直接使用

应该为 `\00类名\00`


〔原图省略〕


### PHP %00 绕过 Private


〔原图省略〕

打开网页给出了备份提示

〔原图省略〕

扫后台发现 ZIP 文件

〔原图省略〕

下载下来打开 index.php 拿到源码（flag.php 是假的）

〔原图省略〕

看到了反序列化，接下来去看 class.php


我们需要传入 username = admin，password = 100，于是构造反序列化


还没有结束，因为类的两个属性声明为 private，只在所声明的类中可见，在该类的子类和该类的对象实例中均不可见

所以要在此基础上补上 `%00`


最后是绕过 __wakeup()

当反序列化中对象属性的个数和真实的个数不等时，__wakeup() 就会被绕过，所以修改使其不相等即可


〔原图省略〕


### PHP \00 绕过 Private


〔原图省略〕

打开网页给出了源码


首先，反序列化不调用构造函数

因为反序列化时通过读取对象的字节流来恢复对象的状态，而不是通过调用对象的构造函数来创建对象

所以直接来看析构函数


但是空的函数不能执行，所以我们要构造一个

这里要利用 `Create_function()` 函数


`create_function` 实际上会在内部执行以下操作：

1. 生成一个唯一的函数名(如 `__lambda_func`)
2. 用给定的参数和代码体创建一个新函数
3. 返回这个函数名以便后续调用

构造序列化代码


这样相当于


实际创建的代码为


得到


需要注意因为是 `private` 属性，所以不能直接使用

应该为 `\00类名\00`


〔原图省略〕

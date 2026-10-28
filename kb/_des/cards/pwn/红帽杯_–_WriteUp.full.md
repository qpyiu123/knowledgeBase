---
title: "红帽杯 – WriteUp"
category: pwn
tags: ["红帽杯", "pwn", "ChaMd5-Venom", "PHP-write-getshell", "Yii2-RCE2", "phpggc"]
signals: ["红帽杯 2021", "ChaMd5-Venom", "PHP-write-getshell", "Yii2-RCE2", "phpggc", "sqli-blind", "HEC-jacobian", "XTEA-XOR", "fmt-write", "pwn_unknown", "WriteUp", "ChaMd5", "Venom", "PHP"]
difficulty: hard
source: "https://www.ctfiot.com/1970.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 红帽杯 – WriteUp

> 赛事：红帽杯 2021 | 方向：pwn | 难度：hard | 工具：PHP

## 一句话总结

红帽杯WriteUp多方向,涵盖ChaMd5 Venom战队招新文+PHP写文件短代码+Yii2 RCE2反序列化+SQL盲注+超椭圆曲线Jacobian DLP+XTEA魔改+fmt-write逐字节覆盖。

## 攻击链

1. PHP写文件:preg_match过滤system/eval/exec/base/compress/chr/ord/str/replace/pack/assert等+strlen<=33,fwrite到hack.php
2. 拼接flag.php内容到hack.php,使用bypass短代码
3. Yii2反序列化:./phpggc Yii2/RCE2 'eval($_REQUEST["ant"])' base64编码,Yii2\db\BatchQueryResult->dataReader FakedGenerator formaters
4. 二次解码触发eval
5. SQL盲注:ascii(mid((select concat(id,username,password) from users),i,1))=cc+id=-1 or过滤
6. HEC超椭圆曲线:已知y=x和y=x^7,GF(p)上HyperellipticCurve,Jacobian DLP,blocks切分8字节反推keys
7. 模数生成器攻击:Str(last18位)+000+Str(first18位),factordb/factor分解
8. 32轮XTEA+key[0]+=789+key[3]+=135攻击
9. fmt-write逐字节改one_gadget地址到ret_addr
10. libc-2.27 0x10a45c one_gadget

## 关键 payload

```
flag{1b82f60a-43ab-4f18-8ccc-97d120aae6fc}
```

## 经验教训

复杂混合赛题考查多个方向:PHP写入短代码绕字符限制+phpggc工具生成反序列化payload+HEC Jacobian DLP用Sage解+fmt-write逐字节改got都需要熟练运用。

## 标签

ChaMd5-Venom、PHP-write-getshell、Yii2-RCE2、phpggc、sqli-blind、HEC-jacobian、XTEA-XOR、fmt-write、format-string-overwrite、libc-leak

## 参考来源

- https://www.ctfiot.com/1970.html
- 原文件：红帽杯_–_WriteUp.full.md

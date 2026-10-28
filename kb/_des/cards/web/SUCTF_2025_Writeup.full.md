---
title: "SUCTF 2025 Writeup - XMCVE-Polaris"
category: web
tags: ["SUCTF", "web", "php-unserialize", "cake-php", "react-promise", "oss-version"]
signals: ["SUCTF 2025", "php-unserialize", "cake-php", "react-promise", "oss-version", "ssti", "magic-method-chain", "web_unknown", "SUCTF", "XMCVE-Polaris", "PHP", "Solidity", "SU_OSS", "oss"]
difficulty: medium
source: "https://www.ctfiot.com/224263.html"
tools: ["PHP", "Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SUCTF 2025 Writeup - XMCVE-Polaris

> 赛事：SUCTF 2025 | 方向：web | 难度：medium | 工具：PHP、Solidity

## 一句话总结

SUCTF 2025 XMCVE-Polaris 第 4，PHP 反序列化新链 + Solidity 签名复用 + 内置服务器源码泄露。

## 攻击链

1. SU_OSS: ls 找 oss 旧版本文件
2. SU_POP: 入口 /ser?ser=base64 → React\Promise\Internal\RejectedPromise __destruct
3. reason 拼接触发 __toString → Cake\Http\Response
4. stream = new Cake\ORM\Table 触发 __call('rewind')
5. BehaviorRegistry._methodMap = ['rewind' => ['z', 'generate']]
6. MockClass.generate() eval(classCode) call_user_func
7. system($_GET[1]) 弹 shell
8. flag 在 /root/flag.txt，suid find 提权
9. SU_photogallery: php -S 内置服务器源码泄露 /unzip.php
10. check_extension/chech_base 关键词+base64 双重过滤
11. 魔改 zip 注释 + Unicode 文件名绕过
12. SU_Checkin: 23 位密码 SePassWordLen23SUCTF + Jasypt PBEWithMD5AndDES
13. 3 位爆破字典 (62^3=238328)
14. Onchain Magician: Solidity 0.8.28 magic box ecrecover 签名复用
15. isOpened 状态重放 + chainId

## 关键 payload

```
/ser?ser=<base64(serialize($a))>
```

## 经验教训

CakePHP 链子 fix 时只改头/尾，中间常被保留；找链应优先按中间环节搜索。

## 标签

php-unserialize、cake-php、react-promise、oss-version、ssti、magic-method-chain

## 参考来源

- https://www.ctfiot.com/224263.html
- 原文件：SUCTF_2025_Writeup.full.md

---
title: "第三届香山杯网络安全大赛初赛 Writeup"
category: misc
tags: ["香山杯", "misc", "PHP-unserialize", "POP-chain", "__destruct", "__toString"]
signals: ["香山杯 2022", "PHP-unserialize", "POP-chain", "__destruct", "__toString", "__invoke", "preg_match-bypass", "ChaCha20-RC4", "Chaquopy", "deserialize", "PHP", "POP", "preg_match", "rot23"]
difficulty: medium
source: "https://www.ctfiot.com/139097.html"
tools: ["PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届香山杯网络安全大赛初赛 Writeup

> 赛事：香山杯 2022 | 方向：misc | 难度：medium | 工具：PHP、Python

## 一句话总结

香山杯初赛 4 题：PHP 反序列化 POP 链绕 preg_match + rot23 + 内存 dump ou.exe + Chaquopy XXTEA 9 round。

## 攻击链

1. Web PHP_unserialize_pro: Welcome.__destruct (name=''A_G00d_H4ck3r'') → echo arg → H4ck3r.__toString → $func() → G00d.__invoke
2. 绕 preg_match ''/f|l|a|g|*|?/i'': system(''sort /[!q]1[!q][!q]'') 或 strtolower
3. MISC 签到: base64 解一次 + rot13 + rot23 = iodj{zh1f0p3_2_Fwi}
4. RE URL从哪儿来: 32位无壳, 动调从内存导出 ou.exe, 再 base64 解密
5. RE hello_py: Chaquopy 技术调用 Python, 提取 hello.py (XXTEA 变种)
6. 加密算法: encrypt(n, v, key), delta=0x9e3779b9, rounds=6+52//n, MX 函数 4 参数
7. 密钥: key_str = [689085350, 626885696, 1894439255, 1204672445, 1869189675, 475967424, 1932042439, 1280104741, 2808893494]
8. 逆: decrypt(9, v, key) 还原 9 个 uint32 → struct >I 8 字节打包 → flag

## 关键 payload

```
Welcome->H4ck3r->G00d sort /[!q]1[!q][!q] + Chaquopy hello.py + XXTEA-like 9 round
```

## 经验教训

PHP 反序列化 __destruct→__toString→__invoke 经典 POP 链；preg_match 黑名单用 glob 字符类 [!q] 绕；Chaquopy 嵌入式 Python 调用。

## 标签

PHP-unserialize、POP-chain、__destruct、__toString、__invoke、preg_match-bypass、ChaCha20-RC4、Chaquopy、XXTEA、in-memory-dump

## 参考来源

- https://www.ctfiot.com/139097.html
- 原文件：第三届“香山杯“网络安全大赛初赛Writeup.full.md

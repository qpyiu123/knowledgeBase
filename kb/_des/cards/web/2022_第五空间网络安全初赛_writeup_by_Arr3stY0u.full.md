---
title: "2022 第五空间网络安全初赛 WriteUp by Arr3stY0u"
category: web
tags: ["第五空间 2022", "web", "phar反序列化", "任意文件读取", "rootfs.img", "crackme"]
signals: ["第五空间 2022 2022", "phar反序列化", "任意文件读取", "rootfs.img", "crackme", "z3约束求解", "多字节异或", "safevm", "deserialize", "phar", "rootfs", "SMC", "file_exist", "img_name"]
difficulty: medium
source: "https://www.ctfiot.com/57918.html"
tools: ["IDA", "Z3", "binwalk"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 第五空间网络安全初赛 WriteUp by Arr3stY0u

> 赛事：第五空间 2022 2022 | 方向：web | 难度：medium | 工具：IDA、Z3、binwalk

## 一句话总结

5 题：phar反序列化、rootfs crackme z3 求解、SMC 多字节异或、safevm 未完成。

## 攻击链

1. file_exist(img_name) 触发 phar:// 反序列化
2. 生成 upload 类 phar 包改 png 后缀上传
3. 触发 __wakeup 调用 file_get_contents(/flag) 输出
4. binwalk -Me rootfs.img 拆 mips 路由器文件系统
5. 读 /bin/crackme + /etc/config
6. IDA 重命名 seg000 + 用 ida_bytes.patch_dword 调偏移
7. 用 z3 求解 16 字节输入满足 dword_422000 16 个线性方程
8. 多次 Sbox 替换 (Fun_0x7 ~ Fun_0x1d) 还原 flag
9. safevm 远端偏移量不同（未完成）

## 关键 payload

```
phar://upload/phar.png
```

## 经验教训

phar 触发链 = 上传 phar 改 png 后缀 + file_exist 触发；crackme 远端偏移和本地不同是常见坑。

## 标签

phar反序列化、任意文件读取、rootfs.img、crackme、z3约束求解、多字节异或、safevm

## 参考来源

- https://www.ctfiot.com/57918.html
- 原文件：2022_第五空间网络安全初赛_writeup_by_Arr3stY0u.full.md

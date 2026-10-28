---
title: "2025 强网杯 WriteUp By N0wayBack（招新+多 pwn/reverse/web）"
category: pwn
tags: ["2025 强网杯", "pwn", "N0wayBack 战队招新 cainyzb@qq.com", "Java Runtime.exec bash base64", "timestamp[year] PHP 反序列化+文件包含", "XSLT TemplatesImpl 内存马"]
signals: ["2025 强网杯 2025", "N0wayBack 战队招新 cainyzb@qq.com", "Java Runtime.exec bash base64", "timestamp[year] PHP 反序列化+文件包含", "XSLT TemplatesImpl 内存马", "OGNL systemProperties user.home", "MMXEncode packed_decrypt (sub-key+rotate+swap)", "butterfly_mmx_encode", "custom VM dumpmem cap+keystone 重定位", "deserialize", "reverse", "ssti", "N0wayBack", "Java"]
difficulty: hard
source: "https://www.ctfiot.com/275191.html"
tools: ["Java", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 强网杯 WriteUp By N0wayBack（招新+多 pwn/reverse/web）

> 赛事：2025 强网杯 2025 | 方向：pwn | 难度：hard | 工具：Java、PHP

## 一句话总结

2025 强网杯 N0wayBack 招新+综合：Java XSLT 内存马 + PHP timestamp 反序列化 + OGNL + 自定义 VM 反编译 + MMXEncode packed_decrypt。

## 攻击链

1. Java 反序列化 XSLT payload → TemplatesImpl 内存马
2. PHP /api.php timestamp[year] 反序列化文件包含
3. OGNL /check?rule=#{#systemProperties['user.home']=='/tmp'}
4. Pwn: %9$p-%12$s 格式化串泄栈 + heap 环境变量拿 shell
5. Reverse: custom VM dumpmem + capstone + keystone 重定位
6. MMXEncode: packed_decrypt = (x - key)→rotate_right_1→swap_2→xor_key

## 关键 payload

```
packed_decrypt: x[i]=(x[i]-key[i])&0xff; x=rotate_right_1; swap_2; x[i]^=key[i]
```

## 经验教训

自定义 VM 逆向套路 = 0x606AC0 结构体数组 + dfs topo 排序 + capstone/keystone 重定位；MMXEncode packed_decrypt = 减 key → 循环右移 1 → 2 字节交换 → xor key 4 步组合。

## 标签

N0wayBack 战队招新 cainyzb@qq.com、Java Runtime.exec bash base64、timestamp[year] PHP 反序列化+文件包含、XSLT TemplatesImpl 内存马、OGNL systemProperties user.home、MMXEncode packed_decrypt (sub-key+rotate+swap)、butterfly_mmx_encode、custom VM dumpmem cap+keystone 重定位

## 参考来源

- https://www.ctfiot.com/275191.html
- 原文件：2025-强网杯-WriteUp_By_N0wayBack.full.md

---
title: "强网杯S9 Real World monotint - V8 CVE-2024-12695 FinalizationRegistry利用"
category: web
tags: ["强网杯S9线下赛", "web", "V8", "CVE-2024-12695", "FinalizationRegistry", "unregister_token"]
signals: ["强网杯S9线下赛 2025", "V8", "CVE-2024-12695", "FinalizationRegistry", "unregister_token", "Object.assign", "Object.builtins", "JSWeakRef", "SimpleNumberDictionary", "web_unknown", "Real", "World", "monotint", "x300R"]
difficulty: hard
source: "https://www.ctfiot.com/295025.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯S9 Real World monotint - V8 CVE-2024-12695 FinalizationRegistry利用

> 赛事：强网杯S9线下赛 2025 | 方向：web | 难度：hard

## 一句话总结

强网杯S9 Real World monotint:0x300R浏览器nday CVE-2024-12695 V8 FinalizationRegistry越界写到沙箱逃逸弹计算器。

## 攻击链

1. patch V8 src/builtins/builtins-object-gen.cc删ObjectAssign properties hash check + js-weak-refs.cc CHECK→DCHECK → 0x300R monotint浏览器nday → 适配CVE-2024-12695 → 编译chromium 139.0.7258.128 v8_enable_sandbox=false → registry.register触发unregister_token hash生成 → Object.assign覆盖properties → 越界写入victim_arr → corrupt_obj_get_hash预测hash → construct_oob_arr用register触发地址预测写key_list_prev → 错位字节resize构造稳定OOB → cage_read/cage_write实现addrof+AAR+AW → 沙箱逃逸到gnome-calculator弹计算器

## 关键 payload

```
Object.assign绕过properties hash check + SimpleNumberDictionary越界写 + 错位字节resize + V8 sandbox escape
```

## 经验教训

V8 FinalizationRegistry + Object.assign组合漏洞:unregister_token在register时分配hash,Object.assign会覆盖properties指向PropertyArray绕过hash check;SimpleNumberDictionary越界写可破坏OOB arr;CVE-2024-12695需patch ObjectAssign+JSFinalizationRegistry::RemoveCellFromUnregisterToken;V8 sandbox逃逸用cage_read/cage_write稳定原语;浏览器nday完整利用链:patch+编译+JS+escape。

## 标签

V8、CVE-2024-12695、FinalizationRegistry、unregister_token、Object.assign、Object.builtins、JSWeakRef、SimpleNumberDictionary、OOB_arr、越界写、浏览器沙箱逃逸、hash_map、register/weak_cell、addrof、AAR、AW、0x300R、monotint、chromium_no_sandbox

## 参考来源

- https://www.ctfiot.com/295025.html
- 原文件：强网杯S9_Real_World_–_monotint.full.md

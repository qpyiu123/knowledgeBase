---
title: "嘉新杯部分wp"
category: crypto
tags: ["恒安嘉新杯 / EasyAES + 失窃的工艺", "crypto", "EasyAES", "4层CBC", "双重爆破", "SHA-256 key派生"]
signals: ["恒安嘉新杯 / EasyAES + 失窃的工艺 2025", "EasyAES", "4层CBC", "双重爆破", "SHA-256 key派生", "OTA流量分析", "晨星安全团队", "Zion_Cat", "crypto_oracle", "CBC", "OTA", "session_key", "AES-CBC", "hex"]
difficulty: medium
source: "https://www.ctfiot.com/271379.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 嘉新杯部分wp

> 赛事：恒安嘉新杯 / EasyAES + 失窃的工艺 2025 | 方向：crypto | 难度：medium

## 一句话总结

嘉新杯 2 题：EasyAES 4 层 CBC 双重爆破 + 失窃的工艺 OTA 流量分析 session_key 解密。

## 攻击链

1. 题1 EasyAES: 4 层 AES-CBC 加密
2. c3 (密文 hex 192 字节) → 3 次 unpad + decrypt 得 c0
3. part2 (3 字符 ascii_letters+digits) SHA-256 派生 key1
4. 解 c3 → c2 → c1 → c0 (需要 valid_padding 检查)
5. part1 (3 字符) SHA-256 派生 key0, 解 c0 → flag (36 字符 + 4 横线)
6. flag 格式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
7. 题2 失窃的工艺: OTA 流量分析
8. hello 消息找到 session_key + vehicle_type + 密文
9. session_key: b908232bfa70d5c3060dd2f96b36a7fc8199e18ef1b3c509efe4a86bf9339d90
10. ALTaXk84WULvUwvHHoKpDlmW8PKnKIhyCZVl3kiI4Kca1NgiZDbUt6O6H1OAsZvUX7FyZsgjRJLolAEBnp0Lpg==

## 关键 payload

```
4 层 AES-CBC + part1+part2 SHA-256 派生 key + flag UUID 格式
```

## 经验教训

多层 AES-CBC 加密需要 valid_padding 检查 + unpad 逐层验证; SHA-256 短 key 派生可爆破 (3 字符 62^3 = 238k); OTA 流量 first message 通常含 session_key。

## 标签

EasyAES、4层CBC、双重爆破、SHA-256 key派生、OTA流量分析、晨星安全团队、Zion_Cat

## 参考来源

- https://www.ctfiot.com/271379.html
- 原文件：嘉新杯部分wp.full.md

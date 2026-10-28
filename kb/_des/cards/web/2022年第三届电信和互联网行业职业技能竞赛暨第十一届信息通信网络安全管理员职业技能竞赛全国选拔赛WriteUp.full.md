---
title: "2022 年第三届电信和互联网行业职业技能竞赛 WriteUp"
category: web
tags: ["2022 电信/互联网行业职业技能竞赛", "web", "职业技能竞赛", "xor-0x70", "flag-reverse", "SilentEye"]
signals: ["2022 电信/互联网行业职业技能竞赛 2022", "职业技能竞赛", "xor-0x70", "flag-reverse", "SilentEye", "binwalk", "crc-collision", "ddddocr", "SQL-异或注入", "sqli", "deserialize", "reverse", "crypto_rsa", "xor"]
difficulty: medium
source: "https://www.ctfiot.com/61661.html"
tools: ["binwalk"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 年第三届电信和互联网行业职业技能竞赛 WriteUp

> 赛事：2022 电信/互联网行业职业技能竞赛 2022 | 方向：web | 难度：medium | 工具：binwalk

## 一句话总结

2022 电信职业技能赛：xor 0x70 + binwalk + CRC 碰撞 + ddddocr SQL 异或 + RSA

## 攻击链

1. PWN: 内联库函数, 调试器找 flag (无原文代码)
2. Reverse: 输入反转 + XOR 0x70 → 反转后 xor 0x70 还原
3. MISC 1: 1 进入 calc, print(eval(line)) 直接拿 key
4. MISC 2: __import__(''os'').popen(''cat flag'').read()
5. MISC 3: binwalk jpg → zip → CRC 碰撞密码 ohhhh_you_found_me → 解压 → base64 → 图片 SilentEye → flag
6. WEB func.php: ddddocr 识别验证码 + 异或 SQL 注入 1''^(ascii(substr(database(),{0},1))={1})^''1, 过滤 select, 改查 code 字段
7. WEB EzPop: POP 链构造
8. WEB 超级马里奥: js 藏 flag 路径
9. Crypto: 爆破 X0=4/5 → 恢复 key → 解密第一段 → 作 key 解密第二段
10. Crypto old_rsa: 费马小定理分解 modulus = s, p,q 关系 n/s 开根, 解 rsa

## 关键 payload

```
1'^(ascii(substr(database(),{0},1))={1})^'1
```

## 经验教训

异或 SQL 注入绕过关键字是经典；CRC 碰撞短文件名密码是 misc 入门；费马小定理分解 RSA

## 标签

职业技能竞赛、xor-0x70、flag-reverse、SilentEye、binwalk、crc-collision、ddddocr、SQL-异或注入、费马小定理、临时密钥重用

## 参考来源

- https://www.ctfiot.com/61661.html
- 原文件：2022年第三届电信和互联网行业职业技能竞赛暨第十一届信息通信网络安全管理员职业技能竞赛全国选拔赛WriteUp.full.md

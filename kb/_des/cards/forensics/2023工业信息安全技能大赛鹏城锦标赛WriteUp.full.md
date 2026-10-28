---
title: "2023 工业信息安全技能大赛鹏城锦标赛 WriteUp"
category: forensics
tags: ["2023 工业信息安全技能大赛鹏城锦标赛", "forensics", "IEC_60870-5_104", "CAN_15765", "ICMP流量", "SMC_TEA变种"]
signals: ["2023 工业信息安全技能大赛鹏城锦标赛 2023", "IEC_60870-5_104", "CAN_15765", "ICMP流量", "SMC_TEA变种", "AES_ECB", "PEM手撕", "Wiener攻击", "factorDB", "forensic_disk", "IEC104", "CAN", "ICMP", "SMC"]
difficulty: hard
source: "https://www.ctfiot.com/139444.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 工业信息安全技能大赛鹏城锦标赛 WriteUp

> 赛事：2023 工业信息安全技能大赛鹏城锦标赛 2023 | 方向：forensics | 难度：hard

## 一句话总结

工业信息安全综合：IEC104 + CAN + ICMP 隐写 + SMC TEA 变种 + AES + 手撕 PEM RSA。

## 攻击链

1. 工控-Welcome: IEC 60870-5 流量追踪异常 base64 解密 flag{sign_in_successfully!}
2. 解 Hex0 + Base64 + 键盘密码
3. CAN 包 ISO 15765 解析 ID=730，拼接导出二进制
4. strings 找假 flag，反编译 pyc 反写 decode
5. 源码逆向，每条 ICMP data 长度转 ASCII（192.168.3.73 源）
6. 去除花指令 + SMC TEA 变种 (delta=0x11451419, 移位改了)
7. idapython 还原 sub_2DB7 AES+hex 加密
8. AES-ECB (key=rGzuwTc31NRH9tsT) 解密 flag
9. RSA: 手撕 PEM 拿 N，factorDB 分解找 p,q
10. RsaCtfTool issue #304 找 e，Wiener 攻击兜底

## 关键 payload

```
key = rGzuwTc31NRH9tsT, n = 460657813884289609896372056585544172485318117026246263899744329237492701820627219556007788200590119136173895989001382151536006853823326382892363143604314518686388786002989248800814861248595075326277099645338694977097459168530898776007293695728101976069423971696524237755227187061418202849911479124793990722597
```

## 经验教训

PEM corrupt 时手撕结构体；SMC TEA 变种要看 delta 和移位；Wiener 攻击是大 e RSA 兜底。

## 标签

IEC_60870-5_104、CAN_15765、ICMP流量、SMC_TEA变种、AES_ECB、PEM手撕、Wiener攻击、factorDB、RsaCtfTool

## 参考来源

- https://www.ctfiot.com/139444.html
- 原文件：2023工业信息安全技能大赛鹏城锦标赛WriteUp.full.md

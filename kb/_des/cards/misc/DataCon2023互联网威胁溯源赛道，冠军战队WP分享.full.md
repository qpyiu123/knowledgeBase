---
title: "DataCon2023互联网威胁溯源赛道，冠军战队WP分享"
category: misc
tags: ["DataCon 2023", "misc", "threat-hunting", "ddos", "ntp-flood", "slow-http"]
signals: ["DataCon 2023 2023", "threat-hunting", "ddos", "ntp-flood", "slow-http", "botnet", "p2p", "c2", "aes-ecb", "misc_unknown", "DataCon2023", "DDoS", "AES-ECB", "NTP"]
difficulty: hard
source: "https://www.ctfiot.com/150471.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2023互联网威胁溯源赛道，冠军战队WP分享

> 赛事：DataCon 2023 2023 | 方向：misc | 难度：hard

## 一句话总结

DataCon2023威胁溯源：DDoS分类+僵尸机IP+窃密AES-ECB流量

## 攻击链

1. DDoS 5种：NTP(100源)+UDP(100)+SYN(200)+慢速header(50)+慢速payload(50)
2. 慢速http双向握手→僵尸机真实IP
3. 102.33.5.89跳板机+83.250.118.40被控主机+koko运行
4. 106.167.202.117+104.54.45.183 P2P僵尸节点+SSH爆破
5. AES-ECB窃密流量：16字节分组+全0段+相同明文密文相同
6. 配置文件：root/tsgoingon admin/admin123
7. 加密配置解密→C2 NODE_IP

## 关键 payload

```
MON_GETLIST字段是NTP反射放大攻击标志
```

## 经验教训

慢速http双向握手IP是真实僵尸机；P2P节点IP=僵尸IP

## 标签

threat-hunting、ddos、ntp-flood、slow-http、botnet、p2p、c2、aes-ecb、ptrace

## 参考来源

- https://www.ctfiot.com/150471.html
- 原文件：DataCon2023互联网威胁溯源赛道，冠军战队WP分享.full.md

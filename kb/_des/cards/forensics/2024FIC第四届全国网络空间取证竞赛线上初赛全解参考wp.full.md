---
title: "2024 FIC 第四届全国网络空间取证竞赛 初赛 WP"
category: forensics
tags: ["第四届全国网络空间取证竞赛 (FIC 2024)", "forensics", "杀猪盘", "ESXi", "vmdk", "Docker"]
signals: ["第四届全国网络空间取证竞赛 (FIC 2024) 2024", "杀猪盘", "ESXi", "vmdk", "Docker", "MySQL", "若依", "RuoYi", "jar-反编译", "forensic_disk", "forensic_memory", "misc_unknown", "esxcfg-volume", "wxid"]
difficulty: hard
source: "https://www.ctfiot.com/176442.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 FIC 第四届全国网络空间取证竞赛 初赛 WP

> 赛事：第四届全国网络空间取证竞赛 (FIC 2024) 2024 | 方向：forensics | 难度：hard

## 一句话总结

杀猪盘综合取证：手机+服务器+PC 三检材联动

## 攻击链

1. 案：卢某被'杀猪盘'诈骗 → 查李某手机(检材1) + 服务器(检材2) + 赵某PC(检材3)
2. ESXi vmdk esxcfg-volume -l 挂载
3. 微信 wxid 提取 → 赌博群 URL http://www.honglian7001.com/down
4. 服务器扫 192.168.110.110:8000/login + 密码 limoon890
5. docker inspect 9b 看 MYSQL_ROOT_PASSWORD
6. ruoyi-admin.jar 解压改 application-druid.yml 启动 /api/shopOrder
7. iStoreOS OpenWrt NasTools PassWall2 → token 订阅地址
8. TrueCrypt 卷密码 qwerasdfzxcv
9. 火眼鲁盒 dst01.jpeg 镜像 0.85 缩放

## 关键 payload

```
ruoyi-admin.jar BOOT-INF/classes/application-druid.yml → MYSQL_ROOT_PASSWORD=my-secret-pw
```

## 经验教训

综合取证赛三大类：微信/QQ 聊天记录；ESXi/Docker 容器部署链路；加密卷密码与镜像；iStoreOS 软路由+订阅 token

## 标签

杀猪盘、ESXi、vmdk、Docker、MySQL、若依、RuoYi、jar-反编译、vmdk挂载、微信取证、iStoreOS、OpenWrt、NasTools、鲁盒

## 参考来源

- https://www.ctfiot.com/176442.html
- 原文件：2024FIC第四届全国网络空间取证竞赛线上初赛全解参考wp.full.md

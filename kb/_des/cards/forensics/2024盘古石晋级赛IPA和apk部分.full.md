---
title: "2024 盘古石晋级赛 IPA 和 APK 部分（iOS + Android 取证）"
category: forensics
tags: ["2024 盘古石晋级赛", "forensics", "iOS IPA 毛雪柳手机取证", "iCost 记账 APP default.realm Realm 数据库", "Mattermost 内部 IM", "base.apk 伏季雅手机"]
signals: ["2024 盘古石晋级赛 2024", "iOS IPA 毛雪柳手机取证", "iCost 记账 APP default.realm Realm 数据库", "Mattermost 内部 IM", "base.apk 伏季雅手机", "威尼斯诈骗 APP", "w2a.W2Ah5.jsgjzfx.org.cn 包名", "__W2A__h5.jsgjzfx.org.cn 打包 ID", "io.dcloud.PandoraEntry 启动项", "forensic_disk", "misc_unknown", "iOS", "iCost", "Mattermost"]
difficulty: medium
source: "https://www.ctfiot.com/183403.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 盘古石晋级赛 IPA 和 APK 部分（iOS + Android 取证）

> 赛事：2024 盘古石晋级赛 2024 | 方向：forensics | 难度：medium

## 一句话总结

盘古石晋级赛：iOS 毛雪柳记账 iCost+ Mattermost + Android 伏季雅威尼斯诈骗 APP + 义言 Mattermost 多检材协同；雷电 APP 智能分析一键导出 base.apk 元数据。

## 攻击链

1. 毛雪柳 iOS: iCost 记账 APP Documents/default.realm → realm 数据库
2. 2 月收入 9600+2357=11957 元
3. Mattermost IM 共享目录 /private/var/mobile/Containers/Shared/AppGroup/BBE0D501-AB0B-422E-9B4D-02E2D86130D4
4. gxyt 老板 user_id=enf863dp1ifi3ffos7bpduynny + gxyt@163.com
5. 私聊频道 "发财" 加入时间 1713931168391 → 2024-04-24-11-59-28
6. 老板最后发送时间 1714011890182 → 2024-04-25-10-24-50
7. 伏季雅 Android: 诈骗 APP 威尼斯，包名 w2a.W2Ah5.jsgjzfx.org.cn
8. 服务器 192.168.137.125 + 打包 ID __W2A__h5.jsgjzfx.org.cn + 启动 io.dcloud.PandoraEntry
9. 义言手机 Mattermost app.db 服务器 192.168.137.97
10. 数据库名 aHR0cDovLzE5Mi4xNjguMTM3Ljk3OjgwNjU=.db

## 关键 payload

```
iCost APP default.realm + realm studio 2 月 type=1 收入 11957
```

## 经验教训

iOS 取证从 iTunes 备份 + 雷电 APP 分析 + realm studio 看 realm 数据库是 2024 主流流程；Mattermost 数据库名 = base64(URL).db 是反取证隐藏套路；雷电模拟器自带 APP 智能分析比 jadx 快很多。

## 标签

iOS IPA 毛雪柳手机取证、iCost 记账 APP default.realm Realm 数据库、Mattermost 内部 IM、base.apk 伏季雅手机、威尼斯诈骗 APP、w2a.W2Ah5.jsgjzfx.org.cn 包名、__W2A__h5.jsgjzfx.org.cn 打包 ID、io.dcloud.PandoraEntry 启动项、雷电 APP 智能分析、app.db Mattermost

## 参考来源

- https://www.ctfiot.com/183403.html
- 原文件：2024盘古石晋级赛IPA和apk部分.full.md

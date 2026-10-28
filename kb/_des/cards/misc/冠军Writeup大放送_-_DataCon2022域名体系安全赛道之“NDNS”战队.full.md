---
title: "冠军Writeup大放送 | DataCon2022域名体系安全赛道之\"NDNS\"战队"
category: misc
tags: ["DataCon2022 域名体系安全", "misc", "DataCon", "域名分类", "CDN", "动态域名"]
signals: ["DataCon2022 域名体系安全 2022", "DataCon", "域名分类", "CDN", "动态域名", "Sinkhole", "Domain Parking", "Webhosting", "FastFlux", "misc_unknown", "DataCon2022", "NDNS", "CNAME", "TXT"]
difficulty: hard
source: "https://www.ctfiot.com/92019.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 冠军Writeup大放送 | DataCon2022域名体系安全赛道之"NDNS"战队

> 赛事：DataCon2022 域名体系安全 2022 | 方向：misc | 难度：hard

## 一句话总结

DataCon2022 域名体系安全冠军 NDNS：8 类域名分类判定指标 + 5 关域名接管 (CNAME + TXT 归属权验证)。

## 攻击链

1. 国防科技大学 NDNS 战队 (DNSLab) 域名体系安全冠军
2. 域名分类: 8 类 (CDN/动态/隐藏/Sinkhole/Parking/Webhosting/p2p/FastFlux)
3. CDN 特征: 大量 CNAME, SLD FQDN 多, IP 数量多分布广
4. 判定: SLD CNAME > 100, IP 地理位置数 > 0/2 (得分 100/22)
5. 隐藏域名 (GFW): IP ASO 集中 (Google/Twitter/Facebook/Dropbox), IP 解析 > 14W
6. 动态域名: 花生壳/3322/dnspod/aliyun/huaweicloud
7. Sinkhole: NS 改研究者控制 DNS, IP 集中
8. Domain Parking: 停放服务商 Sedo/Bodis/IONOS
9. Webhosting: 000Webhost/Wix.com/Squarespace
10. FastFlux: storm worm 2006, 频繁换 IP/NS
11. 域名接管 level1-5: CNAME 注销 + TXT 归属权验证
12. level1: 无验证直接接管
13. level2-5: TXT 记录/文件/API 验证差异化

## 关键 payload

```
CDN CNAME>100 + GFW ASO+14W + 域名接管 CNAME/TXT
```

## 经验教训

CDN 域名为厂商 SLD 下的 CNAME 链 (如 admin.datacon.cdn.)；GFW 隐藏域名 IP ASO 集中 (Google/Twitter/Facebook) 解析 >14W；域名接管是 CNAME 注销 + TXT 验证绕过。

## 标签

DataCon、域名分类、CDN、动态域名、Sinkhole、Domain Parking、Webhosting、FastFlux、域名接管、CNAME、TXT归属权、DNSSEC、DMARC

## 参考来源

- https://www.ctfiot.com/92019.html
- 原文件：冠军Writeup大放送_-_DataCon2022域名体系安全赛道之“NDNS”战队.full.md

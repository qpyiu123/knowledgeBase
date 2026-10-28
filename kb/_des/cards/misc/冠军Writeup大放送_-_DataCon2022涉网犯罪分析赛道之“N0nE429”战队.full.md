---
title: "冠军Writeup大放送 | DataCon2022涉网犯罪分析赛道之\"N0nE429\"战队"
category: misc
tags: ["DataCon2022 涉网犯罪分析", "misc", "DataCon", "攻击者画像", "同源关联", "风险评级"]
signals: ["DataCon2022 涉网犯罪分析 2022", "DataCon", "攻击者画像", "同源关联", "风险评级", "Mirai样本", "IOC提取", "signal函数", "resolve_cnc_addr", "misc_unknown", "DataCon2022", "N0nE429", "WAF", "frame-tag"]
difficulty: hard
source: "https://www.ctfiot.com/91525.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 冠军Writeup大放送 | DataCon2022涉网犯罪分析赛道之"N0nE429"战队

> 赛事：DataCon2022 涉网犯罪分析 2022 | 方向：misc | 难度：hard

## 一句话总结

DataCon2022 涉网犯罪分析冠军 N0nE429：WAF 日志+frame-tag 攻击者画像+同源关联 + Mirai IOC 自动化提取。

## 攻击链

1. 武汉大学 N0nE429 战队 (JackNoire/Jiryu/Scorpion) 师从傅建明
2. 攻击者画像 6 类: 安全公司/非恶意互联网应用/僵尸网络/白帽黑客/雇佣黑客/未知
3. 风险评级 6 档: 基本可信/低风险/中风险/中高风险/高风险/特殊
4. 数据源: attack-log (WAF web 告警) + frame-tag (IP属性/DNS/hack-tool)
5. MongoDB 存储 (记录长度受限, 略大文件单独处理)
6. 冬奥 2.4-2.20 期间 602 个 IP 切片
7. 指标: is_dangerous/is_proxy/is_gateway/is_tor/is_gov_targeted/has_webshell/has_hacktool
8. 同源: 相同风险+相同身份+IP 主机号接近
9. Mirai IOC: idapython 定位 main → signal(SIGTRAP=5, &anti_gdb_entry)
10. resolve_cnc_addr 三种形式: 直接赋值/字符串传参/table 加密
11. table 加密: TABLE_CNC_DOMAIN/TABLE_CNC_PORT → table_retrieve_val
12. 加密函数: 统计 logic 7-9 + airthmetic 2-4 指令

## 关键 payload

```
攻击者画像 6 类+评级 6 档 + Mirai IOC 自动化提取 (idapython)
```

## 经验教训

攻击者画像核心是建立指标体系 (is_dangerous/is_proxy/is_gov_targeted 等)；Mirai 反编译定位 main→signal(SIGTRAP)→anti_gdb_entry→resolve_cnc_addr→table 加密是自动化 IOC 提取关键链。

## 标签

DataCon、攻击者画像、同源关联、风险评级、Mirai样本、IOC提取、signal函数、resolve_cnc_addr、table加密、MongoDB

## 参考来源

- https://www.ctfiot.com/91525.html
- 原文件：冠军Writeup大放送_-_DataCon2022涉网犯罪分析赛道之“N0nE429”战队.full.md

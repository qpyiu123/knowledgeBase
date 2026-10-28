---
title: "记一次用 AI 打比赛"
category: misc
tags: ["BlockHarbor 比赛", "misc", "AI-assisted", "CAN-bus", "UDS", "caringcaribou"]
signals: ["BlockHarbor 比赛 2025", "AI-assisted", "CAN-bus", "UDS", "caringcaribou", "automotive-security", "RDBI-dump", "security-access", "seed-answer", "misc_unknown", "BlockHarbor", "RDBI", "dump", "Security"]
difficulty: medium
source: "https://www.ctfiot.com/267997.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 记一次用 AI 打比赛

> 赛事：BlockHarbor 比赛 2025 | 方向：misc | 难度：medium | 工具：C

## 一句话总结

BlockHarbor汽车安全比赛AI辅助WP,涵盖caringcaribou UDS RDBI dump+Security Access算法逆向+CAN日志固件重建+seed→key计算,rockyou.txt爆破压缩包密码。

## 攻击链

1. 题目1AutoGraph: RAMN ECU B和C的caringcaribou UDS RDBI dump日志+签名固件,提示flag是十进制secret key
2. 用rockyou.txt爆破压缩包密码(字母+数字爆不出来)
3. 从candump日志重建完整固件+识别Security Access算法
4. ECU C给出seed 9A5ABF0C1CAAFDEB72761E909501D6E9,求answer(32位hex大写)
5. 题目2ECU C: SecurityAccess算法逆向,seed→key计算
6. flag是十进制格式的secret key

## 关键 payload

```
32位hex大写answer
```

## 经验教训

汽车安全比赛常考UDS(统一诊断服务)+CAN总线+caringcaribou工具;SecurityAccess算法(Seed→Key)需要逆向固件提取;rockyou.txt是国外比赛压缩包密码首选字典。

## 标签

AI-assisted、CAN-bus、UDS、caringcaribou、automotive-security、RDBI-dump、security-access、seed-answer、firmware-signing、rockyou

## 参考来源

- https://www.ctfiot.com/267997.html
- 原文件：记一次用_AI_打比赛.full.md

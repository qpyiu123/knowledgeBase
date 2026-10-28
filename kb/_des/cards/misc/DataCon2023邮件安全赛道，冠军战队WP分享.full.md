---
title: "DataCon2023邮件安全赛道，冠军战队WP分享"
category: misc
tags: ["DataCon 2023", "misc", "phishing", "spam", "email", "url"]
signals: ["DataCon 2023 2023", "phishing", "spam", "email", "url", "ocr", "qrcode", "threat-intel", "tranco-top1m", "misc_unknown", "DataCon2023"]
difficulty: hard
source: "https://www.ctfiot.com/149890.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2023邮件安全赛道，冠军战队WP分享

> 赛事：DataCon 2023 2023 | 方向：misc | 难度：hard

## 一句话总结

DataCon2023邮件安全：4类邮件分类+钓鱼特征工程+邮件炸弹攻击

## 攻击链

1. 邮件分类4类：正常/垃圾/钓鱼/误报
2. 训练集4277封含垃圾+钓鱼各半
3. 6大主题分类：金钱补助/软件更新/科研培训/广告营销/色情/开票开户
4. 关键词黑名单+通配符匹配（中间截断/谐音/近形字）
5. URL白名单：Tranco TOP1M域名匹配
6. 附件检测：合法后缀白名单
7. 内联图片：仅含图片无文本→钓鱼
8. 邮件炸弹：2小时内大量发送

## 关键 payload

```
关键词黑名单+Tranco TOP1M域名白名单+内联图片特征
```

## 经验教训

钓鱼邮件检测特征工程：关键词黑白名单+URL白名单+附件+内联图

## 标签

phishing、spam、email、url、ocr、qrcode、threat-intel、tranco-top1m、mail-bomb

## 参考来源

- https://www.ctfiot.com/149890.html
- 原文件：DataCon2023邮件安全赛道，冠军战队WP分享.full.md

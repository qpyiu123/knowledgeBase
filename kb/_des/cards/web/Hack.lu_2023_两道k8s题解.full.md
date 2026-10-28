---
title: "Hack.lu 2023 两道k8s题解"
category: web
tags: ["Hack.lu 2023", "web", "k8s", "kubernetes", "crd", "operator"]
signals: ["Hack.lu 2023 2023", "k8s", "kubernetes", "crd", "operator", "flagrequest", "anti-bruteforce", "watch", "web_unknown", "Hack", "K8s", "CRD", "Flagrequest", "token"]
difficulty: hard
source: "https://www.ctfiot.com/138920.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hack.lu 2023 两道k8s题解

> 赛事：Hack.lu 2023 2023 | 方向：web | 难度：hard | 工具：Python

## 一句话总结

Hack.lu 2023 K8s：CRD Flagrequest+operator+anti-bruteforce token

## 攻击链

1. 题目：两个 K8s 题目涉及 CRD
2. Flagrequest CRD + Flagprotector CRD
3. 创建 name=give-flag Flagrequest
4. 必须含 hack.lu/challenge-name 标签
5. spec.anti-bruteforce = "Bi$wmX4PBTQLGe%AIKPO19$ussap4w
6. Kubernetes Python operator 监听 watch
7. 删除 flagprotector CRD（不删除则被拒）
8. 创建合法 Flagrequest
9. Operator 创建 Flag CRD 返回 flag

## 关键 payload

```
metadata.name=give-flag + labels.hack.lu/challenge-name=give-flag + spec.anti-bruteforce=Bi$wmX4PBTQLGe%AIKPO19$ussap4w
```

## 经验教训

K8s CRD challenge常需理解operator watch流程+反token条件

## 标签

k8s、kubernetes、crd、operator、flagrequest、anti-bruteforce、watch

## 参考来源

- https://www.ctfiot.com/138920.html
- 原文件：Hack.lu_2023_两道k8s题解.full.md

---
title: "42 个 TanStack 包遭供应链劫持：6 分钟植入 84 个恶意版本"
category: misc
tags: ["供应链安全", "misc", "供应链劫持", "TanStack", "pull_request_target", "Pwn Request"]
signals: ["供应链安全 2026", "供应链劫持", "TanStack", "pull_request_target", "Pwn Request", "GitHub Actions缓存中毒", "OIDC令牌内存提取", "T1199", "T1071.001", "misc_unknown", "Pwn", "Request", "Actions", "OIDC"]
difficulty: medium
source: "https://www.ctfiot.com/307893.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 42 个 TanStack 包遭供应链劫持：6 分钟植入 84 个恶意版本

> 赛事：供应链安全 2026 | 方向：misc | 难度：medium

## 一句话总结

TanStack 供应链劫持复盘 — Pwn Request + Actions 缓存中毒 + OIDC 内存提取 + P2P 信使 + 6分钟植入 84 个恶意版本，覆盖 npm+PyPI 多平台。

## 攻击链

1. 初始访问: pull_request_target "Pwn Request" 模式 (T1199)
2. 持久化: GitHub Actions 缓存中毒 (T1090.003)
3. 凭证窃取: OIDC 令牌从进程内存提取 (T1003.003)
4. 远程控制: 远程 dispatch 行为 (T1071.001)
5. 拼写错误域名: git-tanstack[.]com (c 替换)
6. 会话信使网络: P2P 加密流量伪装
7. GitHub API 死信: 令牌上传至新建仓库
8. 数据隐匿于合法流量
9. 6 分钟植入 84 个恶意版本到 42 个 @tanstack/* 包
10. 1200 万次/周下载量

## 关键 payload

```
Pwn Request / Actions 缓存 / OIDC 内存提取 / git-tanstack.com / P2P 信使 / 84 恶意版本 6 分钟 / 1200万次/周
```

## 经验教训

pull_request_target 是 CI 致命弱点（PR 触发可信工作流可读 secrets）；GitHub Actions 缓存是横向扩散温床；OIDC token 写内存不安全。

## 标签

供应链劫持、TanStack、pull_request_target、Pwn Request、GitHub Actions缓存中毒、OIDC令牌内存提取、T1199、T1071.001、T1003.003、T1090.003、T1552、T1070.004、git-tanstack.com拼写、P2P加密、GitHub API死信

## 参考来源

- https://www.ctfiot.com/307893.html
- 原文件：42个TanStack包遭供应链劫持：6分钟植入84个恶意版本.full.md

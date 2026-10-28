---
title: "【Hack The Box】PC【WriteUp】"
category: web
tags: ["HackTheBox", "web", "rustscan", "nmap", "gRPC", "grpcurl"]
signals: ["HackTheBox 2023", "rustscan", "nmap", "gRPC", "grpcurl", "evans", "proto-reflection", "SimpleApp", "pyload", "web_unknown", "Hack", "Box", "LoginUser", "SSH"]
difficulty: medium
source: "https://www.ctfiot.com/136588.html"
tools: ["Python", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【Hack The Box】PC【WriteUp】

> 赛事：HackTheBox 2023 | 方向：web | 难度：medium | 工具：Python、nmap

## 一句话总结

Hack The Box PC 题，gRPC 50051 端口反射枚举 + LoginUser 用户枚举 + pyload SSH 登录。

## 攻击链

1. rustscan --top --ulimit 1500 扫 22/50051/grpc.reflection.v1alpha 服务 list 拿 SimpleApp/evans 或 grpcurl 调 LoginUser 用户名密码（遍历）/get user id 后 pyload 上传文件走 SSH 公私钥登录 get shell

## 关键 payload

```
端口 22 + 50051 (gRPC)  SimpleApp.LoginUser  Python gRPC client
```

## 经验教训

rustscan 比 nmap 快的现代端口扫描器；gRPC 服务默认在 50051 端口，需用 grpcurl/evans 工具；grpc.reflection.v1alpha 反射服务可枚举所有方法和消息。

## 标签

rustscan、nmap、gRPC、grpcurl、evans、proto-reflection、SimpleApp、pyload、ssh-key、RCE、login-brute

## 参考来源

- https://www.ctfiot.com/136588.html
- 原文件：【Hack_The_Box】PC【WriteUp】.full.md

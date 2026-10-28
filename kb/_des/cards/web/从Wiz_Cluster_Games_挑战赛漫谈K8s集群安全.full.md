---
title: "从Wiz Cluster Games挑战赛漫谈K8s集群安全"
category: web
tags: ["Wiz EKS Cluster Games 2023", "web", "Kubernetes", "EKS", "RBAC", "IRSA"]
signals: ["Wiz EKS Cluster Games 2023 2023", "Kubernetes", "EKS", "RBAC", "IRSA", "imagePullSecrets", "ECR", "AWS", "OIDC", "auth_bypass", "Wiz", "secret", "IMDS", "AssumeRoleWithWebIdentity"]
difficulty: medium
source: "https://www.ctfiot.com/151534.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从Wiz Cluster Games挑战赛漫谈K8s集群安全

> 赛事：Wiz EKS Cluster Games 2023 2023 | 方向：web | 难度：medium

## 一句话总结

Wiz EKS 5 关云原生攻击链：RBAC 读 secret → imagePullSecrets 拉镜像 → IMDS 提 AWS 凭证 → ECR 历史泄密 → IRSA AssumeRoleWithWebIdentity 读 S3。

## 攻击链

1. Challenge 1: RBAC 仅给 secrets get/list → kubectl get secret log-rotate -o json base64 解码
2. Challenge 2: pods list/get → kubectl get pod database-pod-2c9b3a4e -o yaml 找 imagePullSecrets
3. 拿 registry-pull-secrets dockerconfigjson base64 解 crane auth login index.docker.io
4. crane pull eksclustergames/base_ext_image 提 layer tar 找 flag.txt
5. Challenge 3: ECR 镜像 401 → IMDS 169.254.169.254/latest/meta-data/iam/security-credentials 拿 ASIA 临时凭证
6. aws ecr get-login-password docker login 拉 central_repo-aaf4a7c 镜像
7. docker history --no-trunc 翻 RUN 层泄 ARTIFACTORY_TOKEN 拿到 flag
8. Challenge 4: SA challenge4 无权 → IMDS 拿 NodeInstanceRole
9. aws eks get-token 拿 ExecCredential token → kubectl --token 读 secrets node-flag
10. Challenge 5: SA debug-sa IRSA 绑 challengeEksS3Role → kubectl create token debug-sa
11. aws sts assume-role-with-webidentity 拿 STS 临时凭证
12. aws s3 cp s3://challenge-flag-bucket-3ff1ae2/flag 拿 flag

## 关键 payload

```
wiz_eks_challenge{*}
```

## 经验教训

K8s 攻击面按 RBAC→Secrets→IMDS→IRSA 层层升级；aws sts get-caller-identity 是验证当前凭证的快捷命令；service-account-token + OIDC 是 K8s 1.24+ 标准姿势。

## 标签

Kubernetes、EKS、RBAC、IRSA、imagePullSecrets、ECR、AWS、OIDC、service-account-token、云安全

## 参考来源

- https://www.ctfiot.com/151534.html
- 原文件：从Wiz_Cluster_Games_挑战赛漫谈K8s集群安全.full.md

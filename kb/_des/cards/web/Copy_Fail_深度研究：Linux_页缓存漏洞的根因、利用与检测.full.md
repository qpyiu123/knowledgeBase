---
title: "Copy Fail 深度研究：Linux 页缓存漏洞的根因、利用与检测"
category: web
tags: ["安全研究文章", "web", "kernel", "page-cache", "AF_ALG", "splice"]
signals: ["安全研究文章 2024", "kernel", "page-cache", "AF_ALG", "splice", "CVE", "container-escape", "authencesn", "esn", "web_unknown", "Linux", "page", "cache", "in-place"]
difficulty: hard
source: "https://www.ctfiot.com/307687.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Copy Fail 深度研究：Linux 页缓存漏洞的根因、利用与检测

> 赛事：安全研究文章 2024 | 方向：web | 难度：hard

## 一句话总结

Linux page cache写穿漏洞：AF_ALG+splice in-place污染只读文件

## 攻击链

1. 漏洞点：AF_ALG + splice in-place处理导致page cache被改
2. authencesn: AAD[4:8]临时写入scratch供HMAC
3. sendmsg发8字节AAD 4字节X填+4字节待写数据
4. splice从/usr/bin/su送t+4字节到AF_ALG socket
5. 多次调用覆盖ELF头部获得root shell
6. 同namespace容器共享镜像层page cache
7. Docker默认seccomp不阻止

## 关键 payload

```
op.sendmsg([aad],cmsg,MSG_MORE); os.splice(target_fd,pipe_w,t+4,offset_src=0); os.splice(pipe_r,op.fileno(),t+4)
```

## 经验教训

容器共享page cache导致只读volume可写；AF_ALG sendmsg/splice是攻击面

## 标签

kernel、page-cache、AF_ALG、splice、CVE、container-escape、authencesn、esn

## 参考来源

- https://www.ctfiot.com/307687.html
- 原文件：Copy_Fail_深度研究：Linux_页缓存漏洞的根因、利用与检测.full.md

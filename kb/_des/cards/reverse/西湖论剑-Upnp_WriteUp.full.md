---
title: "西湖论剑-Upnp WriteUp"
category: reverse
tags: ["西湖论剑 Upnp", "reverse", "NETGEAR-R-series", "UPnP-rce", "SOAPAction", "DeviceConfig"]
signals: ["西湖论剑 Upnp 2022", "NETGEAR-R-series", "UPnP-rce", "SOAPAction", "DeviceConfig", "ParentalControl", "auth-bypass", "session-confirm", "HTTP-v4", "reverse", "UPnP", "WriteUp", "NETGEAR", "R7000"]
difficulty: hard
source: "https://www.ctfiot.com/110766.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 西湖论剑-Upnp WriteUp

> 赛事：西湖论剑 Upnp 2022 | 方向：reverse | 难度：hard

## 一句话总结

西湖论剑UPnP WriteUp,NETGEAR R7000系列路由器固件,UPnP SOAPAction协议11个service+SOAPLogin+Cookie sess_id会话+GetMacList白名单+acosNvramConfig_get(lan_ipaddr)比对,经典IoT路由器攻击面。

## 攻击链

1. 路由器固件:NETGEAR R7000系列
2. HTTP请求处理:解析SOAPAction头+v11=stristr(http_v4, "SOAPAction:")
3. action_v13 = v11 + 11
4. 11个内部serverName:parentalcontrol(index=7), DeviceConfig(index=1)
5. 验证:strncpy 127字节+stristr匹配serverName
6. 关键判断:'(v21 - 2) == r && (v21 - 1) == n'即"urn:...:SOAPLogin"格式
7. 未登录:返回401
8. /tmp/opendns_auth.tbl记录已登录MAC地址
9. sessConfirm:验证Cookie sess_id
10. GetMacList + strstr检测已登录MAC
11. lan_ipaddr比较:v45=acosNvramConfig_get("lan_ipaddr")
12. Bypass:伪造Cookie: sess_id=,伪造请求 lan_ipaddr绕过strcmp
13. processAction调用:serverIdx=0~10+ifSSL+pass_v7

## 关键 payload

```
SOAPAction: urn:NETGEAR-ROUTER:service:ParentalControl:1#Authenticate
```

## 经验教训

路由器UPnP SOAPAction是IoT设备经典攻击面;NETGEAR系列有公开的SOAP接口;acosNvramConfig_get(lan_ipaddr)是路由器配置读取常见API;Cookie sess_id+MAC白名单是身份认证基本模式。

## 标签

NETGEAR-R-series、UPnP-rce、SOAPAction、DeviceConfig、ParentalControl、auth-bypass、session-confirm、HTTP-v4、lan-ipaddr、opendns-auth

## 参考来源

- https://www.ctfiot.com/110766.html
- 原文件：西湖论剑-Upnp_WriteUp.full.md

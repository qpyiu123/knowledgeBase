---
title: "HITCON 2023 x DEVCORE Wargame: My todolist Write-up"
category: web
tags: ["HITCON 2023 x DEVCORE Wargame", "web", "web", "json-net", "typename-all", "role-principal"]
signals: ["HITCON 2023 x DEVCORE Wargame 2023", "web", "json-net", "typename-all", "role-principal", "ysoserial", "process-start", "dotnet-deserialize", "web_unknown", "HITCON", "Wargame", "todolist", "Json", "Net"]
difficulty: hard
source: "https://www.ctfiot.com/136182.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON 2023 x DEVCORE Wargame: My todolist Write-up

> 赛事：HITCON 2023 x DEVCORE Wargame 2023 | 方向：web | 难度：hard

## 一句话总结

HITCON 2023 Wargame My todolist：Json.Net反序列化+RolePrincipal+Process.Start

## 攻击链

1. TypeNameHandling=All + MetadataPropertyHandling=ReadAhead
2. 第一个$type控制target类型
3. 第二个$type指定RolePrincipal gadget
4. Process.StartInfo执行 /c calc命令
5. ysoserial.exe -g RolePrincipal -f Json.Net
6. --bgc ActivitySurrogateDisableTypeCheck -c 1
7. POST /Api/UpdateTodo 设置uuid+field=value
8. POST /Api/MyProfile 触发命令执行cmd=whoami

## 关键 payload

```
$type=System.Web.Security.RolePrincipal + Process.StartInfo /c calc
```

## 经验教训

Json.Net TypeNameHandling=All配合RolePrincipal gadget可RCE

## 标签

web、json-net、typename-all、role-principal、ysoserial、process-start、dotnet-deserialize

## 参考来源

- https://www.ctfiot.com/136182.html
- 原文件：HITCON_2023_x_DEVCORE_Wargame-_My_todolist_Write-up.full.md

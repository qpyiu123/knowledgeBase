---
title: "沙箱逃逸之google ctf 2019 Monochromatic writeup"
category: web
tags: ["Google CTF 2019", "web", "Chromium Mojo IPC", "Person/Dog/Cat Interface", "BeingCreatorInterface", "Blink"]
signals: ["Google CTF 2019 2019", "Chromium Mojo IPC", "Person/Dog/Cat Interface", "BeingCreatorInterface", "Blink", "content_browser_manifest", "MojoJS", "rce", "Google", "CTF", "Monochromatic", "Chromium", "Mojo", "IPC"]
difficulty: insane
source: "https://www.ctfiot.com/91451.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 沙箱逃逸之google ctf 2019 Monochromatic writeup

> 赛事：Google CTF 2019 2019 | 方向：web | 难度：insane

## 一句话总结

Google CTF 2019 Monochromatic：Chromium Mojo IPC BeingCreatorInterface + 3 Interface UAF沙箱逃逸

## 攻击链

1. Mojo IDL定义BeingCreatorInterface+PersonInterface+DogInterface+CatInterface→content_browser_manifest暴露blink.mojom.BeingCreatorInterface→renderer调用CreatePerson/CreateDog/CreateCat→Impl侧直接传入blink::mojom::FoodInterface引用计数处理UAF→sandbox逃逸

## 关键 payload

```
mojo public/tools/bindings/mojom.gni;interface BeingCreatorInterface CreatePerson CreateDog CreateCat;PersonInterface GetName/SetName/GetAge/SetAge/GetWeight/SetWeight/CookAndEat(blink.mojom.FoodInterface food)
```

## 经验教训

Blink Mojo IPC新增Interface需注册到content_browser_manifest；FoodInterface引用计数UAF是逃逸点

## 标签

Chromium Mojo IPC、Person/Dog/Cat Interface、BeingCreatorInterface、Blink、content_browser_manifest、MojoJS

## 参考来源

- https://www.ctfiot.com/91451.html
- 原文件：沙箱逃逸之google_ctf_2019_Monochromatic_writeup.full.md

---
title: "HITCON CTF 2022 — Fourchain – Hypervisor"
category: misc
tags: ["HITCON CTF 2022", "misc", "pwn", "hypervisor", "virtualbox", "e1000-mmio"]
signals: ["HITCON CTF 2022 2022", "pwn", "hypervisor", "virtualbox", "e1000-mmio", "ring0-ring3", "arb-read-write", "pdevins-fake", "pfnwrite-callback", "misc_unknown", "HITCON", "CTF", "Fourchain", "Hypervisor"]
difficulty: hard
source: "https://www.ctfiot.com/81562.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HITCON CTF 2022 — Fourchain – Hypervisor

> 赛事：HITCON CTF 2022 2022 | 方向：misc | 难度：hard

## 一句话总结

HITCON CTF 2022 Fourchain Hypervisor：E1000 MMIO fake pDevIns劫持callback

## 攻击链

1. VirtualBox E1000 MMIO 任意读写
2. 泄露 Ring 3 DeviceE1000->pDevIns = 0x178 偏移
3. 读 pDevIns->pCritSectRoR3 = 偏移 0x28
4. 构造 fake_pDevIns + 写 R3 pDevIns = fake
5. fake_pDevIns + 0x28 = pCritSectRoR3
6. R3 pDevIns->pfnWriteCallback = system
7. 触发 R3 MMIO write → system("touch /tmp/456")
8. ioremap(E1000_MMIO_BASE, 0x1000) R3 触发

## 关键 payload

```
R3 pDevIns->pfnWriteCallback = system; "touch /tmp/456
```

## 经验教训

VirtualBox E1000 pDevIns->pfnWriteCallback可劫持为system

## 标签

pwn、hypervisor、virtualbox、e1000-mmio、ring0-ring3、arb-read-write、pdevins-fake、pfnwrite-callback

## 参考来源

- https://www.ctfiot.com/81562.html
- 原文件：HITCON_CTF_2022_—_Fourchain_–_Hypervisor.full.md

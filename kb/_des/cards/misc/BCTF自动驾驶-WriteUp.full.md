---
title: "BCTF 自动驾驶 - WriteUp"
category: misc
tags: ["BCTF", "misc", "ADC Autonomous Driving", "Stanley controller", "PID控制", "Lane Detection targeted attack"]
signals: ["BCTF 2022", "ADC Autonomous Driving", "Stanley controller", "PID控制", "Lane Detection targeted attack", "KMeans聚类", "deltaE_cie76", "rgb2lab", "GPS spoofing", "rce", "BCTF", "Stanley", "PID", "Lane"]
difficulty: hard
source: "https://www.ctfiot.com/1441.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# BCTF 自动驾驶 - WriteUp

> 赛事：BCTF 2022 | 方向：misc | 难度：hard | 工具：Python

## 一句话总结

BCTF 自动驾驶 — Stanley 横向控制 + PID 纵向控制 + Lane Detection targeted attack + Adversarial NPC GPS 缩放攻击 (rate=1.2 pos[120]/pos[399] 锚点)。

## 攻击链

1. demo: Lane Detection targeted attack + ADC Programming interception
2. planning.py: Stanley controller (k_e=0.3, k_v=0.01) + delta_steer_per_iter=0.1
3. preprocess_image: 416x416 resize + BGR2RGB + transpose
4. waypoint_distance: np.sqrt(sum((waypt1-waypt2)**2))
5. normalize_angle: 限定 ±π
6. lateral_control: yaw_path + crosstrack_error + yaw_diff_crosstrack
7. longitudinal_control: PID(1.0, 0.1, 0.01, setpoint=5)
8. Adversarial NPC: 改 npc_benign.json 的 GPS 坐标, rate=1.2 缩放
9. pos[120+i].latitude = rate*(pos[120].latitude - pos[399].latitude) + pos[120+i].latitude
10. 写 gps_new.json 作为攻击 GPS

## 关键 payload

```
Stanley controller k_e=0.3 k_v=0.01 / PID(1.0,0.1,0.01) / rate=1.2 GPS 缩放 / pos[120] vs pos[399] 锚点
```

## 经验教训

自动驾驶对抗攻击: 横向 Stanley + 纵向 PID 控制;GPS 注入通过修改 npc JSON 即可;车道线检测可被 adversarial 干扰。

## 标签

ADC Autonomous Driving、Stanley controller、PID控制、Lane Detection targeted attack、KMeans聚类、deltaE_cie76、rgb2lab、GPS spoofing、npc_benign.json、latitude/longitude/altitude/yaw/speed、adversarial NPC、lane target attack

## 参考来源

- https://www.ctfiot.com/1441.html
- 原文件：BCTF自动驾驶-WriteUp.full.md

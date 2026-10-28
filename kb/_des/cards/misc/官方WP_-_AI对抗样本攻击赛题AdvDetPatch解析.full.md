---
title: "AI对抗样本攻击赛题AdvDetPatch官方WP(yolov5对抗补丁)"
category: misc
tags: ["伽玛实验场AI对抗赛 + 2019信安国赛Deep_Learning", "misc", "对抗样本", "PGD", "Adam优化器", "yolov5"]
signals: ["伽玛实验场AI对抗赛 + 2019信安国赛Deep_Learning 2023", "对抗样本", "PGD", "Adam优化器", "yolov5", "白盒攻击", "目标检测对抗", "对抗补丁", "deepfool", "stego", "Maple_Leaves", "Lilac", "yolov5l", "yolov5n"]
difficulty: hard
source: "https://www.ctfiot.com/118789.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AI对抗样本攻击赛题AdvDetPatch官方WP(yolov5对抗补丁)

> 赛事：伽玛实验场AI对抗赛 + 2019信安国赛Deep_Learning 2023 | 方向：misc | 难度：hard

## 一句话总结

中科大+Maple_Leaves一血+哈工大Lilac二血yolov5目标检测对抗补丁+偷梁换柱(替换模型)非预期解。

## 攻击链

1. 一血:观察yolov5l.pt相对路径加载+ln -s替换为yolov5n.pt绕过检测 → 二血:冻结网络参数+对input梯度下降+保留梯度绝对值最大的20480像素+Adam优化14轮迭代 → 攻击:patch=randn+127/255+mask应用+clamp[0,1]→loss=Σ25200个bbox置信度 → 通用:DeepFool低扰动对抗样本骗过wing识别

## 关键 payload

```
20480像素 + Adam(lr=0.1) + yolov5l.pt相对路径 + yolov5n.pt替换 + conf_thres=0.25
```

## 经验教训

对抗样本白盒攻击经典方法:冻结模型+对input梯度下降+Adam优化+NMS前25200候选bbox置信度最小化;对抗补丁设计考虑形状(网格/方形/圆/星形)+位置(检测框中心)+纹理;一血非预期:加载模型用相对路径即可替换;信安国赛Deep_Learning经典0解题,需用DeepFool低扰动;信安国赛当年0解。

## 标签

对抗样本、PGD、Adam优化器、yolov5、白盒攻击、目标检测对抗、对抗补丁、deepfool、伽玛实验场、FGSM、替换模型、偷梁换柱

## 参考来源

- https://www.ctfiot.com/118789.html
- 原文件：官方WP_-_AI对抗样本攻击赛题AdvDetPatch解析.full.md

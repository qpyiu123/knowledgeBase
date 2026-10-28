---
title: "【卫星安全系列五】attitude 赛题复现"
category: crypto
tags: ["Hack-A-Sat 2020 attitude", "crypto", "卫星姿态", "四元数", "旋转矩阵", "Kabsch算法"]
signals: ["Hack-A-Sat 2020 attitude 2023", "卫星姿态", "四元数", "旋转矩阵", "Kabsch算法", "rmsd库", "scipy.spatial.transform.Rotation", "恒星追踪", "卡尔曼", "misc_math", "attitude", "Kabsch", "SVD", "dataA_list"]
difficulty: hard
source: "https://www.ctfiot.com/153356.html"
tools: ["Python", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【卫星安全系列五】attitude 赛题复现

> 赛事：Hack-A-Sat 2020 attitude 2023 | 方向：crypto | 难度：hard | 工具：Python、netcat

## 一句话总结

卫星姿态 attitude: 2500 恒星向量 + Kabsch 算法 SVD 旋转矩阵 + 四元数提交 20 次。

## 攻击链

1. 题目: 给 2500 行恒星 (X,Y,Z,星等) 参考向量 dataA_list
2. nc 拿到 4 浮点观测向量 (id, x, y, z)
3. 卫星姿态: 星体坐标系 → 惯性坐标系 旋转关系
4. 描述方式: 旋转矩阵 / 四元数 (q=[w,x,y,z]) / 欧拉角 / DCM / 轴角
5. Kabsch 算法: 中心化 + 协方差矩阵 + SVD 分解 + 旋转矩阵
6. pip install rmsd 库
7. R = rmsd.kabsch(A, B) 计算最优旋转
8. sol = Rotation.from_matrix(R).as_quat() 矩阵转四元数
9. 发送 ','.join(str(x) for x in sol) 四元数
10. 重复 20 次验证通过

## 关键 payload

```
rmsd.kabsch + scipy Rotation.as_quat() 四元数
```

## 经验教训

卫星姿态用四元数 (w,x,y,z) 表示避免万向锁；Kabsch 算法通过 SVD 找两组点集最佳旋转；rmsd 库 + scipy.spatial.transform.Rotation 是 Python 卫星题双神器。

## 标签

卫星姿态、四元数、旋转矩阵、Kabsch算法、rmsd库、scipy.spatial.transform.Rotation、恒星追踪、卡尔曼

## 参考来源

- https://www.ctfiot.com/153356.html
- 原文件：【卫星安全系列五】attitude_赛题复现.full.md

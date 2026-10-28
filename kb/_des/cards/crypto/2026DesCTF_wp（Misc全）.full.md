---
title: "2026 DesCTF wp（Misc 全 - bkcrack 已知明文攻击 + zigzag 还原 + torch 模型反演 + Modbus + Shamir 秘密分享）"
category: crypto
tags: ["2026 DesCTF", "crypto", "DesCTF 2026 Misc", "bkcrack 已知明文攻击 challenge.png 89504E47 IHDR", "7z 头 37 7A BC AF 27 1C", "2D zigzag 还原 PIL"]
signals: ["2026 DesCTF 2026", "DesCTF 2026 Misc", "bkcrack 已知明文攻击 challenge.png 89504E47 IHDR", "7z 头 37 7A BC AF 27 1C", "2D zigzag 还原 PIL", "torch 加载 model.pth 提 eval_cache embedding 反演", "红外遥控器 cmd:00 15=OK/16=U/17=D/18=R/19=L 6x6 网格 ABCDEF/GHIJKL/MNOPQR/STUVWX/YZ1234/567890", "Modbus func_code 8 异常响应", "Shamir 秘密分享 Lagrange 插值还原 P=666c61677b...", "block_cipher", "stego_image", "ai", "pwn_unknown", "DesCTF"]
difficulty: hard
source: "https://www.ctfiot.com/301742.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2026 DesCTF wp（Misc 全 - bkcrack 已知明文攻击 + zigzag 还原 + torch 模型反演 + Modbus + Shamir 秘密分享）

> 赛事：2026 DesCTF 2026 | 方向：crypto | 难度：hard | 工具：C

## 一句话总结

2026 DesCTF Misc 全：bkcrack 已知明文 + PIL zigzag + torch 模型反演 + 红外遥控 6x6 网格 + Modbus func 8 + Shamir 秘密分享 Lagrange 还原。

## 攻击链

1. 7z 文件头 37 7A BC AF 27 1C 已知
2. bkcrack -C challenge.zip -c challenge.png -x 0 89504E47...IHDR 已知明文攻击
3. 2D zigzag PIL 反向还原
4. torch.load('model.pth') 提 eval_cache (39, 64) + embedding.weight (95, 64) → argmin 距离 → idx2char → flag
5. 红外遥控器: 提取 cmd: 0x15-0x19 字节 → 网格 6x6 → 模拟 OK 键
6. Modbus func_code==8 异常响应 crc 还原
7. Shamir: 5 份 share + P 模数 → Lagrange at zero → flag

## 关键 payload

```
bkcrack -C challenge.zip -c challenge.png -x 0 89504E470d0a1a0a0000000d49484452
```

## 经验教训

DesCTF 2026 Misc 集齐密码学/取证/AI 三大方向；bkcrack 是 ZIP 已知明文攻击首选工具；torch 加载 .pth 提 embedding+eval_cache 反推训练字符是 AI 攻击新套路；Shamir 秘密分享直接 Lagrange at zero 还原。

## 标签

DesCTF 2026 Misc、bkcrack 已知明文攻击 challenge.png 89504E47 IHDR、7z 头 37 7A BC AF 27 1C、2D zigzag 还原 PIL、torch 加载 model.pth 提 eval_cache embedding 反演、红外遥控器 cmd:00 15=OK/16=U/17=D/18=R/19=L 6x6 网格 ABCDEF/GHIJKL/MNOPQR/STUVWX/YZ1234/567890、Modbus func_code 8 异常响应、Shamir 秘密分享 Lagrange 插值还原 P=666c61677b...、多文件综合取证

## 参考来源

- https://www.ctfiot.com/301742.html
- 原文件：2026DesCTF_wp（Misc全）.full.md

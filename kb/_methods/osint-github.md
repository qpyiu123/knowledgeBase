---
title: 方法卡 · OSINT 图片溯源与泄露数据检索
category: osint
tags: [osint, image-hash, phash, reverse-search, hibp, github]
signals:
  - 题目给一张照片且要求找出拍摄地/账号/原始出处
  - 图片被裁剪、镜像或加过滤，肉眼比对失效
  - 附件里出现 32/40 位十六进制串，怀疑是口令哈希
  - 用户名/邮箱/域名需要在公开仓库与泄露库中交叉定位
  - 图里有 C2PA 元数据或 Software=Midjourney 之类生成痕迹
difficulty: hard
source: kb/osint/osint-image-reverse.md, kb/osint/leaked-data-search.md
tools: [python, imagehash, google-lens, yandex, hibp, github-search]
updated: 2026-11-03
---

## 适用场景

两类线索需要收敛：**图**（同一张图换皮后要找回原图/账号）与**字符串**（哈希、邮箱、域名的泄露面）。
信号：肉眼相似的图直接搜不到；哈希串长度 32/40/64；需要判断"这张图和那张图是不是同一张"。

## 前置条件

- 图片先转灰度 PGM 或直接读像素；离线比较用 dhash/ahash（差值/均值哈希）。
- 反向搜图走 Google Lens / Yandex / Bing Visual Search，**先裁剪掉水印与背景**再搜。
- 口令泄露查询用 HIBP 的 k-anonymity 接口：只上送 SHA-1 前 5 位，**不要**把完整哈希或口令发到任何站外服务。
- 合规边界：只查公开数据，不碰需要授权才能访问的库，不把他人真实隐私写进 writeup。

## 步骤

1. **先看元数据**。C2PA 清单、`Software=Midjourney/Adobe Photoshop 25.0` 能直接说明生成或二次编辑，比像素比对更有说服力。
2. **算哈希指纹**。同一张图缩放/压缩后 dhash/ahash 变化很小；`distance` 小于 10 通常视为同源，10..20 需人工比对称与纹理，>20 基本不同。
3. **镜像/翻转先处理**。截图常被水平翻转，先翻转候选图再算距离，否则距离会被结构性地拉大。
4. **反向搜图**。把图裁成焦点区域，多引擎并搜；对搜索结果里的原图再做一次哈希比对确认，而不是只信"看起来一样"。
5. **字符串分类**。32 位十六进制 = MD5（也可能是 NTLM），40 位 = SHA-1，64 位 = SHA-256；先定类型再查。
6. **口令泄露查询**。本地算 SHA-1 → 取前 5 位 → 查 k-anonymity 接口 → 用后缀在返回列表里匹配，全程不回传完整哈希。
7. **公开仓库检索**。用用户名/邮箱/域名搜 GitHub 代码、Gist、提交历史；拿到仓库名后再回本地用 `grep -R` 复核（检索结果只是线索）。
8. **交叉验证**。地点用街景/卫星图比对，账号用多平台同名+时间线比对；至少两条独立证据再下结论。

## 立即可用脚本

`kb/_methods/scripts/osint_github.py`

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe kb\_methods\scripts\osint_github.py --image shot.pgm
.venv\Scripts\python.exe kb\_methods\scripts\osint_github.py --distance 0x1234567890abcdef 0x1234567890abcdee
.venv\Scripts\python.exe kb\_methods\scripts\osint_github.py --hash-kind d41d8cd98f00b204e9800998ecf8427e
.venv\Scripts\python.exe kb\_methods\scripts\osint_github.py --hibp password
.venv\Scripts\python.exe kb\_methods\scripts\osint_github.py --selftest
```

- `--image`：PGM(P5) 灰度图，输出 64 位 dhash/ahash 十六进制指纹。
- `--distance`：两个 64 位整数哈希值的汉明距离 + 判定档位（同源 / 疑似 / 基本不同）。
- `--hash-kind`：按长度与十六进制合法性判 32/40/64 位哈希类型。
- `--hibp`：本地算 SHA-1 及前 5 位（k-anonymity 只上送这 5 位），脚本本身不联网。
- `--json`：机器可读输出，便于批量汇总。
- 失败：无参数、非 PGM、哈希串非法、距离为负 → 中文提示，退出码 2。
- `--selftest` 覆盖哈希、距离、判定档位、哈希类型、参数拒绝五组断言，通过时打印 `selftest ok` 并退出 0。

## 手工示例

```
$ python osint_github.py --hash-kind d41d8cd98f00b204e9800998ecf8427e
hash_kind: MD5 或 NTLM（32 位十六进制无法区分）

$ python osint_github.py --hibp password
hibp: {'sha1': 'SHA1:5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8', 'prefix5': '5BAA6', 'suffix': '1E4C9B93F3F0682250B6CF8331B7EE68FD8'}

$ python osint_github.py --distance 0 15
distance: {'value': 4, 'verdict': '同源'}
```

边界：`--hash-kind abc` → `失败：长度 3 不是常见的 32/40/64 位哈希`（退出码 2）；无参数 → argparse 报"必须提供 ... 之一"（退出码 2）。

## 失效场景

- **dhash 不是 pHash**：脚本实现的是差分/均值哈希，抗几何变形能力弱；要求对旋转、透视鲁棒时请上 `imagehash.phash` 或 DCT 版实现。
- **不做图像解码**：只吃 PGM(P5)，JPEG/PNG 需先用 `magick shot.png -colorspace Gray shot.pgm` 转换，否则直接报错。
- **不联网**：所有"检索"都在本地计算指纹与查询串，实际反查必须在合规前提下由人手动发起到对应平台。
- **哈希类型不可区分**：32 位十六进制既可能是 MD5 也可能是 NTLM，脚本不做二次判定，需结合上下文（Windows 转储 vs Web 应用）。
- **元数据早被洗掉**：社交平台上传会自动剥 EXIF/C2PA，此时只能靠像素指纹与外部线索，不能指望"从图里读出设备型号"。

## 相关文档

- `kb/osint/osint-image-reverse.md`：pHash/dHash/wHash/aHash 的区别、距离阈值、镜像翻转先处理、C2PA 痕迹。
- `kb/osint/leaked-data-search.md`：HIBP k-anonymity、哈希长度判型、本地转储统计、合规边界。
- `kb/forensics/exif-metadata.md`：把元数据取证做细（GPS、DateTimeOriginal、Software）。
- `kb/_methods/exif-metadata.md`：本库随附的 EXIF 解析脚本与流程。

## 目录与收录说明

- 卡：`kb/_methods/osint-github.md`；脚本：`kb/_methods/scripts/osint_github.py`（纯标准库、无网络、无绝对盘符）。
- 覆盖 backlog 项 `osint-github`（category=osint），证据来自 `kb/osint/osint-image-reverse.md` 与 `kb/osint/leaked-data-search.md`。
- 与 `exif-metadata.md` 的分工：本卡负责"跨源比对"，元数据取证归 EXIF 卡。

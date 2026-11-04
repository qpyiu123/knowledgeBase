---
title: 方法卡 · QR 码与条码结构核查
category: misc
tags: [qr, barcode, ean13, code128, grid, forensics]
signals:
  - 题目给的是一堆 0/1、#/空格 或黑白像素的方阵
  - 图片里有一个方形码，角上有三个回字形定位框
  - 记录只有 13 位数字且末位像校验位（EAN-13）
  - 一维条码被切断，只剩一段条与一个码值数组
  - 只有 13 位数字的条码
  - EAN-13 末位校验失败
difficulty: medium
source: kb/misc/barcode-check-digit.md, kb/misc/cyberchef-and-tools.md
tools: [python, .venv python, zbarimg, CyberChef]
updated: 2026-11-03
---

## 适用场景

附件是二维码截图、手抄的 0/1 点阵、被裁过的条码照片，或者流量/日志里只留下一串数字。
脚本可检查条码校验位、矩阵尺寸及定位图案。QR 分支只做结构演示，逐行采样字节不是二维码内容；读取内容请使用 zbarimg 等解码器。

- 有线上一维码：13 位数字（EAN-13）或一串 Code128 码值，先判校验位是否成立，判断是否抄错。
- 有方形矩阵：先判是不是 QR 版本（边长 21+4k），再看定位图案、定时图案、掩码号。
- 只有像素图：先转 PGM 灰度，按模块中心降采样成矩阵，避免手工数格子。

## 前置条件

- 纯标准库即可（argparse/re/sys），不需要 PIL、zxing、numpy。
- 图像要先转成 PGM：`magick shot.png -colorspace Gray -compress none out.pgm`（或 GIMP 导出 P5）。
- 明确模块边长：`--modules 21` 对应版本 1，25 对应版本 2 … 177 对应版本 40。

## 步骤

1. **先判形态**。13 位纯数字走 `--ean`；逗号分隔的整数走 `--code128`；其余按矩阵走 `--text/--matrix/--pgm`。
2. **算校验位而不是靠眼看**。EAN-13 从左数前 12 位交替乘 1、3，末位要满足 `(10 - total%10) % 10`；Code128 起始符权重 1、第 k 位权重 k、末位为模 103 校验和。
3. **检查矩阵**。确认尺寸、定位图案和定时线；保留区和采样顺序是本脚本的简化演示。
4. **读取内容用解码器**。例如先运行 `zbarimg shot.png`；本脚本试掩码和逐行采样仅供观察，不输出有效 QR 码字。
5. **图片模糊时**先降采样再人工核对：把 PGM 用模块中心采样得到矩阵，打印成 0/1 文本，与明显图案（定位框、定时线）逐行对照。
6. 解码器成功返回内容后，再判断是否需要继续解 Base64 等编码。
7. 结果统一记进报告：版本、掩码号、抽取字节的十六进制前缀，便于复现。

## 立即可用脚本

`kb/_methods/scripts/qr_barcode.py`

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe kb\_methods\scripts\qr_barcode.py --matrix m.txt --modules 21
.venv\Scripts\python.exe kb\_methods\scripts\qr_barcode.py --pgm shot.pgm --modules 25
.venv\Scripts\python.exe kb\_methods\scripts\qr_barcode.py --ean 9780306406157
.venv\Scripts\python.exe kb\_methods\scripts\qr_barcode.py --code128 104,40,41,42,30,60
.venv\Scripts\python.exe kb\_methods\scripts\qr_barcode.py --selftest
```

- `--matrix` 读 UTF-8 文本矩阵，`--text` 直接给矩阵文本，`--pgm` 读 P5/P2 灰度图。
- `--modules` 只能是 21+4k（21..177），否则报版本错误。
- 输出：版本、尺寸、掩码号、格式信息纠错等级、简化罚分、数据模块数、可读字节数与前 32 字节十六进制。
- 失败一律 stderr 中文提示 + 退出码 2（参数不足、矩阵非方、定位/定时图案不合、文件缺失）。
- `--selftest` 覆盖保留区/读取顺序、定位图案、参数拒绝、条码校验四类断言，全部通过时打印 `selftest ok` 并退出 0。

## 手工示例

```
$ python qr_barcode.py --ean 9780306406157
9780306406157: 校验通过
$ python qr_barcode.py --code128 104,40,41,42,30,60
104,40,41,42,30,60: 校验通过
```

矩阵形态（21x21，`#` 与 `1` 都算黑）：

```
$ python qr_barcode.py --matrix m.txt
版本 1，尺寸 21x21，掩码 2（格式信息 5），罚分 49，数据模块 192，可读字节 24
演示采样字节（逐行取样，未按 QR 码字顺序解码）：55556a56aaaa955556aaa555aaa555aaa555aaa555aaa555
```

边界：`--text '0101'` → `失败：矩阵不是正方形：1x4`（退出码 2）；`--ean 12345` → `失败：EAN-13 必须是 13 位数字`（退出码 2）。

## 失效场景

- **没有 RS 纠错**：脚本不做 Reed-Solomon 校验与纠正，单点像素翻转会直接污染提取字节，需人工按定位/定时图案排除破损行。
- **不做采样网格对齐**：PGM 只按整除/等比例取模块中心，镜头透视、旋转、光照不均的实拍图会整体错行，需先透视矫正再做。
- **不做编码模式解析**：只取字节，不区分数字/字母/字节/汉字模式，也不还原 ECI 与版本信息块，非 ASCII 内容需自行按模式表解码。
- **一维码只验校验位**：不读条宽，无法从图像还原码值；Code128 必须由题目或人工给出码值数组。
- **复杂版式失败**：版本≥7 的对齐图案、多块交织未建模，`reserved_map` 仅对 21x21 用规范字面量，更大尺寸的保留区是近似铺法。

## 相关文档

- `kb/misc/encoding-auto-detect.md`：拿到字节后判断还是不是又一层编码。
- `kb/misc/cyberchef-and-tools.md`：Magic 配方、XOR Brute Force 复核。
- `kb/_methods/enc_chain_decode.md`：多层编码链的通用拆解流程。
- `kb/_methods/cyberchef-recipes.md`：CyberChef 配方与判定阈值。

## 目录与收录说明

- 卡：`kb/_methods/qr-barcode.md`；脚本：`kb/_methods/scripts/qr_barcode.py`（纯标准库、无网络、无绝对盘符）。
- 覆盖 backlog 项 `qr-barcode`（category=misc），校验来源为 `kb/misc/barcode-check-digit.md`，工具来源为 `kb/misc/cyberchef-and-tools.md`。
- 与已有 `enc_chain_decode.md` 的分工：本卡负责条码校验与 QR 结构演示，`enc_chain_decode.md` 负责"字节→明文"的链式解码。
- 定性：本卡不引入第三方库，`tests/test_method_scripts.py` 会自动收集本脚本的 `--selftest`。

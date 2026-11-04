---
title: 方法卡 · PNG/BMP 隐写与 LSB 分析
category: forensics
tags: [steg, png, bmp, lsb, crc, exif-tool, zsteg, 取证]
signals:
  - "图片能正常打开，但 binwalk 显示 IEND 之后还有数据"
  - "grep -abo 'IEND' img.png 的偏移小于文件大小"
  - "strings 出 tEXt/zTXt 自定义关键字或一段可疑 base64"
  - "文件头是 BM 而题目提示是 PNG，或反之"
  - "zlib 头 78 9c 但长度跟像素数对不上"
  - "图片颜色看着有点噪点，红蓝通道疑似互换"
difficulty: medium
source: kb/forensics/steganalysis-workflow.md, kb/misc/file-repair-and-corruption.md
updated: 2026-11-03
tools: [python3, zsteg, stegsolve, binwalk, exiftool, pngcheck]
---
## 适用场景

题目给一张 PNG/BMP，肉眼无异常，但"答案就在文件里"。按层推进，别一上来就跑
`steghide`：`steghide` 只支持 jpg/bmp/wav，对 PNG 直接报错，而且 `stegseek` 只解 jpg。
PNG 题的主战场是**容器尾部**、**文本 chunk**、**像素 LSB 位平面**和**chunk CRC 是否被同步重算**四层。

## 前置条件

- 原始文件（不要经过聊天软件转发或截图，会被重新压缩，LSB 必丢）。
- 一个能跑 python 的环境；本卡脚本纯标准库，不装 zsteg 也能拿到 80% 线索。
- 想手工看图时准备 `stegsolve`/`zsteg`；修文件准备 `pngcheck`。
- 明确"数据是写在 PNG 里"还是"PNG 只是外壳"——先看文件头再决定路径。

## 步骤

1. **认格式**：前 8 字节 `89 50 4E 47 0D 0A 1A 0A` 是 PNG，`42 4D` 是 BMP。
   扩展名与内容不一致时以内容为准，这本身就是出题线索。
2. **容器层**：`grep -abo 'IEND' img.png | tail -1` 定位 IEND 起点，
   文件大小减去该偏移再减 12（length+type+crc），多出来的字节就是尾部追加数据。
   BMP 同理，比像素偏移 + 宽×高×bpp 之后的部分。
3. **元数据层**：遍历 tEXt/iTXt/zTXt，自定义 keyword（写成 `password`、`Comment`）
   常是下一步的口令；zTXt 数据体是 zlib 流，脚本会自动解。
4. **像素层**：解 IDAT（zlib）→ 逐行去掉 filter 字节 → 按 `LSB-first` 顺序取每个像素
   R/G/B 的最低位拼字节。取不到可读文本就走变体：位序反选（MSB-first）、只取单通道、
   隔像素取（stride=2）、从第 2/3 位平面取。
5. **判定层**：每个 chunk 的 CRC 必须等于 `zlib.crc32(type+data)`。某个 IDAT 的 CRC
   报错而 IHDR 正常，说明只有那段被改过；IHDR 宽高被改且 CRC 也重算过，就要用
   "像素数据流长度 ÷ 每行字节数"反推真实高度。
6. **交叉验证**：抽出来的字节先看头部两字节：`78 9c/78 da/78 01` 是 zlib，
   直接 `zlib.decompress`；`\x89PNG`/`PK\x03\x04`/`\xff\xd8` 说明里面还嵌了文件，
   存盘继续按对应格式分析。

## 立即可用脚本

`kb/_methods/scripts/steg_png_bmp.py`（纯标准库，离线只读）

```
python steg_png_bmp.py --file img.png
python steg_png_bmp.py --file img.png --extract-lsb --channel rgb --stride 1
python steg_png_bmp.py --file img.png --extract-lsb --msb --carve-tail tail.bin
python steg_png_bmp.py --zlib-check 789c
python steg_png_bmp.py --selftest
```

参数：

- `--file`：目标 PNG/BMP（必填，除非用 `--selftest`/`--zlib-check`）。
- `--extract-lsb`：解 IDAT 并抽像素位平面；输出字节数与前 120 字节预览（latin1）。
- `--msb`：改按位序反选（每个通道取最高位拼字节）。
- `--channel r|g|b|rgb`：只取指定通道，默认 rgb。
- `--stride N`：每 N 个像素取一个，默认 1。
- `--carve-tail OUT`：把 IEND 之后的追加数据另存为 OUT（只写你给的文件，不删任何东西）。
- `--zlib-check HEX`：校验两字节 zlib 头（CMF/FLG），判断压缩级别与是否带预置字典。
- `--selftest`：内置断言（往返、非法头拒绝、参数不足、固定输入）。

失败行为：认不出格式、IDAT 解压失败、`--stride < 1` 都在 stderr 打印 `失败：…`
并返回非 0；`--selftest` 通过时打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ grep -abo 'IEND' img.png | tail -1
98213:IEND
$ ls -l img.png
-rw-r--r-- 1 kali kali 98500 img.png     # 98500 - 98213 - 12 = 275 字节尾巴
$ python steg_png_bmp.py --file img.png --carve-tail tail.bin
  尾部追加: 275 字节（疑似藏东西，试 --carve-tail）
$ head -c 2 tail.bin | xxd
00000000: 789c                                     # zlib，继续解压
$ python -c "import zlib;print(zlib.decompress(open('tail.bin','rb').read()))"
b'flag{1end_tail_1s_easy}'
```

## 失效场景

- 图片被重新编码过（发给你的已经是二次压缩产物）：LSB 全部被打散，只能做尾部/文本层。
- 隐写工具自带加密（`stegseek`、`outguess`、`F5`、`mp3stego`）：需要口令，
  本脚本抽出来的只是密文，要回到口令爆破流程。
- 调色板 PNG（color type 3）：IDAT 里是索引不是真实 RGB，直接取 LSB 拿到的是调色板索引，
  需先按 PLTE 还原；脚本对 8 位非隔行只做近似还原，16 位/隔行图会明确报"暂不支持"。
- 写入方用的是 bit-plane 2/3 或成对像素差分：默认只取最低位，要人工换平面再试。

## 相关文档

- `kb/forensics/steganalysis-workflow.md`：分层表与工具矩阵（binwalk/foremost/exiftool/steghide）。
- `kb/misc/file-repair-and-corruption.md`：chunk 结构与 CRC 重算、IHDR 宽高反推。
- `kb/forensics/file-carving.md`：IEND/EOI 标记与雕刻边界，尾部数据继续雕。
- `kb/_methods/enc_chain_decode.md`：抽出来的字符串若是编码套娃，接着用这张卡。

## 目录与收录说明

- 卡片：`kb/_methods/steg-png-bmp.md`；脚本：`kb/_methods/scripts/steg_png_bmp.py`。
- 对应 backlog 项 `steg-png-bmp`（category=forensics），源文档
  `kb/forensics/steganalysis-workflow.md` 与 `kb/misc/file-repair-and-corruption.md`。

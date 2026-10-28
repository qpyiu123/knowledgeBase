---
title: 二维码与条码识别（残缺二维码 / Aztec / DataMatrix）
category: misc
tags: [二维码, qrcode, zbarimg, 残缺码, Aztec, DataMatrix]
signals: [附件是一张二维码, 二维码缺了三个角, 二维码被打了马赛克, 扫码结果只有一半 flag, 图片里有一维条形码, 需要重建二维码的定位图形]
difficulty: easy
source: "CTF-Wiki / zbar 文档 / ZXing 纠错原理 / qrazybox 在线工具"
tools: [zbarimg, zxing, qrazybox, aperisolve, python-zxing, Pillow, ImageMagick]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是二维码图片，但**三个角的定位方块（Finder Pattern）缺了一个**。
- 二维码被**遮住一部分**，扫出来是 `flag{abc` 这样的半截。
- 图片是 `Aztec` 码或 `DataMatrix` 码（正方形、中心有牛眼图案），普通扫一扫 App 认不出。
- 题面给的是"二维码的一部分"，要求"还原"。
- 图片里有一排竖条纹——Code128/EAN-13 条形码。
- 扫出来是 URL/Base64，需要继续解码。

## 二、原理

二维码（QR Code）由**定位图形**（3 个大方块）、**校正图形**、**时序图形**、**格式信息**和**数据+纠错码**组成。Reed–Solomon 纠错允许在若干码字错误时仍能恢复数据，等级 L/H 分别能纠正约 7%/30% 的损坏。因此：

- **缺 1 个定位角**：很多解码器仍能靠另外两个角 + 校正图形定位，直接 `zbarimg` 常能出。
- **大面积遮挡**：先根据已知的 mask、版本、格式信息**手工重建矩阵**，再解码；工具是 [QrazyBox](https://github.com/Merricx/qrazybox)（Web 版）。
- **打了马赛克/模糊**：马赛克是不可逆的，只能利用"同一位置多处马赛克块取值不同"推出规律，或从题面提示重建原图。
- **Aztec / DataMatrix**：与 QR 不同的二维符号。Aztec 中心是"靶心"（Bullseye），DataMatrix 两侧有 L 形实线和交替黑白的"时钟轨"。`zbarimg` 只支持 QR/DataMatrix/一维码，Aztec 用 `zxing` 或在线工具。

## 三、操作步骤

1. **放大与二值化**：`magick`/Pillow 放大 4 倍、灰度、阈值化，去掉噪点。
2. **先扫一遍**：`zbarimg --raw file.png`；失败再 `zxing --try_harder`。
3. **残缺修复**：用 QrazyBox 手工补定位图形/时序图形，或直接把缺失模块当"错误"交给纠错。
4. **验证**：`--raw` 输出不含前缀，去掉换行即可。
5. **冷门符号**：把图裁出符号区域，换成 Aztec/DataMatrix 解码模式。
6. **多码同图**：`zbarimg` 会输出每一段，注意用 `--quiet` 抑制日志。

## 四、命令/脚本

### 基础扫描

```bash
zbarimg --raw -q target.png                 # -q 静音，--raw 只要文本
zbarimg --raw target.png | tr -d '\n'
# zxing（Java CLI）
java -cp javase.jar:core.jar com.google.zxing.client.j2se.CommandLineRunner \
     --try_harder --dump_results target.png
python -m pyzbar target.png                  # 需要 pyzbar
file target.png && identify target.png       # 确认尺寸
```

### 预处理：放大 + 二值化 + 反色

```bash
magick target.png -resize 400% -colorspace Gray -threshold 50% big.png
magick big.png -negate big_neg.png
zbarimg --raw -q big.png; zbarimg --raw -q big_neg.png
python - <<'PY'
from PIL import Image, ImageOps
im = Image.open('target.png').convert('L')
im = im.resize((im.width*4, im.height*4), Image.NEAREST)
im = im.point(lambda p: 255 if p > 128 else 0)
im.save('prep.png'); ImageOps.invert(im).save('prep_inv.png')
PY
```

### 生成/重建二维码（对比定位图形）

```bash
pip install qrcode[pil]
python - <<'PY'
import qrcode
img = qrcode.make('flag{PLACEHOLDER}', version=None, error_correction=qrcode.constants.ERROR_CORRECT_H)
img.save('ref.png')
print('ref size', img.size)
PY
# 用两张图的矩阵对比：把 ref 与题图同尺寸后做 XOR 可视化
magick compare -compose src target.png ref.png diff.png
```

### 手工重建矩阵（QrazyBox 工作流）

```
1. 打开 https://merricx.github.io/qrazybox/
2. Tools -> Import from Image，上传残缺二维码
3. 用 Draw 模式补：三个 Finder Pattern（7x7）、Timing Pattern（行/列交替黑白）、
   Alignment Pattern（版本>=2 才有）、Format Info（两个 15bit 副本）
4. Tools -> Reed Solomen Decoder 先看纠错是否足够
5. Tools -> Extract QR Information 直接拿文本
```

### 一维条码

```bash
zbarimg --raw barcode.png
# 若条码被旋转：先转正
magick in.png -rotate 90 rot.png && zbarimg --raw rot.png
```

### 二维码内容进一步处理

```bash
zbarimg --raw -q target.png | sed 's/data:.*base64,//' | base64 -d | xxd | head
```

## 五、常见坑 / 变体

- **马赛克不等于损坏**：马赛克抹掉的是像素，纠错无能为力；此时题目一定给了别的线索（如相同马赛克块对应的原文位置已知）。
- **反色二维码**：黑白颠倒，很多解码器失败，先 `-negate`。
- **倾斜/透视**：先做四点透视变换（`magick ... -distort Perspective`），否则 zbar 定位失败。
- **Aztec 码**：`zbarimg` 不支持，用在线 `zxing.org` 或 `zxing-cpp`；Aztec 没有三个定位角，只有中心靶心。
- **DataMatrix**：注意有 L 形实线 + 时钟轨，方向靠这个判断，不要按 QR 的思路补。
- **截断的 flag**：扫出来短一截，说明是**分段多码**或高频纠错块被截，需要换更高分辨率重扫。
- **多帧 GIF**：二维码在某一帧才完整，`ffmpeg` 拆帧后逐帧扫。

## 六、参考来源

- [CTF Wiki - 杂项（编码与图片分析入口）](https://ctf-wiki.org/misc/introduction/)
- [zbar 条码/二维码识别库](https://github.com/mchehab/zbar)
- [QrazyBox - QR 码分析与重建工具](https://github.com/Merricx/qrazybox)
- [ZXing 官方（含 CLI 用法）](https://github.com/zxing/zxing)
- [Reed-Solomon 纠错与 QR 结构（Thonky 教程）](https://www.thonky.com/qr-code-tutorial/error-correction-coding)

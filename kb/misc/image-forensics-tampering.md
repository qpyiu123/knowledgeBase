---
title: 图片取证（ELA、拼接检测、重压缩与深度伪造识别）
category: misc
tags: [ela, image-forensics, splicing, deepfake, forensically, noise]
signals: [题目要求判断图片是否被篡改或者哪一块被 P 过, 图片里有一块区域的噪点明显比周围干净, 题目给了原始图和处理后图要求找差异区域, 图片里某个人脸边缘有模糊或者重影, 题目给了一张截图要求判断是不是真机拍摄, 图片分辨率很低但是细节非常锐利, 给了一批同来源图片要求逐张判断真假]
difficulty: medium
source: "FotoForensics ELA 原理 / Forensically 工具 / 深度伪造检测公开研究"
tools: [forensically, fotoforensics, imagemagick, python, exiftool, gmic]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目直接问"找出被修改的区域""这张图是原图吗"。
- 图像里某块区域**噪点几乎为 0**（纯色背景被直接贴上），或某块区域**边界有 1~2px 的虚边**。
- 人物头部/手臂边缘有"重影"或"像素拉丝"，光源方向与阴影方向不一致。
- 图片 EXIF 几乎没有（`exiftool` 只剩 Software），但分辨率极高——通常是截图或网络转载。
- 题目给了一组图（`a.png` 与 `b.png`），要求找**唯一的差异块**。
- 给了一张"新闻截图"，要求判断是不是 AI 生成或 PS 的。

## 二、原理

- **ELA（Error Level Analysis）**：把图片以固定质量（如 90）重新 JPEG 压缩一次，与原图做差并放大。**JPEG 是分块 DCT 量化**，同一次压缩的图各区域误差水平相近；二次保存或拼接进来的区块**压缩历史不同**，误差水平会显著偏离——这是 ELA 的核心假设。
- **拼接检测**：从别处拷来的区域经过不同次数的压缩/缩放，其噪声底（noise floor）与本体不同，用高通滤波 + 局部方差图可视化即可。
- **重压缩检测**：多次 JPEG 保存会在 DCT 系数直方图上留下**周期性格子**，这是比 ELA 更硬的证据。
- **深度伪造（Deepfake）**：
  - 视觉层面：眨眼频率异常、五官边缘融合痕迹、耳部/牙齿细节崩坏、背景扭曲。
  - 信号层面：GAN 上采样留下**网格状频谱峰**，可用 FFT 看频谱亮点。
  - 元数据/来源：生成器的固定尺寸（512×512、1024×1024）、没有相机 EXIF。

## 三、操作步骤

1. **元数据分析**：`exiftool -a -u -g1 -D`，看相机型号、`Software`、`DateTimeOriginal` 与 `DateTime` 是否一致。
2. **ELA**：本地 `forensically` 网页工具或用 ImageMagick 手工复现，把误差倍率调到 15~30 倍观察。
3. **噪声/高通分析**：`gmic` 或 python 做高通滤波 + 局部方差，找噪声异常区域。
4. **重压缩分析**：对可疑区域裁出，重复保存不同次数再比对 DCT 直方图（或简化用 ELA 多档质量交叉）。
5. **频谱分析**：FFT 之后取对数幅度谱，找规则网格峰。
6. **人工视觉复核**：剖面/边缘放大、光影方向一致性、克隆重复（`Forensically` 的 Clone Detection）。

## 四、命令 / 脚本

```bash
# 元数据时间线一致性
exiftool -a -u -g1 -D target.jpg | grep -iE 'date|software|model|make'
# 提取量化表（JPEG 压缩指纹）
exiftool -b -ThumbnailImage target.jpg > thumb.jpg
python - <<'EOF'
from PIL import Image
im = Image.open('target.jpg')
print('quantization tables:', im.quantization)
EOF

# 差异图（两张图对比）
compare -metric AE a.png b.png diff.png
convert a.png b.png -compose difference -composite -auto-level diff.png
```

```python
#!/usr/bin/env python3
# ELA：重压缩差值 + 放大
from PIL import Image, ImageChops, ImageEnhance
import sys

def ela(path, quality=90, scale=25):
    im = Image.open(path).convert('RGB')
    tmp = '_ela_tmp.jpg'
    im.save(tmp, 'JPEG', quality=quality)
    diff = ImageChops.difference(im, Image.open(tmp).convert('RGB'))
    return ImageEnhance.Brightness(diff).enhance(scale)

if __name__ == '__main__':
    ela(sys.argv[1]).save('ela_out.png')
    print('saved ela_out.png')
```

```python
#!/usr/bin/env python3
# 噪声底图：高通滤波 + 局部方差，定位拼接区域
import numpy as np
from PIL import Image
from scipy import ndimage
import sys

img = np.asarray(Image.open(sys.argv[1]).convert('L')).astype(np.float32)
hp = img - ndimage.gaussian_filter(img, 1.5)          # 高通
var = ndimage.generic_filter(hp, np.std, size=7)      # 局部标准差
v = (var - var.min()) / (var.ptp() + 1e-9)            # 归一化
Image.fromarray((v * 255).astype(np.uint8)).save('noise_map.png')
print('mean std=%.3f  p99=%.3f' % (var.mean(), np.percentile(var, 99)))
```

```python
#!/usr/bin/env python3
# 频谱图：GAN 上采样网格峰检测
import numpy as np
from PIL import Image
img = np.asarray(Image.open('face.png').convert('L')).astype(np.float32)
F = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(img))))
F = (F - F.min()) / (F.max() - F.min())
Image.fromarray((F * 255).astype(np.uint8)).save('spectrum.png')
```

## 五、常见坑 / 变体

- **ELA 对大块纯色背景会全白**：相机/手机拍出的纯色区域本来就平滑，ELA 高不代表篡改，要看**相对分布**而不是绝对值。
- **PNG 无压缩历史**：对 PNG 做 ELA 需要先转 JPEG，结果只对"这张图曾经过 JPEG"有意义。
- **强烈重压缩的图**：多次保存后 ELA 会整体"糊平"，此时改用 DCT 直方图的周期检测。
- **截图**：屏幕截图没有压缩残差，ELA 全区域一致，不能据此判断有无 PS；应改用图层面板/时间戳。
- **深伪检测不要只靠一个指标**：人脸边缘 + 频谱 + 元数据 + 源一致性（同批次图是否共用同一张底图）四路交叉。
- **对比题要先对齐**：两张图可能尺寸不同、JPEG 有 1~2px 偏移，先 `compare -metric AE` 再用 ECC 对齐。
- **变体**：视频抽帧做 ELA、GIF 逐帧噪声分析、恢复被裁掉的画面（越界像素在 JPEG 里仍被编码）。

## 七、补充排查清单（按成本从低到高）

1. **看 EXIF 前后矛盾**：`DateTimeOriginal`（拍摄）晚于 `DateTime`（修改）在物理上不可能，可以直接认定改过。
2. **看缩略图**：`exiftool -b -ThumbnailImage` 取出的内嵌缩略图很多 PS 软件不会同步更新，缩略图与主图不一致就是篡改铁证。
3. **看 XMP 历史**：`exiftool -xmp:all`，Adobe 系软件会写 `xmpMM:History`，能直接看到编辑动作序列。
4. **看量化表**：`PIL.Image.open(f).quantization`，与同机型样片的量化表比对，异常说明被别的软件重压过。
5. **看克隆区域**：`Forensically` 的 Clone Detection（PCA 分块）能标出几乎相同的区块，适合"复制粘贴遮盖"。
6. **看透视/比例**：地平线、人影长度、门窗透视消失点，用画线工具在图上延长判断是否自洽。
7. **看深度伪造的时间特征**：同一人物在连续帧的眨眼间隔、头部姿态跳变是否违反物理连续性。
8. **交叉验证**：把 ELA、噪声底、频谱、元数据四条证据打分后加权，单一指标异常不足以下结论，四项中有三项指向同一区域才可信。
9. **出题视角**：伪造时最常忘的是**内嵌缩略图、XMP history、DCT 系数的重压缩痕迹**，求解时优先打这三个点。
10. **输出格式**：很多题要求给出"篡改区域的左上角坐标"或"被改后的文字"，先确定提交格式再动手分析。

## 八、常见工具对照

| 工具 | 能力 | 适用场景 |
| --- | --- | --- |
| Forensically（网页） | ELA、克隆检测、噪声、放大镜、元数据 | 单人快速初筛 |
| FotoForensics | ELA + 元数据 + 评分 | 需要他人视角复核 |
| ImageMagick | 差分、裁剪、直方图 | 批量脚本化 |
| exiftool | 全元数据 dump/改写 | 找时间戳矛盾 |
| gmic | 滤波、FFT、形态学 | 自定义噪声分析 |
| python+scipy | 任意自研特征 | 批量统计与阈值判定 |

## 六、参考来源

- [FotoForensics：ELA 原理与使用说明](https://fotoforensics.com/)
- [Forensically：免费在线图像取证工具集（ELA、克隆检测、噪声）](https://29a.ch/photo-forensics/)
- [AFIP：元数据取证——EXIF 时间戳一致性分析](https://afip.org/research/metadata-forensics/)
- [Forensically 的克隆检测与误差分析思路](https://29a.ch/photo-forensics/#error-level-analysis)
- [CTF-Wiki：Misc 图片取证思路](https://ctf-wiki.org/misc/introduction/)

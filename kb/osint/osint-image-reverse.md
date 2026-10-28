---
title: 图片反查与 AI 图像指纹
category: osint
tags: [图片反查, tineye, yandex, phash, ai生成图, 图像指纹]
signals: [题目给一张图问来源, 需要找出处或原图, 需要判断是否 AI 生成, 需要找被裁切的原图, 需要比对两张图是否为同一张]
difficulty: easy
source: "CTF-Wiki 信息搜集 / TinEye 官方说明 / imagehash 文档 / OpenAI 与 Google 关于生成图像标识的说明"
tools: [tineye, yandex, google-lens, imagehash, exiftool, imagemagick, aperisolve]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一张照片，问「这张图最初出现在哪里」。
- 需要判断图片是否经过裁剪/拼接，或是否由 AI 生成。
- 给了两张相似图片，要求判断是否同源。
- 附件图片有可疑拼接痕迹（ELA 显示局部差异）。

## 二、原理

**反向图片搜索** 有三类匹配方式：
1. **精确哈希**：MD5/SHA1 完全一致（未被压缩的原图）。
2. **感知哈希（pHash/dHash/aHash/wHash）**：把图缩放成 8×8 灰度再做 DCT/差分，得到 64 bit 指纹，**抗压缩、抗轻微裁剪**。`imagehash` 的 `distance` 小于 10 通常视为同源。
3. **语义检索**：Yandex/Google Lens 把图编码为向量检索相似图，能找回**裁剪版/带水印版/同场景不同角度**。

**AI 生成图的判别线索**：
- 元数据里 `Software` 为 `Midjourney`、`Stable Diffusion`、`ComfyUI` 等；
- C2PA / IPTC 的内容凭证（`c2pa` 字段）；
- 隐写式的**生成 ID 水印**（如 Google SynthID，不可直接读出，需要官方检测器）；
- 视觉破绽：手指/文字/反射/镜面里的重复纹理、背景透视错误。

## 三、操作步骤

1. **先算指纹**：`md5sum` + `imagehash` 四算法，建立对比基线。
2. **反查**：Yandex（人脸/亚洲图强）、TinEye（精确历史）、Google Lens（覆盖面）。
3. **看元数据**：`exiftool` 找 Software/C2PA/注释；被清过就看文件头尾部残留。
4. **比对同源**：两张图缩放同尺寸后算 pHash 距离 + SSIM。
5. **AI 判定**：综合元数据 + 视觉破绽 + 官方检测器结论，**不要只凭一张图下结论**。
6. **裁剪还原**：用反查找到的原图比对尺寸差异，确定裁掉的区域。

## 四、命令/脚本

### 指纹计算与比对

```bash
pip install imagehash Pillow
python - <<'PY'
from PIL import Image
import imagehash
for f in ['a.jpg', 'b.jpg']:
    im = Image.open(f)
    print(f, im.size,
          'phash', imagehash.phash(im),
          'dhash', imagehash.dhash(im),
          'whash', imagehash.whash(im))
PY
md5sum a.jpg b.jpg; sha256sum a.jpg
```

```python
#!/usr/bin/env python3
# img_match.py —— 批量比较两张图的多种指纹，判断是否同源
import sys
from PIL import Image
import imagehash, numpy as np

def feats(path):
    im = Image.open(path)
    return {
        'phash': imagehash.phash(im),
        'dhash': imagehash.dhash(im),
        'whash': imagehash.whash(im),
        'ahash': imagehash.average_hash(im),
    }

a, b = feats(sys.argv[1]), feats(sys.argv[2])
for k in a:
    d = a[k] - b[k]                 # 汉明距离
    print(f'{k:6s} dist={d:3d}  {"同源" if d <= 10 else "不同/需人工"}')

# 像素级结构相似度（同尺寸时）
x = np.asarray(Image.open(sys.argv[1]).convert('L').resize((256, 256)), float)
y = np.asarray(Image.open(sys.argv[2]).convert('L').resize((256, 256)), float)
mx, my = x.mean(), y.mean()
cov = ((x - mx) * (y - my)).mean()
print('corr:', cov / (x.std() * y.std() + 1e-9))
```

### 元数据与生成痕迹

```bash
exiftool -a -u -g1 suspicious.jpg | grep -iE 'software|comment|artist|create|tool|generat|c2pa'
strings -n 8 suspicious.jpg | grep -iE 'midjourney|stable|comfy|dall|openai|c2pa|generator'
# C2PA 内容凭证（若有，需 c2patool）
pip install c2pa-python 2>/dev/null; c2patool suspicious.jpg 2>/dev/null | head -20
# ELA：看局部压缩噪声是否一致（不一致 = 拼接/局部编辑）
python - <<'PY'
from PIL import Image, ImageChops
im = Image.open('suspicious.jpg').convert('RGB')
im.save('re.jpg', quality=88)
d = ImageChops.difference(im, Image.open('re.jpg').convert('RGB')).point(lambda p: min(255, p * 20))
d.save('ela.png')
print('ELA 输出 ela.png：亮度越高的区域越可疑')
PY
```

### 反查入口（直接可用链接）

```bash
# Yandex：上传或给 URL
echo 'https://yandex.com/images/search?rpt=imageview&url=IMAGE_URL'
# Google Lens
echo 'https://lens.google.com/uploadbyurl?url=IMAGE_URL'
# TinEye
echo 'https://tineye.com/search?url=IMAGE_URL'
# 百度识图（中文互联网）
echo 'https://graph.baidu.com/'
# Aperi'Solve（本地隐写+元数据一次跑）
echo 'https://www.aperisolve.com/'
```

### 判断"被裁剪过"

```bash
python - <<'PY'
from PIL import Image
a = Image.open('crop.jpg'); b = Image.open('original.jpg')
print('crop size', a.size, 'original size', b.size)
# 比例是否吻合某个常见社交平台尺寸
w, h = a.size
for ratio, name in [(1, '1:1'), (16/9, '16:9'), (4/3, '4:3'), (9/16, '9:16')]:
    if abs(w / h - ratio) < 0.02:
        print('疑似被裁成', name)
PY
```

## 五、常见坑 / 变体

- **pHash 距离阈值不是绝对**：不同库/不同缩放算法结果不同，10 以内一般同源，> 20 基本不同。
- **平台重压缩**：微信/微博会重编码，精确哈希全废，感知哈希仍可用。
- **镜像/翻转**：先做水平翻转再算指纹，否则会误判为不同图。
- **裁切**：大面积裁剪会让 pHash 失真，改用特征点匹配（ORB/SIFT）。
- **AI 判定不可靠**：检测器有误报率，元数据也可能被清除，必须多证据。
- **水印**：SynthID 类不可见水印需要官方检测器，CTF 里一般给的是可读元数据/像素规律。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [imagehash - 感知哈希库文档](https://pypi.org/project/imagehash/)
- [TinEye 反向图片搜索](https://tineye.com/)
- [Yandex 图片搜索](https://yandex.com/images/)
- [Aperi'Solve（元数据与隐写一键分析）](https://www.aperisolve.com/)
- [OSINT Framework - 图片分析分类](https://osintframework.com/)

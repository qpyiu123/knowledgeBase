---
title: LSB 与频谱图分析（StegSolve / Aperi'Solve / Audacity）
category: misc
tags: [LSB, 位平面, stegsolve, aperisolve, 频谱图, Audacity]
signals: [图片位平面像随机噪声, 隐写工具都解不出, 题目提示颜色或通道, 音频听起来是杂音, 音轨静音却有波形, 文件大小正常但内容不符, 需要逐层翻位平面]
difficulty: medium
source: "Aperi'Solve 决策树 / StegSolve 用法 / Audacity 频谱教程 / LSB 隐写原理"
tools: [stegsolve, zsteg, aperisolve, audacity, sox, python-Pillow, numpy, scipy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目提示「看看每个颜色通道」「红绿蓝」。
- 图片经过 binwalk/exiftool/zsteg 全都**干净无输出**，但文件明显比同类图大。
- 音频前半段像噪声，导出频谱后能看到「字」或「二维码」。
- 一段 wav 用播放器听是空白/白噪声，但波形图上有一簇簇等距尖峰。
- 题面直接给了一句 `LSB` 或给了 `stegsolve` 的截图。

## 二、原理

**LSB（最低有效位）隐写**：把像素每个通道的 8 个比特中最低 1 位替换为密文的比特。肉眼对 ±1 的颜色变化完全无感，但把 8 个位平面**单独抽出成黑白图**，最低位平面就会显出文字/图案。

- 位平面 `bit0` 若呈**均匀随机噪声**，往往说明"确实有 LSB 隐写"（因为嵌入数据近似随机）。
- 若 `bit0` 呈**整齐条纹或有意义的图形**，通常是直接 LSB 明文写入。
- 通道顺序（RGBA）、扫描顺序（先行后列 / 列优先）、MSB/LSB、是否取反——一共有几十种组合，这就是 StegSolve 的 `Frame Browser` 存在的意义。

**频谱图**：音频是把「时间-振幅」画成波形。做 STFT 后得到「时间-频率」图，人耳听不见的高频（>16 kHz）是常见的隐形画布——出题人把文字/二维码绘制在 15~22 kHz 频段，播放时听起来像杂音，但频谱图一眼可见。

**Aperi'Solve**：把 zsteg / steghide / outguess / exiftool / binwalk / foremost / 位平面图 / 通道图 / LSB 预览等几十种分析**一次性并行跑完**并给出可视结果，是图像题第一站。

## 三、操作步骤

1. **先上 Aperi'Solve**：上传图片，等它跑完，重点看 `zsteg`、`Bit planes`、`Random color map`、`Extra data after EOF`。
2. **本地 StegSolve**：`File → Open`，`Analyse → Frame Browser`，逐帧翻 R/G/B/A 的 8 个位平面。
3. **发现图案后逆推**：确定通道和位序 → 用 Python 脚本把该平面导出，再按 8 位一组拼字节。
4. **音频**：Audacity 导入 → 切到 `Spectrogram` 视图，调 `Window size = 2048/4096`，`Export` 保存。
5. **频率反常**：`sox` 生成 PNG 频谱，或用 `spek` 看整体频段分布。
6. **确认内容**：导出的图 / 字节流先 `file`，再 `strings`、`zbarimg`（二维码）。

## 四、命令/脚本

### Aperi'Solve / StegSolve

```bash
# Aperi'Solve 是 Web 平台，命令行等价物如下
zsteg -a target.png
zsteg -E 'b1,rgb,lsb,xy' target.png > plane_b1.bin
# StegSolve 需要 Java：
java -jar Stegsolve.jar
#    Analyse -> Data Extract -> 勾选 RGB 的 B1，预览里直接看文本/图片
#    Analyse -> Stereogram Solver / Frame Browser / Random Color Map
```

### 手工抽位平面（Pillow）

```python
#!/usr/bin/env python3
# lsb_plane.py —— 抽出任意通道/任意位的平面，并尝试按 8bit 拼字节
from PIL import Image
import sys, numpy as np

path, bit, chans = sys.argv[1], int(sys.argv[2]), sys.argv[3]  # chans 例 "rgb"
im = Image.open(path).convert('RGBA')
arr = np.array(im)
idx = {'r': 0, 'g': 1, 'b': 2, 'a': 3}
planes = [((arr[:, :, idx[c]] >> bit) & 1) for c in chans]
out = (np.stack(planes, -1) * 255).astype(np.uint8)
Image.fromarray(out).save(f'plane_bit{bit}_{chans}.png')

bits = np.array(planes).flatten()
bits = bits[: len(bits) // 8 * 8].reshape(-1, 8)
data = np.packbits(bits, axis=1).tobytes()
open(f'plane_bit{bit}_{chans}.bin', 'wb').write(data)
print('bytes:', len(data), 'head:', data[:48])
```

```bash
python lsb_plane.py target.png 0 rgb && file plane_bit0_rgb.bin
strings -n 5 plane_bit0_rgb.bin | head
```

### 行优先 / 列优先 / 位序反转

```python
#!/usr/bin/env python3
# lsb_variants.py —— 组合若干常见顺序，只为寻找 flag 前缀
from PIL import Image
import numpy as np, itertools
im = Image.open('target.png').convert('RGBA')
a = np.array(im)
def bits_of(chan, bit):
    return ((a[:, :, chan] >> bit) & 1)
for (bit, chan, order, rev) in itertools.product(
        range(2), ['rgba', 'argb'], ['xy', 'yx'], [False, True]):
    m = np.stack([bits_of('rgba'.index(c), bit) for c in chan], -1)
    if order == 'yx':
        m = m.transpose(1, 0, 2)
    flat = m.flatten()
    if rev:
        flat = flat[::-1]
    flat = flat[:len(flat)//8*8].reshape(-1, 8)
    d = np.packbits(flat, axis=1).tobytes()
    if b'flag' in d or b'CTF' in d:
        print('HIT', bit, chan, order, rev)
        print(d[:200])
```

### 音频频谱图

```bash
sox target.wav -n spectrogram -o spec.png -X 2000 -Y 1025 -z 90
# -X 时间跨度(px/s) -Y 频率高度 -z 增益(dB)，观察 >16kHz 区域
ffprobe -v error -show_streams target.wav     # 采样率/位深/声道数
sox target.wav -n stat                        # 统计信息
```

```python
#!/usr/bin/env python3
# spec_hi.py —— 只画 15kHz 以上频段（常见藏字区域）
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal

sr, x = wavfile.read('target.wav')
if x.ndim > 1:
    x = x[:, 0]
f, t, Sxx = signal.spectrogram(x.astype(float), sr, nperseg=4096)
plt.figure(figsize=(14, 5))
plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-12), shading='auto', cmap='magma')
plt.ylim(min(15000, sr / 2 * 0.7), sr / 2)
plt.ylabel('Hz'); plt.xlabel('s')
plt.savefig('spec_hi.png', dpi=160, bbox_inches='tight')
print('saved spec_hi.png, nyquist =', sr / 2)
```

### 双声道差分（「相加成单声道就没声」的题）

```bash
sox target.wav left.wav remix 1
sox target.wav right.wav remix 2
sox -m -v 1 left.wav -v -1 right.wav diff.wav    # 相减
sox diff.wav -n spectrogram -o diff_spec.png -X 2000
```

## 五、常见坑 / 变体

- **别只看 RGB LSB**：alpha 通道、MSB、列优先、取反，这四类占「zsteg 无结果」的绝大多数。
- **StegSolve 的 Data Extract** 输出模式有 `Hex / Text / Image`，切换成 Image 才看得出图案。
- **索引色（调色板）图**：位平面分析基本失效，改走调色板重排路线。
- **音频 LSB 不从第 0 个采样开始**：要跳过 WAV 头（44 字节），并试 `-n 1/-n 2` 两种位深。
- **WAV 头 DataSize 被改小**：`sox` 只能读到改小的长度，需先把头里的 DataSize 改回真实值再分析。
- **频谱图默认参数太糊**：Audacity 里把 `Window size` 提到 4096、`Gain` 拉到 20 以上，高频小字才能看清。
- **视频里藏图**：`ffmpeg` 抽帧后对每帧跑 PNG 流程，或直接看声道频谱。

## 六、参考来源

- [Aperi'Solve 速查表（位平面与通道决策）](https://www.aperisolve.com/cheatsheet)
- [Aperi'Solve 在线平台](https://www.aperisolve.com/)
- [zsteg：PNG/BMP 多组合 LSB 检测](https://github.com/zed-0xff/zsteg)
- [SoX 官方站（spectrogram/remix 效果）](https://sox.sourceforge.net/)
- [Audacity 频谱视图教程](https://manual.audacityteam.org/man/spectrogram_view.html)
- [CTF Wiki - 音频隐写](https://ctf-wiki.org/misc/audio/introduction/)

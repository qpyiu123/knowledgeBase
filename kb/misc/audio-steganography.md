---
title: 音频隐写（频谱/DTMF/莫尔斯/LSB/SSTV）
category: misc
tags: [音频, wav, 频谱图, DTMF, 莫尔斯, LSB]
signals: [附件是 wav 或 mp3, 音频里有嘀嘀声, 音频听起来像杂音, 播放时有规律的嘟嘟声, 题面说听一听, 波形图有等距方波, 立体声左右不同]
difficulty: medium
source: "CTF-Wiki 音频隐写 / Aperi'Solve audio checklist / Audacity 手册 / SoX 文档"
tools: [audacity, sox, ffmpeg, sonic-visualiser, multimon-ng, minimodem, stegolsb, qsstv]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `music.wav`，题面说「仔细听」「这不是一首歌」。
- 播放时听到**短促的嘀嘀**（摩斯）或**电话按键声**（DTMF）。
- 整段是白噪声/杂音，但**波形图很规律**。
- 左右声道分别听一边，区别明显（差分藏数据）。
- 文件名里带 `spectrogram`、题名「眼睛看不见的声音」。

## 二、原理

音频比图片多一个维度：**时间-频率**。常见藏法：

| 手法 | 表现 | 工具 |
| --- | --- | --- |
| 频谱绘图 | 频谱图上直接画字/二维码，常在 15~22 kHz | Audacity / SoX / Sonic Visualiser |
| 摩斯 | 嘀（.）嗒（-）时长分明 | 耳朵 / `multimon-ng -a MORSE` |
| DTMF | 双音频键音 | `multimon-ng -a DTMF` / `dtmf2num` |
| FSK/调制解调 | 类似拨号上网音 | `minimodem` / `multimon-ng` |
| SSTV | 图像在 1100~2300 Hz 慢扫描 | QSSTV |
| WAV LSB | 采样值最低位藏数据 | `stegolsb wavsteg` |
| 双声道差分 | 左右相减出现信号 | SoX `remix` + 相减 |
| WAV 头篡改 | 文件头里的 data 长度被改小 | 手工修复 |

**WAV 结构**：`RIFF(4) size(4) WAVE(4)` + `fmt ` chunk(24) + `data` chunk（8 字节头 + 采样数据）。`data` chunk 的长度字段常被出题人改小，导致播放器只放出一小段——把长度改回真实值就能听到"被藏起来"的部分。

## 三、操作步骤

1. **先看频谱**：Audacity → 切 `频谱图` 视图，`Window size` 设 4096，`Gain` 提高，扫一遍全频段（特别注意 0~100 Hz 和 15 kHz 以上）。
2. **听波形**：找等距脉冲 → 摩斯；找两个持续音交替 → DTMF。
3. **声道分离**：左/右单独导出，再按"相加成单声道就没声"的线索做相减。
4. **LSB 提取**：`stegolsb wavsteg -r`，注意跳过 WAV 头。
5. **检查文件头**：`ffprobe` 的时长与文件大小是否匹配（48kHz 16bit 单声道 2 秒约 192KB）。
6. **恢复出的内容继续套娃**：文本 → base64；图片 → PNG 隐写流程。

## 四、命令/脚本

### 频谱图（第一优先）

```bash
sox target.wav -n spectrogram -o spec.png -X 2000 -Y 1025 -z 90
# -X 时间像素/秒  -Y 频域分辨率  -z 动态范围(dB)
ffmpeg -i target.wav -lavfi showspectrumpic=s=1920x1080:legend=1 spec2.png
# Audacity 手动：音轨菜单 -> 频谱图 -> 首选项里改 window size 4096 / 对数刻度 / range 80dB
```

```python
#!/usr/bin/env python3
# spec_all.py —— 生成全频段 + 15kHz 以上的两张频谱
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
sr, x = wavfile.read('target.wav')
if x.ndim > 1:
    x = x[:, 0]
f, t, S = signal.spectrogram(x.astype(float), sr, nperseg=4096)
for lo, name in [(0, 'spec_full.png'), (15000, 'spec_hi.png')]:
    plt.figure(figsize=(16, 5))
    plt.pcolormesh(t, f, 10*np.log10(S+1e-12), shading='auto', cmap='magma')
    plt.ylim(lo, sr/2); plt.ylabel('Hz'); plt.xlabel('s')
    plt.savefig(name, dpi=150, bbox_inches='tight'); plt.close()
print('nyquist', sr/2)
```

### DTMF / 摩斯 / 调制

```bash
sox target.wav dtmf.wav trim 0 =5            # 截取前 5 秒便于分析
multimon-ng -t wav -a DTMF -a MORSE_CW -a EAS -a FMSFSK -a AFSK1200 dtmf.wav
sox target.wav -n stat 2>&1 | grep -i 'maximum amplitude'
minimodem --rx 1200 -f target.wav            # 若是 1200bps 调制解调
```

```python
#!/usr/bin/env python3
# morse_decode.py —— 按能量阈值把 WAV 转成 0/1，再按停顿时长切分到 . - /
import numpy as np
from scipy.io import wavfile
sr, x = wavfile.read('target.wav')
x = x.astype(float)
if x.ndim > 1:
    x = x[:, 0]
env = np.abs(x)
thr = env.max() * 0.2
on = env > thr
runs, cur, val = [], 1, bool(on[0])
for b in on[1:]:
    b = bool(b)
    if b == val:
        cur += 1
    else:
        runs.append((val, cur)); val, cur = b, 1
runs.append((val, cur))
unit = min(c for v, c in runs if v) if any(v for v, c in runs) else 1
out = []
for v, c in runs:
    n = max(1, round(c / unit))
    if v:
        out.append('.' if n == 1 else '-' if n >= 3 else '.')
    else:
        out.append('' if n == 1 else '/' if n >= 3 else ' ')
print(''.join(out)[:2000])
```

### WAV LSB 与双声道

```bash
pip install stegolsb
stegolsb wavsteg -r -i target.wav -o out.txt -n 1 -b 1000   # 按 1000 字节尝试
stegolsb wavsteg -r -i target.wav -o out2.txt -n 2 -b 1000  # 每采样 2 bit
# 双声道
sox target.wav L.wav remix 1
sox target.wav R.wav remix 2
sox -m -v 1 L.wav -v -1 R.wav minus.wav
sox minus.wav -n spectrogram -o minus_spec.png -X 2000
```

### 修复被改小的 data 长度

```python
#!/usr/bin/env python3
# wav_fix.py —— 把 data chunk 的 size 字段改回文件实际长度
import struct, sys
d = bytearray(open(sys.argv[1], 'rb').read())
i = d.find(b'data')
assert i > 0, 'no data chunk'
real = len(d) - (i + 8)
old = struct.unpack('<I', d[i+4:i+8])[0]
struct.pack_into('<I', d, i+4, real & 0xffffffff)
struct.pack_into('<I', d, 4, (len(d) - 8) & 0xffffffff)   # RIFF size
open(sys.argv[1].replace('.wav', '_fixed.wav'), 'wb').write(d)
print(f'data size {old} -> {real}; RIFF size fixed')
```

### SSTV

```bash
# 用 QSSTV 或 MMSSTV，配置虚拟声卡 loopback
ffplay -f s16le -ar 44100 target.wav &
qsstv                     # 设置里选 "Soundcard input = Monitor of ..."
```

## 五、常见坑 / 变体

- **采样率/位深不明**：`ffprobe` 先确认，`stegolsb -n 1` 与 `-n 2` 都试。
- **LSB 输出全是 0**：说明起始偏移不对，跳过前 N 个采样（`sox target.wav trim 0.1` 再试）。
- **频谱图看不到字**：调 `Window size` 到 2048/8192，切对数刻度，range 拉到 80~100dB，另外查 0~200Hz 的极低频。
- **MP3 有损**：高频内容会被编码器切掉，**几乎不可能是频谱藏字的载体**，题目给 mp3 时优先怀疑 ID3 标签、尾部追加数据。
- **双声道相加归一**：相减后信号太弱，用 SoX `gain -n` 归一化再看频谱。
- **SSTV 不是 1200bps 调制**：别用 minimodem 解 SSTV，它频率是 1100~2300Hz 的连续调频。
- **视频音轨**：`ffmpeg -i video.mp4 -vn audio.wav` 后再走全套流程。

## 六、参考来源

- [CTF Wiki - 音频隐写](https://ctf-wiki.org/misc/audio/introduction/)
- [Aperi'Solve 速查表（Audio 分支与工具对照）](https://www.aperisolve.com/cheatsheet)
- [SoX 官方站（spectrogram/remix/trim 用法）](https://sox.sourceforge.net/)
- [Audacity 频谱视图文档](https://manual.audacityteam.org/man/spectrogram_view.html)
- [multimon-ng 支持的解码协议列表](https://github.com/EliasOenal/multimon-ng)
- [Sonic Visualiser 音频分析工具](https://www.sonicvisualiser.org/)

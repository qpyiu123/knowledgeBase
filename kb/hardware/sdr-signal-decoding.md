---
title: 无线电进阶（SDR、ASK/FSK 解码、sigidwiki 识别）
category: hardware
tags: [sdr, ask, fsk, gnuradio, sigidwiki, rf]
signals: [附件是一个 iq 采样文件或者 wav 里录了射频声音, 题目给的频率是 433.92MHz 或者 315MHz, 需要在频谱图里找出一段周期性突发信号, 提示说这是 ask 或者 ook 调制, 给了 .wav 文件播放时是哒哒声, 题目要求还原遥控器发出的按键码]
difficulty: hard
source: "GNU Radio 官方教程 / sigidwiki 信号识别指南 / rtl-sdr.com 文档"
tools: [gnuradio, urh, universal-radio-hacker, rtl_433, inspectrum, audacity, python]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.wav`（I/Q 两声道录制）或 `.raw`/`.cu8` 采样，采样率几十 kSps 到 2 MSps。
- 题面给出中心频率（`433.92 MHz`）或说"遥控器频率"。
- 要求"从录音里还原按下的键"或"还原传输的数据帧"。
- 频谱图上有周期性窄带突发（burst），间隔约几百 ms。
- `inspectrum` 打开能看到清晰的 OOK 波形（高低电平）。
- 提示提到 `EV1527`、`PT2262`、`PWM`、`OOK`、`Manchester`。

## 二、原理

**SDR 录的是 I/Q 基带采样**：每个采样是复数 `I + jQ`，信号的瞬时频率 = `arg(s[n])` 的差分，幅度 = `|s|`。

**常见低功耗遥控调制：**

| 调制 | 特征 | 解码方式 |
| --- | --- | --- |
| **OOK/ASK** | 有信号 = 幅度 1，无信号 = 0 | 幅度包络 → 阈值 → 脉宽 |
| **FSK** | 两个频率交替 | 瞬时频率 → 正负 → 位流 |
| **PWM（EV1527/PT2262）** | 用脉宽比表示 0/1（如 1:3 与 3:1） | 测每段脉宽分类 |
| **Manchester** | 每 bit 中跳变，上升=1/下降=0 | 采样中点判断 |
| **差分 Manchester** | 依据跳变而非电平 | 先微分再判断 |

**EV1527**：24 bit（20 位地址 + 4 位按键），每位用"短脉冲 + 长间隔"或"长脉冲 + 短间隔"编码，同步码是 1:31 的长间隔。

**识别流程**：频段（315/433/868/915 MHz）→ 调制（看频谱宽度：OOK 很窄且突发，FSK 两峰）→ 编码（脉宽比）→ 位流 → 语义。

## 三、操作步骤

1. **确认采样格式**：`.cu8`（uint8 IQ）、`.cs16`、`.wav`（左右声道 I/Q）、`.raw`（int16）。
2. **看频谱找突发**：`inspectrum` 或 GNU Radio 的 `QT GUI Frequency Sink`，定位突发间隔与带宽。
3. **包络提取**：幅度 `sqrt(I^2+Q^2)`，用阈值二值化，得到时间轴上的 0/1 段。
4. **测脉宽**：统计每段的持续采样数，聚类出"短/长"两类。
5. **按编码规则还原位流**：PWM 按脉宽比，Manchester 按中点电平。
6. **解码语义**：EV1527 的 20 位地址 + 4 位按键，或直接按题给的协议说明拼字节。
7. **交叉验证**：用 `rtl_433` 或 URH 自动识别一遍。

## 四、命令 / 脚本

```bash
# rtl_433 自动识别（有硬件时）
rtl_433 -f 433.92M -s 250k -A
# inspectrum 打开采样
inspectrum -r 250000 capture.cu8
# URH（Universal Radio Hacker）图形化分析
urh
# GNU Radio 里的通用流程
# File Source -> Frequency Xlating FIR Filter -> Complex to Mag -> Threshold -> Binary Slicer
```

```python
#!/usr/bin/env python3
# 从 .cu8 采样里解出 OOK 脉宽，再按 PWM 规则还原位流
import numpy as np, sys

def load_cu8(path):
    raw = np.fromfile(path, dtype=np.uint8).astype(np.float32)
    raw -= 127.5
    iq = raw[0::2] + 1j * raw[1::2]
    return iq

def envelope_bits(iq, thresh_ratio=0.5):
    mag = np.abs(iq)
    th = mag.max() * thresh_ratio
    return (mag > th).astype(np.uint8)

def runs(bits):
    idx = np.flatnonzero(np.diff(bits) != 0) + 1
    seg = np.split(bits, idx)
    return [(int(s[0]), len(s)) for s in seg]

def decode_pwm(segments):
    widths = sorted({w for _, w in segments})
    # 以最小值作为"短"单位
    short = min(widths)
    out = []
    i = 0
    while i + 1 < len(segments):
        level, w = segments[i]
        ratio = w / short
        # EV1527: 1 个短电平 + 3 个短间隔 => 0；3 个短电平 + 1 个短间隔 => 1
        if level == 1:
            nxt = segments[i + 1][1] / short
            bit = 0 if ratio < 2 and nxt > 2 else (1 if ratio > 2 and nxt < 2 else None)
            if bit is not None:
                out.append(bit)
                i += 2
                continue
        i += 1
    return out

if __name__ == '__main__':
    iq = load_cu8(sys.argv[1])
    b = envelope_bits(iq)
    segs = runs(b)
    print('段数=%d 最长段=%d' % (len(segs), max(w for _, w in segs)))
    bits = decode_pwm(segs)
    print(''.join(map(str, bits)))
    # 每 24 bit 一组
    s = ''.join(map(str, bits))
    for i in range(0, len(s) - 23, 24):
        print('frame', hex(int(s[i:i+24], 2)))
```

```python
#!/usr/bin/env python3
# FSK：按瞬时频率正负解位
import numpy as np, sys
iq = np.fromfile(sys.argv[1], dtype=np.int16).astype(np.float32)
z = iq[0::2] + 1j * iq[1::2]
inst = np.angle(z[1:] * np.conj(z[:-1]))
bits = (inst > 0).astype(np.uint8)
print(''.join(map(str, bits[:200])))
```

```bash
# wav 形式的 I/Q（左右声道）
sox cap.wav -t raw -r 250k -e signed -b 16 cap.raw
python -c "
import numpy as np
d = np.fromfile('cap.raw', dtype=np.int16).astype(float)
i, q = d[0::2], d[1::2]
print('samples', len(i), 'rms', np.sqrt((i**2+q**2).mean()))
"
```

## 五、常见坑 / 变体

- **I/Q 顺序反了**：有些工具是 I 在前，有些是 Q 在前，反了频谱会镜像；看 FSK 时会导致位序全反。
- **采样率不足**：OOK 的脉宽 ~200µs 对应 5kHz 带宽，采样 250kSps 足够；但太低会让短脉冲被"抹平"。
- **AGC/自动增益**：录制时开了 AGC，幅度忽大忽小，阈值二值化会失效——用自适应阈值（滑窗均值）。
- **直流偏置**：`|s|` 有基线偏移，先减均值再取包络。
- **帧重复**：遥控器一般重复发 3~5 帧，取其中一帧解即可，重复帧可做校验。
- **频段法规**：315/433/868/915 MHz，题目给错频率解不出任何东西时先确认频段。
- **变体**：LoRa（chirp 扩频，需 gr-lora）、BLE（跳频 + GFSK，需 Sniffle/ubertooth）、zigbee（DSSS）。

## 六、参考来源

- [Signal Identification Wiki：按波形与频谱识别射频信号](https://www.sigidwiki.com/wiki/Signal_Identification_Guide)
- [RTL-SDR 官方博客：信号识别指南与工具链](https://www.rtl-sdr.com/new-signal-identification-guide-wiki/)
- [Universal Radio Hacker 官方文档（解调与协议分析）](https://github.com/jopohl/urh)
- [GNU Radio 官方教程（IQ 处理与整流）](https://github.com/gnuradio/gnuradio)
- [inspectrum：时频域可视化与解调](https://github.com/miek/inspectrum)

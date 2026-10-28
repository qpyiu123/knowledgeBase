---
title: 故障注入（电压毛刺 glitch、时钟毛刺与绕过比对）
category: hardware
tags: [fault-injection, voltage-glitch, clock-glitch, chipwhisperer, crowbar, bypass]
signals: [题目要求通过让芯片在特定时刻出错来跳过校验, 板子上有一颗 LGT8F 或 STM32 且需要解出密钥, 提示提到 glitch 或 fault 或 crowbar, 附件是 chipwhisperer 的 notebook, 需要找到正确的毛刺延迟和宽度参数组合, 芯片会在复位后读一遍 UART 输入然后比对]
difficulty: hard
source: "ChipWhisperer 官方教程（Fault101）/ NewAE 论坛 / 硬件安全公开课程"
tools: [chipwhisperer, cw305, pico-crowbar, python, oscilloscope]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目描述"设备反复读取输入并校验，需要让它在校验时出错"。
- 附件含 `fault101`、`glitch` 字样的 Jupyter notebook 或 `.py` 脚本。
- 板上有一颗小芯片（LGT8F328P、ATmega、STM32F0），用 UART 交互。
- 提示里出现 `crowbar`、`VBAT`、`width`、`offset` 这些参数名。
- 要求"找到能通过校验的 (offset, width) 组合"。
- 有 ChipWhisperer-Lite/Nano 硬件，或题目给了毛刺波形图。

## 二、原理

**故障注入本质是"用物理手段让 CPU 算错一步，从而跳过校验"。**

| 方式 | 手段 | 打哪里 | 效果 |
| --- | --- | --- | --- |
| **电压毛刺（glitch）** | 用 MOSFET 短路 VCC 几十~几百 ns | 电源引脚/芯片 | 指令流跑飞、跳过分支 |
| **时钟毛刺** | 在时钟上插入一个超短脉冲 | 外部时钟输入 | 打乱流水线，单条指令错位 |
| **电磁注入（EMFI）** | 线圈脉冲耦合 | 芯片上方 | 类似电压毛刺，无需接触 |
| **激光注入（LFI）** | 激光打在 SRAM/Flash | 去封装芯片 | 位翻转，精度最高 |

**CTF 里最常见的是"STM8/LGT8F 的读保护绕过"**——经典思路：
1. 芯片上电时会读 `option bytes`/flash 中的 `RDP` 位判断是否允许读。
2. 在读取 RDP 位的那一两个时钟周期内，用 `crowbar` 把 VCC 拉低几十 ns。
3. 芯片读到错误的值（RDP 被判为 0 == 未保护），从而开启调试口。
4. 参数搜索：`ext_offset`（从复位/触发信号后多少时钟开始毛刺）× `width`（拉低多久），逐个组合试。

**为什么参数搜索可行**：目标行为对参数是"窄窗口成功"——窗口外的组合完全正常，窗口内的组合跳过校验。所以暴力扫一遍即可。

## 三、操作步骤

1. **确定触发时机**：UART 发命令后的固定时钟数，或 GPIO 翻转沿；用示波器抓正常波形确定 `ext_offset` 范围。
2. **搭 crowbar**：MOSFET 的 D 接 VCC、S 接 GND、G 接 ChipWhisperer 的 glitch 输出。
3. **单次试打**：先固定 `width`，扫 `ext_offset`（步进 1 个时钟），看设备是否还活着。
4. **二维扫**：`offset × width` 网格，记录每个组合的结果（正常/崩溃/绕过成功）。
5. **加密间隔**：每两次尝试之间要完全断电重上电（`reset` + 延时），否则状态残留。
6. **成功后 dump**：一旦调试口打开，立刻 `read` 出 flash。

## 四、命令 / 脚本

```python
#!/usr/bin/env python3
# ChipWhisperer 电压毛刺参数扫描骨架
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI
import time

api = CWCoreAPI()
api.setParameter('scope_gain', 30)
api.setParameter('scope_offset', 1.34)
api.setParameter('scope_trigger', 'ext_single')
api.setParameter('scope_samplerate', '50MHz' if False else '48MHz')
api.setParameter('glitch_enabled', True)
api.setParameter('glitch_ext_trigger', 'GPIO4')      # 目标发信号表示"开始校验"
api.setParameter('glitch_trigger', 'ext_single')
api.setParameter('glitch_output', 'glitch_only')
api.setParameter('glitch_clk_src', 'clkgen')

def attempt(offset, width):
    api.setParameter('glitch_ext_offset', offset)     # 单位：时钟周期
    api.setParameter('glitch_width', width)           # 单位：时钟周期（如 48MHz 下 1 = 20.8ns）
    api.setParameter('glitch_repeat', 1)
    api.capture(arm=True)
    return api.getLastTrace()

results = []
for width in range(1, 8):
    for offset in range(0, 60):
        try:
            attempt(offset, width)
            ok = check_success()                       # 读目标输出判断是否通过校验
        except Exception:
            ok = None
        results.append((offset, width, ok))
        if ok:
            print('[+] 成功 offset=%d width=%d' % (offset, width))
            break

# 打印成功区域
for r in results:
    print(r)
```

```python
#!/usr/bin/env python3
# 结果可视化：把 (offset, width) 网格画成热力图
import matplotlib.pyplot as plt
import numpy as np

def heat(rows):
    xs = sorted({r[0] for r in rows}); ys = sorted({r[1] for r in rows})
    m = np.zeros((len(ys), len(xs)))
    for x, y, ok in rows:
        m[ys.index(y)][xs.index(x)] = 2 if ok else (1 if ok is None else 0)
    plt.imshow(m, origin='lower', cmap='viridis')
    plt.xlabel('ext_offset'); plt.ylabel('width')
    plt.colorbar(); plt.savefig('glitch_heatmap.png')

heat(results)
```

```python
#!/usr/bin/env python3
# 简易 crowbar 控制（用 pico + 微秒级脉冲）——没有 CW 硬件时的替代
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.2)

def pulse(width_us):
    ser.write(b'G%d\n' % width_us)
    ser.read_until(b'OK\n')

for w in (10, 20, 30, 40, 50):
    pulse(w)
    time.sleep(0.5)
    print('width=%dus' % w, ser.read(128))
```

```bash
# 目标端的触发固件（跑在 CTF 板上）：校验前拉高 GPIO4
# 省略：一般题目会提供 .hex，把它烧进目标板
avrdude -c usbasp -p m328p -U flash:w:target.hex:i
```

## 五、常见坑 / 变体

- **别只扫一维**：成功窗口往往是斜线而非矩形，`offset` 固定只扫 `width` 容易漏。
- **电源电容太大**：板上的去耦电容会"吃掉"毛刺，需要在测试点就近打，或断开电容。
- **重复尝试不做冷启动**：芯片状态残留导致后续尝试全是假阳性，每次尝试前 `reset` + 200ms 延时。
- **电压毛刺幅度**：拉得太低会复位（无法区分），太高无效；先做"death test"确定可靠复位阈值。
- **时钟毛刺更适合无外部电源控制的目标**：直接给 CLK 引脚发短脉冲，不需要动 VCC。
- **ChipWhisperer 的 `width` 单位是时钟周期**：在 48MHz 下 1 个周期 ≈ 20.8ns，别按 ns 填。
- **变体**：EMFI（ChipSHOUTER）、激光注入、ROM 读保护绕过（STM32 RDP 1 → 2 的 glitch）。

## 六、参考来源

- [ChipWhisperer Fault101 教程：时钟毛刺入门](https://github.com/newaetech/chipwhisperer-jupyter)
- [NewAE 论坛：CW305 上的时钟/电压毛刺实现讨论](https://forum.newae.com/t/how-to-implement-the-clock-and-voltage-glitch-fault-attack-on-the-cw305-fpga-board/2414)
- [ChipWhisperer 官方文档（glitch 模块参数）](https://chipwhisperer.readthedocs.io/en/latest/)
- [36C3：TrustZone-M(eh) — 用毛刺绕过安全启动与 AES](https://www.youtube.com/watch?v=4u6BAH8mEDw)
- [Riscure 公开材料：故障注入的建模与参数搜索](https://github.com/Riscure)

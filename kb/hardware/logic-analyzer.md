---
title: 逻辑分析仪（UART/SPI/I2C 波形解码）
category: hardware
tags: [逻辑分析仪, saleae, sigrok, pulseview, uart, spi]
signals: [给了一段波形文件, 附件是 .sal 或 .sr 或 .logicdata, 题目说从总线抓了数据, 需要还原串口输出, 需要解码 I2C 寄存器, 波形里有周期时钟和数据线]
difficulty: medium
source: "Saleae 支持文档 / sigrok 协议解码文档 / I2C 概览（i2c.info）"
tools: [logic2, pulseview, sigrok-cli, minicom, python-serial, fx2lafw]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.sr`（sigrok）、`.sal`（Saleae）、`.logicdata` 等**波形文件**，不是二进制。
- 题目说「从设备的总线上抓到了这些信号」。
- 波形里有两根线：一条周期方波（SCLK），一条不规则（MOSI/MISO）→ SPI。
- 两根线都有周期方波（SCL/SDA），SDA 在 SCL 高电平期间变化 → I2C。
- 一根线上是长短不一的脉冲，像 ASCII 串口（UART）。
- 解码结果里出现 `flag{` 或 `CTF`。

## 二、原理

**逻辑分析仪** 按固定采样率记录每条通道的高/低电平。解码就是把电平序列按协议规则还原成字节：

| 协议 | 线 | 同步方式 | 关键参数 |
| --- | --- | --- | --- |
| UART | TX/RX | 异步 | **波特率**、位序（LSB first）、数据位 8、停止位 1、无校验 |
| SPI | SCLK/MOSI/MISO/CS | 同步 | **CPOL/CPHA**（模式 0~3）、位序、CS 极性 |
| I2C | SCL/SDA | 同步 | 7/10 位地址、起始/停止条件、ACK |
| 1-Wire | DQ | 异步 | 复位脉冲 + 时隙 |

**波特率估算**：量一个比特的最短宽度 `w`（秒），波特率 ≈ `1/w`。常见 9600/115200/921600。

**SPI 模式判定**：
- `CPOL=0`：SCLK 空闲为低；`CPHA=0`：在**第一个边沿**（上升沿）采样。
- 拿不准时 4 个模式全解一遍，哪个输出像 ASCII 就是哪个。

## 三、操作步骤

1. **打开波形**：PulseView 或 Saleae Logic 2。
2. **看时间跨度**：如果是秒级采样而设备是 kHz 通信，可能被严重降采样，需要看原始采样率。
3. **加解码器**：UART/SPI/I2C，先填最可能的参数。
4. **调参**：UART 依次试 9600→115200；SPI 依次试 4 种模式；I2C 试地址位宽。
5. **读结果**：解码器在时序图上会标注每个字节，导出为文本。
6. **拼接**：多字节消息按顺序拼成字符串，`flag` 通常在最后。

## 四、命令/脚本

### Saleae Logic 2（GUI / CLI）

```bash
# Logic 2 有 headless 模式（需安装 Logic 2 并用 automation API）
# 更简单：GUI 打开 .sal -> Analyzers -> 添加 Async Serial / SPI / I2C
# 导出：Analyzers 面板 -> 右键 -> Export -> Text/CSV
```

### PulseView + sigrok（跨平台、免费）

```bash
sudo apt install -y sigrok-cli pulseview
pulseview &                       # GUI：File -> Open -> 选 .sr
# CLI 直接解码并输出
sigrok-cli -i capture.sr -P uart:baudrate=115200:rx=D0 -A uart
sigrok-cli -i capture.sr -P uart:baudrate=9600:rx=D0:format=hex -A uart
sigrok-cli -i capture.sr -P spi:clk=D0:mosi=D1:miso=D2:cs=D3 -A spi
sigrok-cli -i capture.sr -P i2c:scl=D0:sda=D1 -A i2c
# 列出可用解码器
sigrok-cli -L | grep -iE 'uart|spi|i2c|can|jtag'
```

### 实战：UART 波特率自动搜

```bash
for br in 1200 2400 4800 9600 19200 38400 57600 115200 230400 460800 921600; do
  out=$(sigrok-cli -i capture.sr -P uart:baudrate=$br:rx=D0 -A uart 2>/dev/null | tr -d '\n')
  echo "$br: $out" | head -c 300
  echo "$out" | grep -qiE 'flag|ctf|login' && echo "  <== HIT $br"
done
```

### 实战：SPI 四模式扫

```bash
for mode in 0 1 2 3; do
  echo "=== CPOL/CPHA mode $mode"
  sigrok-cli -i capture.sr -P "spi:clk=D0:mosi=D1:miso=D2:cs=D3:cpol=$((mode/2)):cpha=$((mode%2))" \
    -A spi 2>/dev/null | head -20
done
```

### 手工解码（不信任工具时）

```python
#!/usr/bin/env python3
# uart_manual.py —— 从 CSV 采样的电平序列手工解 UART
import csv, sys

rate = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000   # 采样率 Hz
samples = []
with open(sys.argv[1]) as f:
    for row in csv.reader(f):
        if len(row) >= 2 and row[0].isdigit():
            samples.append(int(row[1]) & 1)

# 找下降沿（起始位）：高 -> 低
edges = [i for i in range(1, len(samples)) if samples[i-1] == 1 and samples[i] == 0]
print('edges:', len(edges), 'samples:', len(samples))

def decode(b0, baud):
    spb = rate / baud
    bits = []
    for k in range(1, 9):                       # 跳过起始位
        idx = int(b0 + spb * (k + 0.5))         # 采样点取每位中点
        if idx >= len(samples):
            return None
        bits.append(samples[idx])
    val = sum(b << i for i, b in enumerate(bits))   # LSB first
    stop_idx = int(b0 + spb * 9.5)
    stop = samples[stop_idx] if stop_idx < len(samples) else 1
    return val if stop == 1 else None

for baud in (9600, 115200):
    txt = ''
    for e in edges:
        c = decode(e, baud)
        if c is not None and 32 <= c < 127:
            txt += chr(c)
    print(baud, '->', txt[:200])
```

### 用 Python 直接读 Saleae 的 .sr/.sal

```bash
# .sr 是 zip（metadata + logic-1/digital-N），可以解压后自己解析
mkdir sr_ext && cd sr_ext && unzip -o ../capture.sr
ls -la; cat metadata
xxd logic-1 | head          # 每通道一个文件，位打包
```

## 五、常见坑 / 变体

- **采样率不足**：低于信号频率 10 倍会丢边沿，必须看 `metadata` 里的 samplerate。
- **通道号混淆**：D0/D1 在题目里可能对应 TX/RX 反接，全试一遍。
- **UART 反相（RS-232 电平）**：加 invert 或取反解，`uart:baudrate=...:invert=1`。
- **SPI 的 CS 极性**：有些器件 CS 低有效，解码器要设 `cs_polarity=active-low`。
- **I2C 的重复起始**：解码器会自动处理，但地址 7 位时要注意显示是 0x3C 还是 0x78。
- **多组数据拼接**：一帧被切在多次事务里，要按 CS/起始条件分组后拼接。
- **波形文件被截断**：只记录了几毫秒，可能只有包头，需要题面别的附件补全。

## 六、参考来源

- [sigrok 项目主页（PulseView/sigrok-cli 与协议解码器）](https://sigrok.org/wiki/Main_Page)
- [Saleae 支持中心（Logic 2 与解码器文档）](https://support.saleae.com/)
- [Saleae Logic 2 下载](https://www.saleae.com/pages/downloads)
- [I2C 协议概览（i2c.info）](https://i2c.info/)
- [SparkFun 串口通信教程（UART 原理）](https://learn.sparkfun.com/tutorials/serial-communication/all)
- [pyserial 文档（对接真实串口设备）](https://pypi.org/project/pyserial/)

---
title: UART / JTAG / SWD 接口识别与调试
category: hardware
tags: [uart, jtag, swd, openocd, 接口识别, 调试器]
signals: [板子上有 4 针排针, 需要找调试接口, 串口没有输出, 需要连 jtag 读 flash, 题面给了设备图片, 需要 dump 固件]
difficulty: medium
source: "OpenOCD 官方文档 / Black Magic Probe 文档 / SparkFun 串口教程"
tools: [openocd, blackmagic, jlink, stlink, minicom, screen, pyserial, buspirone, jtagulator]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一张 PCB 照片，板上有 **4 针排针**（VCC/GND/TX/RX）或 **10/20 针排针**（JTAG）。
- 设备串口没有输出，需要自己找 TX 引脚（UART 隐蔽接口）。
- 需要从 MCU 里 dump 固件（`dump_image`）。
- 题面出现「SWD」「SWCLK」「SWDIO」等字样。

## 二、原理

**UART**：异步串行，最少 3 根线（TX、RX、GND）。空闲为**高电平**（mark），传输时先拉低一个比特周期（起始位），然后 8 个数据位（LSB first），最后是高电平停止位。所以识别要点：
- 上电瞬间用万用表/示波器看哪根脚**空闲高、有短促低脉冲** → 那是 TX。
- 用 **1kΩ 电阻 + 逻辑分析仪**：TX 线上试触，若出现 ASCII 就走了大运。

**JTAG**（IEEE 1149.1）：至少 `TCK/TMS/TDI/TDO/TRST` + `VREF/GND`。标准 20 针（ARM 20-pin）或 10 针（Cortex 10-pin）。引脚排列固定，可以按丝印对。

**SWD**（ARM CoreSight）：只需 `SWCLK`、`SWDIO` + `GND/VREF`，是 JTAG 的 2 线精简版，绝大多数 Cortex-M 芯片都支持。

**OpenOCD** 是通用调试服务：连上适配器（stlink/jlink/ftdi）后，可以通过 `gdb`/`telnet`/`tcl` 读写内存、dump flash、设置断点。

## 三、操作步骤

1. **物理观察**：丝印（`TX/RX/GND/3V3`、`TCK/TMS/TDI/TDO`）、排针数量、芯片型号。
2. **UART 定位 TX**：万用表测空闲电压（3.3V 高）；逻辑分析仪试触各脚。
3. **确定波特率**：逻辑分析仪量最小脉宽 → `1/w`；或用 sigrok 的 `uart` 解码器扫。
4. **JTAG/SWD 识别**：20 针按标准排；10 针 Cortex 看 `VTREF/GND/SWCLK/SWDIO`。
5. **OpenOCD 连上**：`openocd -f interface/stlink.cfg -f target/stm32f1x.cfg`。
6. **dump & 分析**：`dump_image flash.bin 0x08000000 0x10000`，然后 `binwalk`/`strings`。

## 四、命令/脚本

### UART 探测与连接

```bash
# 1) 列出串口设备
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null      # Linux
# Windows: Get-CimInstance Win32_SerialPort | Select Name,DeviceID
# 2) 连接（minicom / screen / picocom）
sudo apt install -y minicom picocom
minicom -D /dev/ttyUSB0 -b 115200
picocom -b 115200 /dev/ttyUSB0
screen /dev/ttyUSB0 115200
# 3) 试不同波特率
for b in 9600 19200 38400 57600 115200 230400; do
  echo "=== $b"
  timeout 3 picocom -b $b --imap lfcrlf /dev/ttyUSB0 2>&1 | head -5
done
```

```python
#!/usr/bin/env python3
# uart_sniff.py —— 串口监听 + 自动判断终端提示符
import serial, sys, time
port = sys.argv[1]
for baud in (115200, 9600, 38400, 921600, 57600, 230400):
    try:
        s = serial.Serial(port, baud, timeout=1)
        s.write(b'\r\n')
        data = s.read(512)
        if data:
            print(f'[{baud}] {data[:120]!r}')
            if b'sh' in data or b'login' in data or b'>' in data:
                print('  ^^^ 疑似命中')
        s.close()
    except Exception as e:
        print(baud, 'error', e)
```

### JTAG / SWD 引脚识别

```bash
# 常见的 ARM 20-pin JTAG 标准排列（俯视，pin1 是方形焊盘）
# 1 VTREF  2 VTREF    3 nTRST  4 GND
# 5 TDI    6 GND      7 TMS    8 GND
# 9 TCK   10 GND     11 RTCK  12 GND
# 13 TDO  14 GND     15 nRESET 16 GND
# 17 NC   18 GND     19 NC     20 GND

# Cortex 10-pin (SWD)
# 1 VTREF  2 SWDIO   3 GND    4 SWCLK
# 5 GND    6 SWO     7 KEY    8 NC
# 9 GND   10 nRESET

# 用万用表区分：VTREF 与目标 VCC 通，GND 与板地通，其余是信号
```

### OpenOCD 连接与 dump

```bash
sudo apt install -y openocd gdb-multiarch
# STM32 + ST-Link
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg
# 树莓派 / FTDI 适配器
openocd -f interface/ftdi/ft232h-module-swd.cfg -f target/stm32f4x.cfg
# 用 Black Magic Probe（直接给 GDB server）
arm-none-eabi-gdb -ex 'target extended-remote /dev/ttyACM0' \
  -ex 'monitor swdp_scan' -ex 'attach 1'
```

```bash
# 通过 telnet 直接给 OpenOCD 发命令（端口 4444）
(echo 'halt'; echo 'dump_image flash.bin 0x08000000 0x10000'; echo 'mdw 0x08000000 4'; echo 'reset'; echo 'exit') \
  | telnet localhost 4444
ls -la flash.bin && binwalk flash.bin
```

```tcl
# openocd 脚本：自动连上、dump、退出
init
halt
flash probe 0
dump_image firmware.bin 0x08000000 0x40000
reset
shutdown
```

```bash
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -f dump.tcl
```

### GDB 读内存（找到 flag 地址时）

```bash
arm-none-eabi-gdb -q \
  -ex 'target extended-remote localhost:3333' \
  -ex 'monitor reset halt' \
  -ex 'x/64x 0x20000000' \
  -ex 'dump binary memory sram.bin 0x20000000 0x20010000' \
  -ex 'detach' -ex 'quit'
strings sram.bin | grep -i flag
```

### 保护解锁（CTF 常见）

```bash
# STM32 读保护 RDP level 1：可用 st-flash 或 OpenOCD 解除（会全片擦除）
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg \
  -c 'init; reset halt; stm32f1x unlock 0; reset; shutdown'
# J-Link
JLinkExe -device STM32F103C8 -if SWD -speed 4000 -commandfile unlock.jlink
```

## 五、常见坑 / 变体

- **TX/RX 接反**：没有输出但波形正常时先互换。
- **电平不匹配**：1.8V 器件接 3.3V 适配器会烧，先测 VTREF。
- **UART 被关闭**：某些固件把串口复用为 GPIO，需要先改硬件配置或从 JTAG 读 flash 找字符串。
- **SWD 被禁用**：芯片选项字节里关闭了 SWD，需要先用 OpenOCD 的 mass erase 恢复。
- **JTAG 引脚被复用**：部分引脚兼做 GPIO，需要在启动早期挂上调试器。
- **dump 出来是加密的**：Secure Boot 芯片会返回全 `0xFF` 或乱码，需要侧信道/故障注入（见 `side-channel`）。
- **波特率小数分频**：某些 MCU 实际波特率是 115200±2%，用 `tolerance` 参数放宽。

## 六、参考来源

- [OpenOCD 官方文档（interface/target cfg 与命令）](https://openocd.org/doc/html/index.html)
- [Black Magic Probe 固件与原理](https://github.com/blackmagic-debug/blackmagic)
- [sigrok（逻辑分析仪侧解码 UART/JTAG）](https://sigrok.org/wiki/Main_Page)
- [SparkFun 串口通信教程](https://learn.sparkfun.com/tutorials/serial-communication/all)
- [pyserial 文档](https://pypi.org/project/pyserial/)
- [CTF Wiki - ICS 发现阶段（设备识别思路）](https://ctf-wiki.org/ics/discover/)

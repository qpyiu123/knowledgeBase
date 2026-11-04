---
title: 方法卡 · UART/JTAG 波形与引脚排查
category: hardware
tags: [uart, jtag, swd, logic-analyzer, baud, embedded]
signals:
  - 板子上有 4 个并排的过孔/排针，疑似 VCC GND TX RX
  - 逻辑分析仪抓到一条空闲为高的单线波形
  - 有 .sr 或 .sal 采集文件需要还原串口输出
  - 题目要求从 MCU 里 dump 固件或读出 flag 变量
  - 串口出现乱码，换几个波特率就有可读文本
difficulty: hard
source: kb/hardware/uart-jtag-swd.md, kb/hardware/logic-analyzer.md
tools: [python, logic2, saleae, openocd, minicom]
updated: 2026-11-03
---

## 适用场景

题目给一块板子、一个固件镜像或一段逻辑分析仪采集，需要从**电信号层**拿数据：
读出调试串口的启动日志/flag，或者通过 JTAG/SWD 连上芯片 dump 固件。

信号特征：空闲为高电平（mark），传输时先拉低一个比特周期（起始位），然后 8 个数据位（LSB first），
最后是高电平停止位——这就是 8N1。波形文件是 Logic 的 `.sr`（本质是 zip，内含 `metadata` 与 `logic-1`）。

## 前置条件

- 硬件侧：USB-TTL（CH340/CP2102）或逻辑分析仪；电平确认是 3.3V 再加，5V 先降压。
- 软件侧：`openocd` 配 SWD（`-f interface/stlink.cfg -f target/stm32f1x.cfg`）；串口用 `minicom -D /dev/ttyUSB0 -b 115200`。
- 采样率至少是被测信号最短电平宽度的 10 倍；常用波特率 9600/19200/38400/57600/115200/230400。

## 步骤

1. **先接地再找引脚**。万用表找 GND，再用"上电瞬间 TX 有方波、RX 恒定高"的特征区分 TX/RX；
   20-pin/10-pin JTAG 排针按标准 pinout 对号（VREF、TDI、TMS、TCK、TDO、nTRST、GND）。
2. **估波特率**。量一个比特的最短宽度 w（秒），波特率 ≈ 1/w；拿到大概值后按标准档位试。
3. **逻辑分析仪解码**。配置 8N1（8 数据位、无校验、1 停止位、LSB first），采样点取每位中点；
   手写解码时采样位置 `int(b0 + spb*(k+0.5))`。
4. **`.sr` 拆包**。`unzip -l dump.sr` 看到 `metadata` 与 `logic-1`，把 `logic-1` 当原始数字通道按通道切片即可。
5. **乱码三连**。乱码先怀疑波特率，再怀疑反相（RX/TX 接反），最后怀疑校验位/数据位设置不符。
6. **SWD dump 固件**。`openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -c "init; dump_image flash.bin 0x08000000 0x10000; exit"`。
7. **固件里找 flag**。`strings -a flash.bin`、`binwalk`、定位 `flag{` 与常见加密常量；必要时按 Cortex-M 找到变量地址再回读。
8. 记录：引脚定义、波特率、采样率、抓到的原始字节十六进制，便于他人复现。

## 立即可用脚本

`kb/_methods/scripts/hardware_uart.py`

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe kb\_methods\scripts\hardware_uart.py --hex "ff 00 0f 00 ..." --sample-rate 115200 --baud 9600
.venv\Scripts\python.exe kb\_methods\scripts\hardware_uart.py --file samples.txt --baud 115200
.venv\Scripts\python.exe kb\_methods\scripts\hardware_uart.py --selftest
```

- `--hex`：十六进制采样串（每个采样点一个字节），适合从截断的分析仪导出里拷一小段。
- `--file`：文本采样，每项十进制或 `0x` 十六进制。
- `--sample-rate` / `--baud`：算每比特采样数；`--baud` ≤0 直接拒绝。
- `--threshold`：自定义判决阈值，默认 `(min+max)/2`。
- 输出：采样点数、阈值、每比特采样数、帧错误数、解码字节（latin-1 打印）。
- 失败：无参数、采样串非法、动态范围过小、每比特采样数 <2 → 中文提示，退出码 2。
- `--selftest` 覆盖归一化+解码、波特率估算、参数拒绝、十六进制解析四组断言，通过时打印 `selftest ok` 并退出 0。

## 手工示例

```
$ python hardware_uart.py --hex "ff 00 0f 00 ff 00 0f 00 ..." --sample-rate 115200 --baud 9600
采样点 96，阈值 120，每比特 12.00 采样，帧错误 0
解码 3 字节：Hi!
```

说明：每比特 12 个采样，起始位低、LSB first、停止位高；`Hi!` 的帧是 `0 0001 0010 1` 等三组。
边界：`--hex abc` → `失败：十六进制采样串长度必须是偶数且非空`（退出码 2）。

## 失效场景

- **只做 8N1**：7 位数据、2 停止位、奇偶校验、9 位多机模式一律按 8N1 解，会得到乱码。
- **不做反相/上拉识别**：线序接反（RX 对 RX）或空闲电平为低时，脚本不会自动翻转，需要先把采样取反再喂。
- **不支持差分与高速**：RS-485 差分、USB、SPI/I2C 多线协议不在范围内，SPI 请按 CPOL/CPHA 模式另行解码。
- **阈值不自适应**：光照/电平抖动大的模拟采样用固定中点阈值可能误判，需要先滤波或用 `--threshold` 手工校准。
- **SWD/JTAG 无自动化**：openocd 命令与芯片型号强相关，脚本不替代调试器操作；锁读保护（RDP）的芯片需先解锁（会擦除）。

## 相关文档

- `kb/hardware/uart-jtag-swd.md`：8N1 电平时序、波特率档位、JTAG/SWD 引脚与 openocd 命令。
- `kb/hardware/logic-analyzer.md`：波特率估算、SPI 模式、`.sr` 文件结构、采样中点公式。
- `kb/forensics/file-carving.md`：从 dump 出的镜像里继续切固件/文件系统。

## 目录与收录说明

- 卡：`kb/_methods/hardware-uart.md`；脚本：`kb/_methods/scripts/hardware_uart.py`（纯标准库，无网络）。
- 覆盖 backlog 项 `hardware-uart`（category=hardware），证据来自 `kb/hardware/uart-jtag-swd.md` 与 `kb/hardware/logic-analyzer.md`。
- 与已有卡无重叠；SPI/I2C 类题目后续可另立方法卡。

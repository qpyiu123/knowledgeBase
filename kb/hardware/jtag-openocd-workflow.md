---
title: JTAG 实战（OpenOCD 配置、halt、dump 与断点）
category: hardware
tags: [jtag, openocd, swd, halt, dump-image, gdb-server]
signals: [目标板有 20 针 JTAG 排针或者 TMS TCK TDI TDO 丝印, 附件是一块 ARM 开发板或者 Cortex-M 芯片, 题目要求暂停 CPU 并读出 flash, 需要用 gdb 连上目标调试, 板子上的固件带读保护需要绕过, OpenOCD 报无法识别目标芯片]
difficulty: hard
source: "OpenOCD 官方用户手册 / ARM Debug Interface 架构文档 / 各大芯片厂商 OpenOCD 配置"
tools: [openocd, gdb-multiarch, urJTAG, jtagulator, telnet, arm-none-eabi-gdb]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 板上有 2×10 排针（JTAG 20pin）或 4~6 个测试点标注 `TMS/TCK/TDI/TDO/nRST/VREF`。
- 主控是 Cortex-M0/M3/M4（STM32、nRF、LPC）或 MIPS/ARM9 老设备。
- 题目说"用调试器 halt 后 dump 出 flash 内容"。
- 需要"在某个函数下断点"或"修改寄存器跳过校验"。
- OpenOCD 启动时打印 `Warn : Cannot identify target` 或 `Error: JTAG scan chain interrogation failed`。
- 附件给了 `.cfg` 文件或者芯片型号（如 `stm32f103c8`）。

## 二、原理

**JTAG 是 TAP 状态机驱动的串行调试接口，核心 4 线：**
- `TCK` 时钟、`TMS` 状态控制、`TDI` 数据输入、`TDO` 数据输出。
- TAP 状态机在 TCK 上升沿按 TMS 跳转，`Shift-DR` 状态下把数据串出/串入。

**OpenOCD 的角色**：把"传输层"（FTDI/J-Link/CH341 等 adapter）与"目标层"（TAP 扫描链、CPU 调试单元）桥接起来，再对外暴露：
- **Telnet 4444**：交互命令（`halt`、`reset`、`mdw`、`dump_image`）。
- **GDB 3333**：给 `gdb-multiarch` 连接。
- **TCL RPC 6666**：脚本化。

**两种传输**：
- **JTAG**：多设备可串成扫描链，需要 `ir_length` 匹配 IR 寄存器长度。
- **SWD**：2 线（SWDIO/SWCLK），ARM 独有，更省引脚，绝大多数 Cortex-M 芯片两者都支持。

**读出 flash 的三条路**：
1. **CPU 侧读**（`mdw`/`dump_image`）：芯片运行后通过总线读 flash 地址，最简单但受 MMU/保护限制。
2. **内置 flash 控制器**：用芯片厂商的算法（OpenOCD 的 `flash bank` 自动加载）读，需 `flash probe`。
3. **调试单元直读**：Cortex-M 的 AHB-AP 直接访问，绕过 CPU。

## 三、操作步骤

1. **确认接口**：先试 SWD（更少引脚），失败再试 JTAG；用 `JTAGulator` 或逐引脚试探。
2. **选对配置文件**：`interface/ftdi/*.cfg` 或 `interface/jlink.cfg` + `target/stm32f1x.cfg`。
3. **连上并验证**：`openocd -f ...` 输出应含 `Info : [stm32f1x.cpu] Cortex-M3 r1p1 processor detected`。
4. **halt CPU**：Telnet 里 `halt`，然后 `reg pc` 看是否停住。
5. **探测 flash**：`flash probe 0`，`flash info 0` 看 bank 大小与保护状态。
6. **dump**：`dump_image out.bin 0x08000000 0x10000`。
7. **GDB 调试**：`gdb-multiarch bin -ex 'target remote :3333'`，下断、改寄存器。

## 四、命令 / 脚本

```bash
# 启动 OpenOCD（示例：FT232H + STM32F103）
openocd -f interface/ftdi/ft232h-module-swd.cfg \
        -f target/stm32f1x.cfg \
        -c "adapter speed 1000"

# 另一个终端用 telnet 交互
telnet localhost 4444

# 在 telnet 里执行
# > halt
# > reg pc
# > mdw 0x08000000 8
# > flash probe 0
# > flash info 0
# > dump_image fw.bin 0x08000000 0x20000
# > resume
```

```bash
# 一条命令完成 dump（不开 telnet）
openocd -f interface/ftdi/ft232h-module-swd.cfg -f target/stm32f1x.cfg \
  -c "init; halt; dump_image fw.bin 0x08000000 0x20000; shutdown"
```

```bash
# GDB 调试
gdb-multiarch firmware.elf
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) x/8i $pc
(gdb) break verify_flag
(gdb) continue
(gdb) info registers
(gdb) set $r0 = 1          # 跳过校验
```

```tcl
# 自定义配置文件：接一个不认识的目标（以 SWD 为例）
adapter driver ftdi
ftdi_device_desc "Dual RS232-HS"
ftdi_vid_pid 0x0403 0x6010
ftdi_layout_init 0x0008 0x001b
adapter speed 1000
transport select swd
source [find target/swj-dp.tcl]
set _CHIPNAME ctf
swd newdap $_CHIPNAME cpu -expected-id 0x2ba01477
dap create $_CHIPNAME.dap -chain-position $_CHIPNAME.cpu
set _TARGETNAME $_CHIPNAME.cpu
target create $_TARGETNAME cortex_m -dap $_CHIPNAME.dap
$_TARGETNAME configure -event examine-start { sleep 10 }
```

```python
#!/usr/bin/env python3
# 解析 OpenOCD 的扫描链输出，推断 IR 长度
import re, sys
log = open(sys.argv[1]).read()
for m in re.finditer(r'IR capture(?:.*?)0x([0-9a-fA-F]+)', log):
    v = int(m.group(1), 16)
    print('IR capture 0x%x 已置位位数=%d' % (v, bin(v).count('1')))
for m in re.finditer(r'expected-id 0x([0-9a-fA-F]+)', log):
    print('可能的 IDCODE 0x%s' % m.group(1))
```

## 五、常见坑 / 变体

- **`ir_length` 不对**：JTAG 扫描链里 IR 长度因芯片而异，OpenOCD 默认 4，多设备链要手工设。
- **SWD 引脚被复用为 GPIO**：部分芯片需要先"上电复位时序"（`reset_config srst_only` 或加 `-c "reset_config none"`）。
- **读保护（RDP）**：STM32 读保护 Level 1 会让调试口拒绝访问，需要 `unlock`（Level 2 则不可逆）。
- **`dump_image` 长度不够**：flash 实际大于 0x20000 时要按 `flash info` 的 `size` 给全。
- **电压电平**：JTAG 的 VREF 必须与目标电压一致（1.8V/3.3V），FTDI 的 VTREF 接错会读不到 IDCODE。
- **`Cannot identify target`**：绝大多数是接线或 `adapter speed` 太快，降到 100kHz 再试。
- **变体**：MIPS 的 EJTAG（需 `target/mips_m4k.cfg`）、RISC-V 的 `riscv` target、ESP32 的 `esp32` target。

## 六、参考来源

- [OpenOCD 用户手册：General Commands（adapter speed、halt、dump_image）](https://openocd.org/doc/html/General-Commands.html)
- [OpenOCD 官方文档总入口（配置文件与 target 脚本）](https://openocd.org/doc/html/index.html)
- [HardBreak：OpenOCD 用 dump_image 提取固件实战](https://www.hardbreak.wiki/hardware-hacking/basics/tools/software-tools/openocd)
- [ARM Debug Interface v5 架构规范（SWD 与 AP 访问）](https://github.com/Arm-software)
- [gdb-multiarch 手册（monitor 命令透传）](https://www.gnu.org/software/gdb/documentation/)

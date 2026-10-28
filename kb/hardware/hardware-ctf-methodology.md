---
title: 硬件 CTF 综合题解思路（从板子到 flag 的全链路）
category: hardware
tags: [hardware-ctf, methodology, uart, spi, jtag, rootfs]
signals: [题目给了一块板子的照片或者实物, 附件是一个固件或者一串串口日志, 题目没有任何提示只有一句请拿到 flag, 需要从板上找出测试点然后接到串口, 板子上有明显的调试接口但没有标注, 题目既给 pcap 又给固件]
difficulty: hard
source: "CTF-Wiki 硬件安全章节 / 历年硬件 CTF 题（RHme、TFC）题解"
tools: [multimeter, logic-analyzer, picocom, flashrom, openocd, binwalk, ghidra]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目附件是"一块板子的照片 + 固件二进制"，没有任何文字提示。
- 板上有未标注的测试点、排针、跳线帽。
- 题目同时给了固件与一段 pcap，要求"找出设备发送了什么"。
- 提示只有一句"设备会周期性广播数据，找出其中的密钥"。
- 板上芯片型号被磨掉，需要靠封装与引脚推断。
- 题目要求"按指定顺序操作"或"提交一段交互记录"。

## 二、原理

**硬件题的本质是"在物理层面观察/改变设备行为"**，解题路径是一棵决策树：

```
拿到板子
 ├─ 有 UART?      -> 读日志/进 shell   -> 找文件系统/环境变量
 ├─ 有 SPI Flash? -> 读固件            -> binwalk/逆向
 ├─ 有 JTAG/SWD?  -> halt/dump 内存    -> 断点改校验
 ├─ 有无线?       -> SDR 抓包解调      -> 还原协议
 └─ 都没有        -> glitch / 侧信道 / 芯片漏洞
```

**第一步永远是"找接口"**：4 针 UART、6/10/20 针 JTAG、8 脚 SPI Flash、USB、网口、天线座。

**硬件 CTF 的三类核心技巧**：
1. **被动观察**（串口日志、SPI 总线、RF 抓包）——不破坏设备。
2. **主动读写**（flash 提取、U-Boot 命令行、JTAG dump）——需要接线。
3. **物理攻击**（毛刺、侧信道、去封装）——针对安全芯片。

## 三、操作步骤

1. **信息收集**：看丝印（型号、版本）、拍照记录芯片布局、查数据手册。
2. **找测试点**：万用表测 GND（对地导通）、VCC（3.3V 稳定）；其余引脚上电时用逻辑分析仪抓，能看到明显 115200 位宽方波的就是 UART TX。
3. **UART 接管**：接上读启动日志，抓 `Hit any key to stop autoboot`，进 U-Boot 改 `bootargs`。
4. **固件提取**：`flashrom` 读 SPI Flash，或 `binwalk -eM` 拆固件镜像。
5. **逆向分析**：Ghidra 打开 ELF，找 `flag`、`check`、`verify` 与协议处理函数。
6. **动态验证**：JTAG 下断点，或改固件重烧。
7. **交叉验证**：pcap 与串口日志的时间线对齐，确认"设备实际发了什么"。

## 四、命令 / 脚本

```bash
# 1) 接口识别（逻辑分析仪抓 UART）
sigrok-cli -d fx2lafw --config samplerate=2m --samples 20000000 \
  -C D0,D1,D2,D3 -o capture.sr
sigrok-cli -i capture.sr -P uart:baudrate=115200:rx=D1 | head -20

# 2) 串口
picocom -b 115200 /dev/ttyUSB0
# 3) 固件提取
flashrom -p ch341a_spi -r fw.bin
binwalk -eM fw.bin
# 4) 逆向
ghidraRun &
# 5) JTAG dump
openocd -f interface/ftdi/ft232h-module-swd.cfg -f target/stm32f1x.cfg \
  -c "init; halt; dump_image fw2.bin 0x08000000 0x20000; shutdown"
```

```python
#!/usr/bin/env python3
# 从逻辑分析仪导出的 CSV 自动嗅探 UART 波特率
import csv, sys, statistics

def edges_from_csv(path, chan='d0'):
    prev, out = 0, []
    for r in csv.DictReader(open(path)):
        v = int(r[chan])
        if v != prev:
            out.append((int(r.get('time', 0)), v))
            prev = v
    return out

def guess_baud(edges, clock):
    """取最短的高/低电平段作为 1 bit 的近似"""
    lens = [edges[i+1][0] - edges[i][0] for i in range(len(edges)-1)]
    if not lens:
        return None
    short = sorted(lens)[:max(len(lens)//4, 1)]
    bit_t = statistics.median(short)
    return bit_t, (clock / bit_t if bit_t else None)

if __name__ == '__main__':
    e = edges_from_csv(sys.argv[1])
    print('边沿数', len(e), '估计 bit 时长/波特率:', guess_baud(e, 2_000_000))
```

```python
#!/usr/bin/env python3
# 硬件题常见"flag 藏在固件字符串里"的快速定位
import re, sys, os

PATS = [rb'flag\{', rb'ctf\{', rb'CTF\{', rb'key\s*=', rb'secret']

def scan(root):
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            try:
                d = open(p, 'rb').read()
            except Exception:
                continue
            for pat in PATS:
                for m in re.finditer(pat, d):
                    s = d[max(0, m.start()-32):m.start()+96]
                    print('%-50s %r' % (p[:50], s))

if __name__ == '__main__':
    scan(sys.argv[1])
```

## 五、常见坑 / 变体

- **别急着拆焊**：先找 UART，多数题给了串口就不需要拆 flash。
- **1.8V vs 3.3V**：接错电源会烧芯片，先量 VCC。
- **固件有加密**：`binwalk` 拆不出时看是否整块加密（熵接近 8），密钥常在 BootROM 或 OTP 里。
- **多阶段镜像**：U-Boot 里还有 `uImage`、`dtb`、`rootfs`，注意偏移。
- **时间同步**：串口日志没有时间戳，要把事件与 pcap 的帧号对齐才能确定因果。
- **答案形式**：有些题的 flag 是"设备某次广播的十六进制"，需要精确抓包而不是解出文件。
- **变体**：RHme 系列（RISC-V 侧信道）、TFC CTF 硬件题；比赛常把"逆向 + 硬件"混合出题。

## 六、参考来源

- [CTF-Wiki：硬件安全（UART/JTAG/固件）章节](https://ctf-wiki.org/)
- [sigrok 官方文档（sigrok-cli 与 UART 解码器）](https://sigrok.org/wiki/Sigrok-cli)
- [binwalk 官方仓库](https://github.com/ReFirmLabs/binwalk)
- [HardBreak：硬件 hacking 工具与流程](https://www.hardbreak.wiki/hardware-hacking/basics/tools/software-tools/openocd)
- [RHme 系列 CTF 题解（硬件侧信道与故障注入）](https://github.com/Riscure)

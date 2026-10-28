---
title: SPI Flash / EEPROM 读写与固件提取（CH341A + flashrom）
category: hardware
tags: [spi-flash, eeprom, ch341a, flashrom, dump, firmware]
signals: [板子上有一颗 8 脚的小芯片型号是 W25Q 或者 MX25L, 题目说固件在 flash 里需要读出来, 附件是 .bin 但是开头是 ff ff ff 或者一大片 00, 要求提取路由器或摄像头的固件镜像, 板子上有 SOIC8 封装且旁边标着 U1, 题目给了 SPIFlash 的读波形或者接线图]
difficulty: medium
source: "flashrom 官方文档 / CH341A 使用指南 / Winbond W25Q 数据手册"
tools: [ch341a, flashrom, asprogrammer, binwalk, dd, minipro]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 板上有 8 脚 SOIC/SOP8 芯片，丝印 `W25Q64`、`W25Q128`、`MX25L3206`、`GD25Q`、`AT25`。
- 题目描述"读取板载固件""dump flash 后分析"。
- 附件是 `firmware.bin`，大小是 2 的幂（1MB/4MB/8MB/16MB），且开头是 `ff ff ff` 或大段 `00`——典型的裸 flash 镜像。
- 板子有 2×4 排针标注 `VCC GND CS CLK MOSI MISO`。
- 题目要求"找出被删除/损坏的配置"或"从 flash 里恢复文件系统"。
- 给了一张 CH341A 夹子夹住芯片的照片。

## 二、原理

**SPI Flash 的物理接口是 4 线（+ 电源）：**

| 引脚 | 作用 |
| --- | --- |
| `/CS` | 片选，低有效 |
| `CLK` | 时钟 |
| `MOSI` (DI) | 主→从 数据 |
| `MISO` (DO) | 从→主 数据 |
| `VCC` / `GND` | 供电（3.3V 常见，**1.8V 芯片直接上 3.3V 会烧**） |

**关键指令（标准 SPI，0x03 类）**：
- `0x9F` Read JEDEC ID → 3 字节（制造商 + 型号 + 容量码）。
- `0x03` Read（慢速，无地址限制）。
- `0x0B` Fast Read（需 dummy byte）。
- `0x05` Read Status Register。
- `0x06` Write Enable；`0x20/0xD8` Sector/Block Erase；`0x02` Page Program（256B 页）。

**镜像结构**：很多设备的 flash 头几百 KB 是空（`0xFF`），真正的 U-Boot 在某个偏移或分区表指定位置，所以 `binwalk` 之前要先看"是否有一个非 0xFF 区从某偏移开始"。

**外接读的三种方式**：
1. **夹子在线读（SOIC-8 clip）**：免拆焊，但板上其他器件会干扰 SPI 总线，读出的数据可能不稳定。
2. **拆下芯片读**：最可靠，需热风枪。
3. **板载 ISP 接口**：用排针接，最安全。

## 三、操作步骤

1. **识别芯片**：用放大镜看丝印，或用 `flashrom -p ch341a_spi` 自动探测（会打印 `Found Winbond flash chip ...`）。
2. **确认电压**：查数据手册（`W25Q64JV` 是 3.3V，`W25Q64FW` 是 1.8V），1.8V 必须加电平转换。
3. **接线**：夹子/排针按 `CS-CLK-MOSI-MISO-VCC-GND` 对齐，注意芯片 1 脚标记。
4. **读 ID 验证**：`flashrom -p ch341a_spi` 能列出芯片即为通路。
5. **读两次比对**：`flashrom -r a.bin` 与 `-r b.bin`，`cmp` 一致才可信。
6. **分析**：`binwalk`、`strings`、`file`，再按分区表切。
7. **改后回写**：`flashrom -w new.bin -v`（先 `-E` 擦除，写入后 `-v` 校验）。

## 四、命令 / 脚本

```bash
# 探测与读取（Linux，CH341A USB 编程器）
sudo flashrom -p ch341a_spi
sudo flashrom -p ch341a_spi -r firmware_1.bin
sudo flashrom -p ch341a_spi -r firmware_2.bin
cmp firmware_1.bin firmware_2.bin && echo "两次读取一致"
# 芯片信息（capacity 与 JEDEC ID）
sudo flashrom -p ch341a_spi --flash-name
# 写入与校验
sudo flashrom -p ch341a_spi -w patched.bin -v
# 部分擦写（只改某个区域）
sudo flashrom -p ch341a_spi -w patch.bin --layout layout.txt --noverify -i region
```

```bash
# 分区表驱动的布局文件（layout.txt）
00000000:0001ffff uboot
00020000:002fffff kernel
00300000:00ffffff rootfs
```

```bash
# 分析
binwalk firmware.bin
strings -n 8 firmware.bin | grep -iE 'busybox|u-boot|rootfs|http' | head
# 找非 0xFF 起点（真实数据从这里开始）
python3 - <<'EOF'
d = open('firmware.bin','rb').read()
i = 0
while i < len(d) and d[i] == 0xFF: i += 1
print('首个非FF偏移: 0x%x (%d), 总长 0x%x' % (i, i, len(d)))
EOF
```

```python
#!/usr/bin/env python3
# 从波形/CSV 里手工解码 SPI（逻辑分析仪导出的 cs/clk/mosi 列）
import csv, sys

def decode(path):
    rows = list(csv.DictReader(open(path)))
    bits = []
    prev_clk = 0; cs_active = False
    for r in rows:
        cs = int(r['cs']); clk = int(r['clk']); mosi = int(r['mosi'])
        if not cs:
            cs_active = True
        elif cs_active:
            cs_active = False
            if bits:
                yield bits; bits = []
            prev_clk = 0
            continue
        if cs_active and prev_clk == 0 and clk == 1:   # 上升沿采样
            bits.append(mosi)
        prev_clk = clk

def to_bytes(bits):
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        v = 0
        for b in bits[i:i+8]:
            v = (v << 1) | b
        out.append(v)
    return bytes(out)

if __name__ == '__main__':
    for chunk in decode(sys.argv[1]):
        print(to_bytes(chunk).hex(' '))
```

## 五、常见坑 / 变体

- **夹子在线读不稳定**：板上其它 SPI 器件的三态冲突会导致偶发数据错误，务必读两次比对；不行就拆焊。
- **1.8V 芯片**：`W25Q64FW`/`MX25U` 系列是 1.8V，用 3.3V 编程器会烧坏，需要 CH341A 的 1.8V 转接板。
- **容量对不上**：`flashrom` 探测到芯片但读出的长度是 0 或全 FF，多为接线松动或 CS 未接地。
- **大容量（>16MB）3 字节地址**：部分老编程器不支持 4 字节地址指令（`0x13`），只能读到前 16MB。
- **写保护**：状态寄存器（`0x05` 的 BP0-2 位）会阻止写入，需先 `0x01` 清保护。
- **写入前必须擦除**：NOR flash 只能 1→0，写入前必须擦成 `0xFF`。
- **变体**：EEPROM 的 I2C 接口（`24Cxx` 系列，用 `i2cdetect`/`eeprog`）、NAND flash（需 `nanddump`，有 OOB 与坏块管理）。

## 六、参考来源

- [flashrom 官方文档（ch341a_spi 编程器支持）](https://www.flashrom.org/)
- [CH341A SPI 编程器使用指南（接线与常见问题）](https://winraid.level1techs.com/t/guide-how-to-use-a-ch341a-spi-programmer-flasher/33041)
- [tinysystems 文档：用 CH341A 解砖与刷写（含 1.8V 注意事项）](https://docs.mrchromebox.tech/docs/support/unbricking/unbrick-ch341a.html)
- [binwalk 官方仓库（固件签名提取）](https://github.com/ReFirmLabs/binwalk)
- [Winbond W25Q128 数据手册（指令集与状态寄存器）](https://www.winbond.com/)

---
title: 嵌入式 Linux（串口登录、U-Boot 中断、rootfs 提取）
category: hardware
tags: [embedded-linux, u-boot, uart, rootfs, squashfs, busybox]
signals: [板子上有 4 针 UART 排针标注 TX RX GND VCC, 115200 8N1 串口能刷出启动日志, 启动时提示按任意键进入 U-Boot 控制台, 题目要求拿到 rootfs 里的 flag, 固件是 squashfs 或者 jffs2, 串口登录需要密码但可以用单用户模式绕过]
difficulty: medium
source: "U-Boot 官方文档 / Toradex 串口控制台配置文档 / binwalk 固件提取实战"
tools: [picocom, minicom, putty, binwalk, unsquashfs, jefferson, ubi_reader, dd]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 板上有 4 针（`VCC TX RX GND`）或 3 针排针，丝印不明确。
- 上电后串口能刷出 `U-Boot 2016.05`、`Booting kernel from Legacy Image`。
- 日志出现 `Hit any key to stop autoboot: 3`。
- 登录提示 `buildroot login:` 或 `Password:`。
- 附件是 `firmware.bin`，`binwalk` 能扫出 `Squashfs filesystem`、`JFFS2`、`UBI erase count header`。
- 题目要求"找到 rootfs 里的 flag"或"拿到 root shell"。

## 二、原理

**嵌入式 Linux 启动链**：
```
ROM -> U-Boot -> (load kernel + dtb + rootfs 到内存) -> bootargs -> kernel -> init -> getty(串口登录)
```

**三个切入点：**

1. **U-Boot 命令行**：正常启动时有 `Hit any key to stop autoboot`，按任意键进 `=>` 提示符。可：
   - `printenv` 看 `bootargs`、`bootcmd`；
   - `setenv bootargs ... init=/bin/sh` 改启动参数进单用户；
   - `mmc read`/`sf read` 把 flash 内容读出来。
2. **内核 cmdline**：`rdinit=/bin/sh` 或 `init=/bin/sh` 直接跳过 init（免登录）。
3. **rootfs 离线提取**：从固件镜像里把文件系统解出来，flag 常直接在 `/flag`、`/etc/flag`。

**常见 rootfs 格式**：`squashfs`（只读压缩，嵌入式最常见）、`jffs2`（NOR flash）、`ubifs`（NAND，需 UBI 层）、`ext4`（eMMC）。

## 三、操作步骤

1. **找 UART**：万用表找 GND（对地导通的引脚），上电时用逻辑分析仪/示波器抓 TX（有数据的那根）。
2. **确认波特率**：115200 最常见，其次 57600/38400/9600；抓上升沿估算位宽。
3. **接串口读日志**：`picocom -b 115200 /dev/ttyUSB0`，记录启动日志里的 flash 布局与 bootargs。
4. **抓中断窗口**：上电瞬间按住回车，出现 `=>` 即成功。
5. **拿 shell**：`printenv`，改 `bootargs` 加 `init=/bin/sh` 后 `boot`。
6. **离线提取**：`binwalk -eM firmware.bin`，再按格式 `unsquashfs`/`jefferson`/`ubireader_extract_images`。
7. **找 flag**：`grep -r 'flag' rootfs/`。

## 四、命令 / 脚本

```bash
# 串口连接
picocom -b 115200 /dev/ttyUSB0
minicom -D /dev/ttyUSB0 -b 115200
# Windows: putty -> Serial -> 115200 8N1

# 波特率自动猜测（读串口字节看是否像 ASCII）
python3 - <<'EOF'
import serial, time
for baud in (9600, 19200, 38400, 57600, 115200, 230400, 1500000):
    try:
        s = serial.Serial('/dev/ttyUSB0', baud, timeout=1)
        s.reset_input_buffer(); time.sleep(0.3)
        d = s.read(64)
        s.close()
        txt = ''.join(chr(c) if 32 <= c < 127 else '.' for c in d)
        print(baud, txt)
    except Exception as e:
        print(baud, 'ERR', e)
EOF

# U-Boot 命令行（手工）
# => printenv
# => setenv bootargs "console=ttyS0,115200 root=/dev/mtdblock2 init=/bin/sh"
# => boot
# => md.b 0x80000000 0x100        # 看内存
# => sf probe 0; sf read 0x80000000 0 0x1000000   # 读 SPI flash
```

```bash
# 固件提取
binwalk -eM firmware.bin
# squashfs
unsquashfs -d rootfs img.squashfs
unsquashfs -l img.squashfs | head -30
# ubifs（需先解 UBI）
ubireader_extract_images firmware.ubi
ubireader_extract_files -o out rootfs.ubifs
# jffs2
jefferson -d out img.jffs2
# 从 flash 镜像按偏移切
dd if=firmware.bin of=rootfs.sqsh bs=1 skip=$((0x180000)) count=$((0x400000))

# 找 flag
grep -rl 'flag{' rootfs/ 2>/dev/null
strings -n 6 rootfs/bin/busybox | grep -i flag | head
```

```python
#!/usr/bin/env python3
# 自动识别固件里所有文件系统的起始偏移
import re

SIGS = {
    'squashfs': b'hsqs',
    'jffs2':    b'\x85\x19',
    'ubifs':    b'\x31\x18\x10\x06',
    'ext4':     b'\x53\xef',           # 超级块偏移 0x438 处
    'cpio':     b'070701',
}

def scan(path):
    d = open(path, 'rb').read()
    for name, sig in SIGS.items():
        start = 0
        while True:
            i = d.find(sig, start)
            if i < 0:
                break
            print('%-9s @ 0x%08x' % (name, i))
            start = i + 1

if __name__ == '__main__':
    scan(sys.argv[1])
```

## 五、常见坑 / 变体

- **TX/RX 接反**：串口只能收不能发（或只能发不能收）时先交叉 TX/RX。
- **VCC 不要接**：板子自身供电，接 5V 到 3.3V 引脚会烧；只接 GND/TX/RX。
- **U-Boot 被禁用**：`CONFIG_AUTOBOOT_KEYED` 后需要特定按键序列（组合键），或 `bootdelay=0` 完全不给机会。
- **`init=/bin/sh` 被忽略**：内核用 `rdinit` 从 initramfs 启动时要用 `rdinit=/bin/sh`。
- **squashfs 版本/压缩算法**：`unsquashfs` 需支持 `xz`/`lz4` 编译选项，报错时换新版。
- **UBI 的双层结构**：`.ubi` 里是 UBI 卷，卷里才是 ubifs，直接 `unsquashfs` 会失败。
- **变体**：NAND 坏块（`ubidetach`）、安全启动下的只读 rootfs（`dm-verity`）、只读 `/` 需要 `mount -o remount,rw /`。

## 六、参考来源

- [U-Boot 官方文档（bootargs 与命令行）](https://docs.u-boot.org/en/latest/)
- [Toradex：配置串口调试控制台（Linux/U-Boot）](https://developer.toradex.com/software/development-resources/configuring-serial-port-debug-console-linuxu-boot/)
- [binwalk 官方仓库（固件签名与提取）](https://github.com/ReFirmLabs/binwalk)
- [squashfs-tools 官方文档（unsquashfs 参数）](https://github.com/plougher/squashfs-tools)
- [ubi_reader：UBI/UBIFS 提取工具](https://github.com/jrspruitt/ubi_reader)

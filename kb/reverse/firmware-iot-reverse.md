---
title: 固件 / IoT 逆向（固件镜像解包与嵌入式二进制分析）
category: reverse
tags: [firmware, iot, binwalk, squashfs, 嵌入式]
signals: [附件是 .bin / .img / .hex 固件包且体积 4MB~64MB, binwalk 能看出 SquashFS 或 CramFS 文件系统, 镜像里有 UBI / UBI# 标记, 字符串里有 BusyBox 与 OpenWrt 字样, 目标设备是路由器 / 摄像头 / 智能家居, 有 CFE / U-Boot 引导信息, 固件头部出现 HDR0 或 HSQS 魔数, 有 mtd 分区表或在 /proc/mtd, 题面提示「固件」「IoT」「固件升级」]
difficulty: hard
source: "OWASP IoT / binwalk / unblob"
tools: [binwalk, unblob, python, ghidra]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `firmware.bin`、`update.img`、`.trx`，大小 4–64MB。
- `binwalk firmware.bin` 输出 `Squashfs filesystem`、`CramFS`、`JFFS2`、`UBI erase count header`。
- 镜像头部 `HSQS`（SquashFS 小端）、`sqsh`（大端）、`HDR0`（TRX）。
- 字符串里有 `BusyBox v1.xx`、`OpenWrt`、`/etc/init.d/rcS`、`mtdblock`。
- 目标架构常见：**MIPS（大端/小端）**、**ARM/MIPSEL**、少量 x86。
- 题面提示：`固件`、`IoT`、`路由器`、`摄像头`、`升级包`、`binwalk`。
- 只有固件没有符号表；需要自己找 `httpd`、`cgi-bin`、`telnetd`。

## 二、原理

### 1. 固件通常由什么组成

```
[Bootloader/CFE] [Header] [Kernel (uImage)] [RootFS (SquashFS/JFFS2/UBI)] [Padding]
```

- **SquashFS**：只读压缩文件系统，魔数 `hsqs`（小端）/ `sqsh`（大端）。
- **CramFS**：老式只读，魔数 `0x28cd3d45`。
- **UBI/UBIFS**：NAND 擦除块 + LEB 映射，需 `ubireader` 提取。
- **JFFS2**：魔数 `0x1985`。
- **TRX**：Broadcom 格式，`HDR0` + 长度 + CRC + 分区偏移。

### 2. 逆向思路（与"拿 flag"相关）

1. **解出 rootfs** → 找 Web 服务（`/usr/sbin/httpd`、`/www/cgi-bin/`）。
2. **分析二进制**：MIPS/ARM 需要 `ghidra` 或 `IDA` 的对应处理器模块。
3. **找硬编码凭据 / 加密密钥**：`/etc/shadow`、`/etc/config/*`、`nvram` 默认值。
4. **Web 端漏洞**：CGI 参数未过滤 → 命令注入（固件类题常见）。
5. **启动脚本**：`/etc/init.d/rcS` 能看到开了什么服务。
6. **加固件时**：需要 CRC（TRX 有 CRC32）或签名（RSA），要重算。

### 3. 硬件接口（CTF 少用，但偶尔给 dump）

- UART：找 `GND/TX/RX` 三个焊盘，115200 8N1。
- SPI Flash：用 `flashrom` 读。
- JTAG：几乎不给。

## 三、解题步骤

1. **识别格式**：`binwalk --signature firmware.bin`，或 `file`。
2. **提取**：`binwalk -eM firmware.bin`，或用 `unblob`（识别更准，含 UBI）。
3. **进 rootfs**：`unsquashfs -d out squashfs-root`，检查 `/www`、`/bin`、`/etc`。
4. **找 Web 服务**：`grep -r "httpd\|cgi\|lighttpd" etc/init.d/`。
5. **分析关键二进制**：`file bin/httpd` 确认架构 → `ghidra` 加载对应 processor。
6. **找 flag 线索**：`grep -r "flag" .`、看 `etc/shadow`、`etc/passwd`。
7. **重打包（如需）**：重新 `mksquashfs` 并修正 TRX 头 CRC。

## 四、可直接运行的脚本

格式识别与提取：

```bash
# 1) 识别
binwalk --signature --term firmware.bin

# 2) 提取（递归 + 单层）
binwalk -eM --run-as=root firmware.bin

# 3) unblob（更准，支持 UBI/多段）
pip install unblob
unblob -e extracted firmware.bin
```

手动解 SquashFS：

```bash
# 找到偏移后（binwalk 输出里的 decimal 偏移）
dd if=firmware.bin of=fs.sqsh bs=1 skip=$OFFSET
unsquashfs -d rootfs fs.sqsh
```

TRX 头解析（Broadcom 固件）：

```python
import struct, zlib, sys

data = open(sys.argv[1], "rb").read()
if data[:4] != b"HDR0":
    print("not a TRX image"); sys.exit()
length, crc, flags, ver = struct.unpack("<IIHH", data[4:16])
print("len=%d crc=0x%08X flags=0x%04X ver=0x%04X" % (length, crc, flags, ver))

body = data[16:16 + length - 12]
calc = zlib.crc32(body) & 0xFFFFFFFF
print("crc match:", calc == crc)

# 分区偏移（常见 v1/v2）
if ver >= 1:
    n = 3 if ver >= 2 else 1
    offs = struct.unpack("<%dI" % n, data[16:16 + 4 * n])
    print("offsets:", [hex(o) for o in offs])
```

识别与修复打包后的长度（重打包时常见坑）：

```python
def fix_trx(src, dst):
    data = bytearray(open(src, "rb").read())
    assert data[:4] == b"HDR0"
    total = len(data)
    data[4:8] = struct.pack("<I", total)
    data[8:12] = struct.pack("<I", zlib.crc32(bytes(data[16:])) & 0xFFFFFFFF)
    open(dst, "wb").write(data)
    print("repacked", dst, total)
```

固件里快速找可疑二进制（MIPS/ARM 架构确认）：

```python
import os, struct

def arch(b):
    if b[:4] == b"\x7fELF":
        cls = b[4]; data = b[5]; mach = struct.unpack("<H", b[18:20])[0]
        m = {3: "x86", 8: "MIPS", 40: "ARM", 62: "x86-64", 183: "AArch64", 20: "PPC"}
        endian = "LE" if data == 1 else "BE"
        return "ELF%d %s %s" % (32 if cls == 1 else 64, m.get(mach, mach), endian)
    return None

for root, _, files in os.walk("rootfs"):
    for f in files:
        p = os.path.join(root, f)
        try:
            b = open(p, "rb").read(20)
        except Exception:
            continue
        a = arch(b)
        if a:
            print("%-40s %s" % (p, a))
```

在固件里找 Web 服务与凭据：

```bash
grep -rIl "cgi-bin\|lighttpd\|httpd" rootfs/etc/ 2>/dev/null
grep -rI "password\|passwd" rootfs/etc/config/ 2>/dev/null
cat rootfs/etc/shadow
```

SquashFS 重打包：

```bash
mksquashfs rootfs new.squashfs -comp xz -b 131072 -noappend
```

## 五、常见坑 / 变体

- **SquashFS 压缩算法较新**（`zstd`/`lz4`）：老版 `unsquashfs` 报 `unknown compression`，升级 `squashfs-tools`。
- **UBI 镜像**：`binwalk` 只能识别 `UBI#`，要用 `ubireader_extract_images`。
- **加密固件**（如某些路由器的 `.bin` 头 `encr`）：找解密算法在 bootloader 或工具里。
- **固件头 CRC 校验**：重打包必须重算，否则刷不进去/题目校验失败。
- **MIPS 反编译**：Ghidra 的 MIPS 反编译质量一般，IDA 的 MIPS 更友好。
- **大端 MIPS**（BE）：`file` 显示 `MSB`，Ghidra 要选 `MIPS:BE:32:default`。
- **变体：只给单个二进制**（`httpd`）→ 直接逆向，看 CGI 处理逻辑。
- **变体：给 UART 日志** → 找 `/tmp/` 下的调试输出，常常泄漏 flag。
- **变体：加密的 rootfs + 启动脚本解密** → 分析 `rcS` 里的 `openssl`/`mtd` 命令。
- **注意**：`binwalk -e` 会递归解很多垃圾文件，用 `-M` 限制深度。

## 六、参考来源

- [OWASP — IoT Security Testing Guide](https://github.com/scriptingxss/owasp-fstm)
- [ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk)
- [onekey-sec/unblob](https://github.com/onekey-sec/unblob)
- [SquashFS 文档（squashfs-tools）](https://sourceforge.net/projects/squashfs/)
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra)
- [HackTricks — Firmware Analysis](https://book.hacktricks.wiki/en/hardware-physical-access/firmware-analysis/index.html)

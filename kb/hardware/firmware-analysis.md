---
title: 固件分析（binwalk 提取 / 文件系统 / 服务漏洞）
category: hardware
tags: [固件, binwalk, squashfs, ubi, 固件解包, 漏洞挖掘]
signals: [附件是固件 bin, binwalk 扫描出多个段, 需要找硬编码密码, 固件是 ubi 或 squashfs, 需要重打包固件, 题目要求跑固件里的服务]
difficulty: medium
source: "binwalk 官方仓库 / Recycler/固件解包实践 / PRET 打印机工具文档"
tools: [binwalk, firmware-mod-kit, unsquashfs, ubireader, jefferson, fatcat, firmwalker, qemu-user, PRET]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `firmware.bin` / `update.img`，几 MB 到几十 MB。
- `binwalk` 输出一堆 `Squashfs filesystem`、`UBI erase count header`、`gzip compressed data`。
- 题目问「固件里的 root 密码」「有多少个后门」。
- 需要找出固件里监听端口的程序，跑起来打它。

## 二、原理

固件通常由 **bootloader + kernel + rootfs + 应用** 打包。rootfs 常见格式：

| 格式 | 魔数/识别 | 解包工具 |
| --- | --- | --- |
| SquashFS | `hsqs`（小端）/`sqsh` | `unsquashfs` |
| CramFS | `0x28cd3d45` | `cramfsck` |
| JFFS2 | `0x1985` 节点头 | `jefferson` |
| UBI/UBIFS | `UBI#` | `ubireader_extract_images` |
| ext2/3/4 | `0x53EF` 在偏移 1080 | `mount -o loop` |
| TAR 内嵌 | `ustar` | `tar` |
| gzip 压缩的 tar | `1F 8B` | `zcat \| tar` |

**流程**：`binwalk` 扫描 → `-e` 分离 → 识别 FS → 解包 → 找 `/etc/passwd`、`/etc/shadow`、`rcS`、`init.d`、`www/`、`bin/` → `strings` 搜密码/命令 → 若有已知漏洞复现。

**重打包**：修 rootfs 后 `mksquashfs` 再拼回去，或用 firmware-mod-kit 一键 `build_firmware.sh`。

## 三、操作步骤

1. **`file` + `binwalk`**，列出所有段落与偏移。
2. **`binwalk -e`**（新版要 `--run-as`），得到 `_xxx.extracted/`。
3. **截断/加密**：若 binwalk 卡在中途，用 `dd` 按偏移手动切。
4. **解 FS**：`unsquashfs -d rootfs`，或 `unsquashfs -ll` 先列文件。
5. **搜线索**：`etc/passwd` 里有没有空密码、`rcS` 里启动了什么、`www` 里有没有备份文件。
6. **找漏洞**：`strings bin/* | grep -E 'system|popen'`，再有 `checksec`。
7. **重打包**：`mksquashfs` + 拼接。

## 四、命令/脚本

### 扫描与提取

```bash
file firmware.bin
binwalk firmware.bin
binwalk -e --run-as=root firmware.bin
ls -R _firmware.bin.extracted | head -40
# 加密/压缩嵌套：对提取出的每个文件再扫一遍
find _firmware.bin.extracted -type f -size +1k -exec binwalk {} \; 2>/dev/null | head -40
# 按签名 dd 出来
binwalk -e -D 'squashfs' firmware.bin
```

### 解文件系统

```bash
sudo apt install -y squashfs-tools
unsquashfs -ll _firmware.bin.extracted/*.squashfs | head -30
unsquashfs -d rootfs _firmware.bin.extracted/*.squashfs

# UBIFS
pip install ubi_reader
ubireader_extract_images firmware.bin
ubireader_extract_files ubi_img.ubifs.img -o ubifs_out

# CramFS / JFFS2 / FAT
sudo apt install -y cramfsprogs fatcat
cramfsck -x cramfs_out fs.cramfs
pip install jefferson && jefferson jffs2.img -d jffs2_out
fatcat rootfs.bin                     # FAT 镜像浏览
```

### 定制（firmware-mod-kit）

```bash
git clone https://github.com/rampageX/firmware-mod-kit
cd firmware-mod-kit/src
./extract-firmware.sh /path/firmware.bin      # 自动解到 fmk/rootfs
ls fmk/rootfs
# 修改 rootfs 后重打包
./build-firmware.sh -nodedocs
```

### 内容审计

```bash
# 密码与凭据
grep -rn 'root:' rootfs/etc/passwd rootfs/etc/shadow 2>/dev/null
grep -rn 'password\|passwd\|admin' rootfs/etc/ 2>/dev/null | head -20
# 启动脚本
cat rootfs/etc/init.d/rcS 2>/dev/null
cat rootfs/etc/rc.local 2>/dev/null
# 后门/命令执行
strings -n 6 rootfs/bin/* 2>/dev/null | grep -E 'system\(|popen|/bin/sh' | head
grep -rn 'curl\|wget\|nc -e' rootfs/etc rootfs/usr/sbin 2>/dev/null | head
# Web 目录
ls -la rootfs/www 2>/dev/null; ls -la rootfs/htdocs 2>/dev/null
# 私钥
find rootfs -name '*.key' -o -name '*.pem' -o -name 'id_rsa' | head
```

### 用 firmwalker 盲扫

```bash
git clone https://github.com/craigz28/firmwalker
./firmwalker.sh rootfs/ | tee firmwalker.log
grep -nE 'password|passwd|key|telnet|ssh' firmwalker.log | head -30
```

### 跑起来（QEMU 用户态模拟）

```bash
# 如果目标程序是 MIPS，用 qemu-user 直接跑
file rootfs/bin/busybox
sudo apt install -y qemu-user-static
sudo chroot rootfs /bin/busybox echo chroot_ok
# 或者只跑单个二进制
qemu-mipsel -L rootfs rootfs/usr/sbin/httpd -h
# 完整系统模拟（需要内核与 rootfs）
qemu-system-mipsel -M malta -kernel vmlinux -hda rootfs.img -append "root=/dev/sda console=ttyS0" -nographic
```

### 重打包

```bash
# SquashFS 结构：4 字节对齐 + 压缩块
mksquashfs rootfs new.squashfs -comp xz -b 65536 -noappend
# 替换回镜像（保持原始偏移与大小）
python3 - <<'PY'
orig = bytearray(open('firmware.bin','rb').read())
new  = open('new.squashfs','rb').read()
off  = orig.find(b'hsqs')           # 原 squashfs 起始
print('squashfs at', hex(off), 'new size', len(new), 'avail', len(orig)-off)
orig[off:off+len(new)] = new
open('firmware_mod.bin','wb').write(orig)
PY
```

### 打印机/网络设备固件（PRET）

```bash
# PRET 针对打印机 PJL/PostScript 的协议测试（对真机需授权）
git clone https://github.com/RUB-NDS/PRET
cd PRET && python2 pret.py TARGET pjl -i
```

## 五、常见坑 / 变体

- **binwalk 只扫到一部分**：镜像头部有厂商自定义头（如 `tplink` 的 `0123456789ABCDEF`），先 `dd` 跳过或按偏移切。
- **UBI 需要先提取 volume**：`ubireader_extract_images` 再 `extract_files`，不能直接 `unsquashfs`。
- **文件系统被 XOR 加密**：常见单字节 XOR，`binwalk` 扫不出时试 `xortool`。
- **大端/小端**：SquashFS 的 `hsqs` vs `sqsh` 就是端序标记。
- **权限与符号链接**：解包时用 `unsquashfs -no-xattrs` 避免失败；`chroot` 前要拷贝 `/etc/resolv.conf`。
- **ARM/MIPS 动态库**：`qemu-user -L` 指定 sysroot，否则 `No such file or directory`。
- **重打包大小超限**：新 FS 若比原镜像大，需要增大镜像并重算长度字段。

## 六、参考来源

- [binwalk 官方仓库（-e/-D/--run-as）](https://github.com/ReFirmLabs/binwalk)
- [firmware-mod-kit（extract/build 脚本）](https://github.com/rampageX/firmware-mod-kit)
- [firmwalker（rootfs 敏感信息扫描）](https://github.com/craigz28)
- [ubi_reader（UBIFS 提取）](https://github.com/onekey-sec/ubi_reader)
- [PRET - 打印机利用工具包](https://github.com/RUB-NDS/PRET)
- [CTF Wiki - ICS 利用阶段](https://ctf-wiki.org/ics/exploit/)

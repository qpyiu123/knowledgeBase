---
title: 磁盘镜像取证（sleuthkit / autopsy / 分区恢复）
category: forensics
tags: [磁盘镜像, sleuthkit, autopsy, 分区表, 文件系统, 恢复]
signals: [附件是 img 或 dd 镜像, 存在多个分区, 镜像里有被删除文件, 需要从镜像里提取 flag, 镜像很大, 文件系统是 ext4 或 ntfs]
difficulty: medium
source: "The Sleuth Kit 文档 / Autopsy 文档 / CTF-Wiki 磁盘内存分析"
tools: [sleuthkit, autopsy, mmls, fls, icat, tsk_recover, ewfmount, qemu-nbd, testdisk, photorec]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `disk.img` / `disk.dd` / `disk.E01` / `disk.vmdk` / `disk.vhd`，体积几百 MB 到几 GB。
- `file` 说是 `DOS/MBR boot sector` 或 `Linux rev 1.0 ext4 filesystem`。
- 题目说「从镜像里恢复被删除的文件」「找到隐藏分区」。
- `fdisk -l` 显示多个分区，但挂载后只有一个能看。

## 二、原理

磁盘镜像 = 磁盘扇区的逐字节复制。分析分三层：

1. **分区层**：MBR（偏移 446 起 4×16 字节分区表）或 GPT（LBA1 的 `EFI PART`）。`mmls` 输出偏移与大小。
2. **文件系统层**：ext2/3/4、NTFS、FAT、APFS 等。文件条目（inode / MFT record）与数据块分离存放，**删除只清元数据标记**，数据块往往还在——所以能恢复。
3. **应用层**：从文件系统里提取文件，再走 misc 流程。

**Sleuth Kit 的哲学**：不挂载（避免污染），直接用 `fls` 列目录、`icat` 按 inode 取数据、`tsk_recover` 批量恢复。

## 三、操作步骤

1. **判类型与分区**：`file disk.img`、`mmls disk.img`、`fdisk -l disk.img`。
2. **列出文件**：`fls -r -p -o OFFSET disk.img | head`，找到用户目录。
3. **提取**：`icat -o OFFSET disk.img INODE > out.bin`。
4. **恢复删除项**：`fls` 加 `-d` 看删除条目，`tsk_recover` 批量导出。
5. **挂载查看（可选）**：`mount -o ro,loop,offset=$((OFFSET*512)) disk.img /mnt`。
6. **深度恢复**：`photorec` 按文件签名雕刻（见 `file-carving` 篇）。

## 四、命令/脚本

### 分区层

```bash
file disk.img
mmls disk.img                     # 推荐：输出 Offset(扇区) 与 Slot
fdisk -l disk.img                 # 分区起止扇区
parted -s disk.img unit s print   # 另一种视角
# GPT 镜像
gdisk -l disk.img
# 加密镜像（VeraCrypt/LUKS）
cryptsetup luksDump disk.img
```

### 文件系统层（Sleuth Kit）

```bash
# 注意 -o 是"扇区"偏移，来自 mmls 的 Start 列
fls -o 2048 disk.img                       # 根目录
fls -r -o 2048 disk.img | head -50          # 递归
fls -r -o 2048 disk.img | grep -iE 'flag|secret|key|pass|zip|png'
fls -rd -o 2048 disk.img | head             # -d 只看已删除
icat -o 2048 disk.img 12345 > file_out       # 按 inode 提取
ils -o 2048 disk.img | head                  # 列出 inode
istat -o 2048 disk.img 12345                 # inode 详情（含时间戳）
tsk_recover -o 2048 disk.img out_dir/        # 批量恢复全部文件
tsk_recover -o 2048 -a disk.img out_dir/     # -a 仅已分配文件
```

### 挂载（只读）

```bash
sudo mkdir -p /mnt/d
sudo mount -o ro,loop,offset=$((2048*512)) disk.img /mnt/d
ls -la /mnt/d; find /mnt/d -name '*flag*'
sudo umount /mnt/d
```

### 特殊镜像格式

```bash
# E01 (EnCase) 需要 ewftools
sudo apt install -y ewf-tools
sudo mkdir /mnt/e && sudo ewfmount disk.E01 /mnt/e
mmls /mnt/e/ewf1                     # 挂上后就是一个 raw 设备
# VHD
sudo modprobe nbd max_part=16
sudo qemu-nbd -c /dev/nbd0 disk.vhd
sudo mmls /dev/nbd0
# VMDK
sudo qemu-nbd -c /dev/nbd0 disk.vmdk
# QCOW2
qemu-img info disk.qcow2 && qemu-img convert -O raw disk.qcow2 disk.raw
```

### 时间线分析

```bash
# 全盘时间线（便于找"最后写入"的数据）
fls -r -m '/' -o 2048 disk.img > body.txt
mactime -b body.txt -d -z UTC +2026-01-01 -2026-12-31 | head -40
# 或用 tsk 的 mactime 全量并按时间倒序
mactime -b body.txt 2>/dev/null | tail -30
```

### 分区被删/表坏时

```bash
# 扫描备份分区表
testdisk disk.img            # 交互式：Analyse -> Quick Search -> 写回
# 直接按文件签名恢复
photorec disk.img            # 交互式，选分区后选文件类型
# 手工扫分区边界（MBR 分区表备份在 0x1BE 与 GPT header 在 LBA1）
python -c "
d=open('disk.img','rb').read(4096); print(d[446:446+64].hex())"
```

## 五、常见坑 / 变体

- **`-o` 单位是扇区**：`mmls` 的 Start 直接填，不要换算成字节。
- **分区表里有"隐藏分区"**：`mmls` 会列 Slot，注意 start 在很后面的那个。
- **镜像被分割**：`disk.001 disk.002 ...`，先 `cat disk.0* > disk.img` 合并。
- **镜像加了偏移头**：有些题在镜像前塞了几百字节垃圾，用 `binwalk` 或搜索 `55 AA`/`EFI PART` 找真实起点后 `dd` 截取。
- **NTFS 的 ADS（备用数据流）**：`fls -r` 会显示 `:stream` 条目，`icat` 可提取。
- **ext4 的 journal 回放**：`sudo mount -o ro,norecovery` 避免修改镜像。
- **不要用可写挂载**：会改镜像内容，破坏证据链。
- **跨域**：内存镜像见 `memory-forensics-volatility`，文件雕刻见 `file-carving`。

## 六、参考来源

- [The Sleuth Kit 手册（mmls/fls/icat/tsk_recover）](https://www.sleuthkit.org/sleuthkit/man/)
- [Autopsy 用户手册（Sleuth Kit 官方）](https://www.sleuthkit.org/autopsy/docs/user-docs/4.21.0/)
- [CTF Wiki - 磁盘内存分析](https://ctf-wiki.org/misc/disk-memory/introduction/)
- [TestDisk & PhotoRec 官方站](https://www.cgsecurity.org/wiki/TestDisk)
- [ewfmount / ewf-tools 说明](https://github.com/libyal/libewf)
- [qemu-nbd 挂载 VHD/VMDK 指南](https://wiki.qemu.org/Documentation/GettingStartedDevelopers)

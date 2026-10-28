---
title: 文件雕刻与恢复（foremost / binwalk / photorec）
category: forensics
tags: [文件雕刻, foremost, scalpel, photorec, binwalk, 数据恢复]
signals: [磁盘镜像里有已删除文件, 内存 dump 里有 zip 片段, 需要按文件类型批量恢复, 分区表损坏, binwalk 分离不完整, 文件头尾都在但中间缺]
difficulty: easy
source: "foremost 手册 / PhotoRec 文档 / Sleuth Kit (blkls/fls) / binwalk 文档"
tools: [foremost, scalpel, photorec, binwalk, blkls, testdisk, dd, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一个镜像/内存 dump，说「有一个文件被删了」。
- `fls` 列不出目标文件，但 `strings` 能看到 `PK`、`%PDF`、`\x89PNG`。
- 文件系统损坏，`mount` 失败。
- `binwalk -e` 只分离出一部分，需要按签名扫描整盘。

## 二、原理

**文件雕刻（carving）** 不依赖文件系统元数据，而是按**文件签名（magic）+ 结构**从原始字节流中切出文件：

- **有明确尾标记**：JPEG `FF D9`、PNG `IEND`+CRC、GZIP（有长度字段）、PDF `%%EOF`——可以精确切。
- **无尾标记**：DOCX/ZIP 靠中央目录找边界；MP4 靠 `moov`/`mdat` 长度；有些只能靠启发式。
- **碎片化问题**：文件在磁盘上不连续时，单段切出会损坏。foremost 支持部分修复，但**真正碎片化**的文件需要按簇重组（研究级问题）。

**foremost** 用 `foremost.conf` 定义签名与最大长度；**scalpel** 是它的性能优化分支，支持头尾正则匹配；**photorec** 是 TestDisk 套件里的交互式雕刻器，支持 480+ 格式。

## 三、操作步骤

1. **确认是原始数据**：镜像直接给 foremost；分区镜像先 `mmls` 取偏移，`dd` 切出分区。
2. **首选 foremost**：`foremost -t all -i img -o out/`，看输出报告。
3. **换 scalpel**：格式覆盖率不同，`scalpel img -o out`。
4. **交互式 photorec**：复杂格式用 photorec 选文件类型。
5. **binwalk**：内嵌格式（zip 套 zip、图片套图片）用 binwalk 的签名表最直观。
6. **验证**：`file` + `pngcheck`/`unzip -t`，挑出完整可用的。

## 四、命令/脚本

### foremost

```bash
apt install -y foremost
foremost -t all -i disk.img -o out_all/            # 所有内置类型
foremost -t png,jpg,gif,zip,pdf -i disk.img -o out/ # 指定类型（更快）
foremost -v -T -i disk.img -o out/                  # -v 详细 -T 带时间戳
cat out/audit.txt | head -40                        # 报告：每个文件的偏移与状态
# 自定义签名：编辑 /etc/foremost.conf
#   png  y  200000000  \x89PNG\x0d\x0a\x1a\x0a  \x49\x45\x4e\x44\xae\x42\x60\x82
```

### scalpel

```bash
apt install -y scalpel
cp /etc/scalpel/scalpel.conf /etc/scalpel/scalpel.conf.bak
# 编辑配置，去掉目标类型前的注释
scalpel -c /etc/scalpel/scalpel.conf -o out_scalpel/ disk.img
```

### photorec（交互 + 配置驱动）

```bash
photorec disk.img                 # 交互：选分区 -> 选文件系统 -> 选类型 -> 选输出目录
photorec /log /d out_ph /cmd disk.img fileopt,everything,enable,search   # 无交互
```

### binwalk 签名扫描

```bash
binwalk disk.img | head -40
binwalk -e --run-as=root disk.img        # 分离
binwalk --dd='png:png:1000000' disk.img  # 按自定义类型 dd
binwalk -A disk.img                      # 架构扫描（找代码段）
```

### 按偏移手工切（最精确）

```python
#!/usr/bin/env python3
# carve_by_sig.py —— 按签名 + 结构长度精确切出 PNG/JPEG/ZIP/GZIP
import struct, sys, os, zlib

SIGS = {
    'png': (b'\x89PNG\r\n\x1a\n', b'IEND\xaeB`\x82'),
    'jpg': (b'\xff\xd8\xff', b'\xff\xd9'),
    'pdf': (b'%PDF-', b'%%EOF'),
    'gzip': (b'\x1f\x8b\x08', None),      # 尾部靠解压判断
    'zip': (b'PK\x03\x04', None),         # 尾部靠 EOCD 回扫
}

def carve(data, name):
    head, tail = SIGS[name]
    out, i, n = [], 0, 0
    while True:
        s = data.find(head, i)
        if s < 0:
            break
        if tail:
            e = data.find(tail, s)
            if e < 0:
                break
            e += len(tail)
        elif name == 'zip':
            e = data.find(b'PK\x05\x06', s)
            if e < 0:
                break
            e += 22 + struct.unpack('<H', data[e+20:e+22])[0]   # + 注释长度
        else:                               # gzip：用 zlib 逐字节尝试
            d = zlib.decompressobj(31); i = s
            try:
                d.decompress(data[s:s+50_000_000])
                e = s + 50_000_000 - len(d.unused_data)
            except zlib.error:
                i = s + 1
                continue
        out.append((s, data[s:e]))
        n += 1
        i = e
    for idx, (s, blob) in enumerate(out):
        fn = f'{name}_{idx}_{s:x}.{ "jpeg" if name=="jpg" else name}'
        open(fn, 'wb').write(blob)
        print(fn, len(blob))
    return n

if __name__ == '__main__':
    data = open(sys.argv[1], 'rb').read()
    types = sys.argv[2].split(',') if len(sys.argv) > 2 else ['png', 'jpg', 'zip']
    for t in types:
        carve(data, t)
```

```bash
python carve_by_sig.py disk.img png,jpg,zip
for f in *.png; do pngcheck -q "$f" && echo "OK $f"; done
for f in *.zip; do unzip -t "$f" >/dev/null 2>&1 && echo "OK $f"; done
```

### 用 Sleuth Kit 只雕未分配空间（更快更准）

```bash
# 只对未分配块做雕刻——音量小一个数量级
mmls disk.img                                # 取分区起始扇区 START
blkls -o START disk.img > unalloc.dd          # 导出未分配空间
foremost -i unalloc.dd -o out_unalloc/
# 或者按块大小估算文件系统
fsstat -o START disk.img | head -20
```

### 碎片重组思路（进阶）

```bash
# 1) 先按簇大小把文件系统切片
fsstat -o 2048 disk.img | grep -i 'block size'
# 2) 逐块扫描签名，记录块号
for b in $(seq 0 100000); do :; done    # 用 python 更高效
# 3) 用 photofilmstrip / blkls + 位移算法（论文级）重组
# 实用做法：先用 tsk_recover 试"按 inode 恢复"，失败再做雕刻
tsk_recover -o 2048 -a disk.img recovered/    # -a 只恢复已分配（完整文件）
```

## 五、常见坑 / 变体

- **顺序极性**：`foremost -t all` 慢，先按 `strings` 猜类型再限定。
- **PNG 尾标记**：必须在 `IEND` 后 4 字节 CRC 才算完整，否则 pngcheck 会报错。
- **ZIP 尾**：EOCD 之后可能有 22+ 注释长度，要按字段算。
- **重叠切出**：一个位置可能同时被两种签名命中（如 ZIP 里的 PNG），去重时看偏移。
- **加密/压缩数据**：雕刻出来的文件可能还能用（ZIP 加密仍能打开要密码）。
- **不要覆盖原镜像**：所有操作只读，输出到独立目录。
- **速度**：foremost 单线程，大镜像可以 `split` 成多段并行，最后合并去重。

## 六、参考来源

- [foremost 官方站（配置与用法）](https://foremost.sourceforge.net/)
- [PhotoRec 官方文档](https://www.cgsecurity.org/wiki/PhotoRec)
- [scalpel 手册（Kali 文档）](https://www.kali.org/tools/scalpel/)
- [Sleuth Kit 的 blkls/fsstat 手册](https://www.sleuthkit.org/sleuthkit/man/)
- [binwalk 官方仓库（--dd 与分离）](https://github.com/ReFirmLabs/binwalk)
- [CTF Wiki - 磁盘内存分析](https://ctf-wiki.org/misc/disk-memory/introduction/)

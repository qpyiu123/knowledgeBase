---
title: JPG 图片隐写（DCT/outguess/steghide/EXIF）
category: misc
tags: [jpg, jpeg, 隐写, steghide, outguess, jsteg]
signals: [给了一张 jpg, zsteg 在 jpg 上没结果, 图片里有密码提示, 文件尾部有额外数据, EXIF 里有奇怪注释, 图片尺寸与被裁切不一致, 需要密码才能解出隐藏文件]
difficulty: medium
source: "CTF-Wiki JPG 章节 / Aperi'Solve JPEG checklist / steghide 与 stegseek 文档 / OutGuess 主页"
tools: [steghide, stegseek, outguess, jsteg, exiftool, binwalk, aperisolve]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `.jpg`，题面说「照片里还有东西」「密码是文件名」。
- `zsteg` 对这张图**没有任何输出**（正常，zsteg 只支持 PNG/BMP）。
- `exiftool` 的 `Comment`、`UserComment`、`XPComment` 里有一串可疑字符串。
- 图片看起来是普通风景照，但文件有 2 MB，像素尺寸却只有 800×600。
- `binwalk` 在 `FFD9` 之后发现 `PK` 或 `PKCS7`。
- 题面提示「空密码试试」——这是 `steghide -p ''` 的经典暗示。

## 二、原理

JPEG 是**有损**压缩，像素 LSB 在编码时会被量化抹掉，所以 PNG 那套像素 LSB 工具（zsteg）在这里**无效**。JPEG 隐写分两大流派：

1. **DCT 系数域**：JPEG 把图像切成 8×8 块做 DCT 变换，得到的量化系数用于熵编码。
   - `steghide`：把数据嵌入 DCT 系数，**带密码 + 默认加密**，没有密码无法提取，只支持 JPEG/BMP/WAV/AU。
   - `OutGuess`：修正版 LSB，保留 DCT 直方图统计特性，抗卡方检验；`-r` 提取。
   - `JSteg/F5/jphide`：更老的一批，F5 还有 `-e` 加密选项；对应提取工具 `jsteg reveal`、`f5`、`jpseek`。
2. **容器/元数据域**：EXIF（含内嵌缩略图）、`FFD9` 之后的追加数据、注释段 `COM (FFFE)`。这一类 `binwalk`/`exiftool` 就能搞定。

**判断用哪个工具**：`steghide info` 能识别文件是否被 steghide 处理过；`stegseek` 则是"暴力 + 字典"版 steghide，跑 rockyou 只要几秒。

## 三、操作步骤

1. **元数据与尾部**：`exiftool -a -u -g1`，`binwalk`，`tail -c 200 | xxd` 看是否以 `FFD9` 结束。
2. **内嵌缩略图**：导出 `ThumbnailImage`——很多题的原图/未打码图就在这里。
3. **steghide 先试空密码**，再试文件名/题名/`strings` 里出现的词。
4. **stegseek 字典爆破**（比 steghide 快几个数量级）。
5. **换算法**：`outguess -r`、`jsteg reveal`、`f5`。
6. **仍未出**：检查是否 polyglot（JPEG/ZIP），把尾部截出来当 zip 解。

## 四、命令/脚本

### 元数据 + 结构排查

```bash
exiftool -a -u -g1 target.jpg                     # 所有标签，含 Comment/XPComment
exiftool -b -ThumbnailImage target.jpg > thumb.jpg && file thumb.jpg
strings -n 6 -e l target.jpg | grep -iE 'flag|pass|key|ctf'
tail -c 16 target.jpg | xxd                        # 应看到 ffd9；否则有追加数据
binwalk -e --run-as=root target.jpg
foremost -i target.jpg -o out/
```

### steghide 系列

```bash
steghide info target.jpg                          # 判断是否 steghide 处理过
steghide extract -sf target.jpg -p ''             # 先试空密码
steghide extract -sf target.jpg -p 'PASSWORD'     # 再试文件名/题名/元数据里的词
stegseek target.jpg /usr/share/wordlists/rockyou.txt   # 字典爆破（秒级）
stegseek --crack target.jpg rockyou.txt out.txt
stegseek -sf target.jpg -xf out.bin rockyou.txt   # 指定输出文件
```

### OutGuess / JSteg / F5 / jphide

```bash
outguess -r target.jpg out.txt                    # extract
outguess -k 'PASSWORD' -r target.jpg out.txt       # 带 key
jsteg reveal target.jpg out.txt                   # （需自行编译 jsteg）
f5 -d target.jpg out.txt -p PASSWORD              # F5 提取
jpseek target.jpg out.txt -p PASSWORD             # JPHide/JPSeek
stegbreak -f /usr/share/dict/words -t target.jpg  # 常见于 jphide/outguess 爆破
```

> 冷门提示：**`steghide` 不支持 PNG/GIF**，做 PNG 题时不要浪费时间；反之 zsteg 不支持 JPEG。这是新手最常见的卡点。

### 提取 FFD9 之后数据

```bash
python - <<'PY'
d = open('target.jpg','rb').read()
i = d.rfind(b'\xff\xd9')          # 最后出现的 EOI
tail = d[i+2:]
open('tail.bin','wb').write(tail)
print('tail', len(tail), tail[:16])
PY
file tail.bin
```

### 用循环跑一遍常见空密码/弱口令（WSL 环境）

```bash
sudo apt install -y steghide stegseek outguess exiftool binwalk foremost
for pw in "" "PASSWORD" "flag" "admin"; do
  steghide extract -sf target.jpg -p "$pw" -xf "out_${pw:-empty}.bin" 2>/dev/null && echo "hit: '$pw'"
done
```

## 五、常见坑 / 变体

- **steghide 密码在题面**：题名、图片主题词、`exiftool` 里的 Artist/Title、`strings` 里的第一个可读词，都值得试。
- **stegseek 比 steghide 快**：字典爆破优先用 stegseek，它的提取速度是数量级优势。
- **图片被重新保存过**：用 PS 打开再另存会**破坏 DCT 系数的隐写**，题目若给"处理后"图可能就解不出了，先看元数据里的 Software 字段。
- **JPEG polyglot**：JPG 与 ZIP 拼接很常见，`binwalk` 会给出 `Zip archive data, at offset N`。
- **EXIF 缩略图**：用 `exiftool -b -ThumbnailImage` 导出后单独做 PNG/JPG 分析，很多题的真实内容在缩略图里。
- **量化表指纹**：肉眼看不出隐写时，用 `stegdetect`/`jpegdump` 判断是否被 outguess/F5/jsteg 修改过。
- **混合手法**：steghide 提取出一个 base64 → 还原成文本 → 里面又是 OutGuess 的 key，注意套娃。

## 六、参考来源

- [CTF Wiki - JPG 图片分析](https://ctf-wiki.org/misc/picture/jpg/)
- [Aperi'Solve 速查表（JPEG 分支）](https://www.aperisolve.com/cheatsheet)
- [Steghide 官方站（含命令行文档）](https://github.com/Steghide/steghide)
- [stegseek - 极快的 steghide 破解器](https://github.com/RickdeJager/stegseek)
- [OutGuess 官方主页](https://www.outguess.org/)
- [exiftool 标签大全](https://exiftool.org/TagNames/)

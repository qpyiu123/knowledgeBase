---
title: 视频隐写（MP4/MKV box 结构、帧级隐写、ffmpeg 提取）
category: misc
tags: [video, mp4, mkv, ffmpeg, frame-stego, mvhd]
signals: [给了一段 mp4 或 mkv 视频, 视频结尾黑屏但时长还有几秒, 某些帧画面闪一下就能看到一行字, 视频里只有一帧和别的不一样, 文件大小远大于码率估算值, mkvinfo 显示有很多没见过的 tag, moov 的时长和实际解码帧数对不上, 视频能正常播放但 binwalk 扫出额外文件, 题目说 flag 在视频的每秒里]
difficulty: medium
source: "ISO/IEC 14496-12 MP4 规范 / Matroska 官方规范 / ffmpeg 文档 / CTF-Wiki 视频隐写"
tools: [python, ffmpeg, ffprobe, mkvtoolnix, MP4Box, strings, binwalk]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.mp4` / `.mkv` / `.avi` / `.flv`，题目说"看完这段视频"。
- 视频末尾有几秒纯黑或纯色，播放器进度条还有，内容是空的——**尾部追加数据**。
- 某些帧里有一闪而过的文字、二维码或色块，正常播放速度下看不清。
- `binwalk video.mp4` 扫出 `IEND`、`PK\x03\x04`、`7z` 之类的额外签名。
- `mkvinfo`：元素树里出现一堆 `SimpleTag`（`COMMENT`、`TITLE`，内容像 base64）。
- `ffprobe` 的 `duration` 与 `nb_frames / r_frame_rate` 严重不符。
- `mdat` box 长度字段比实际数据短，后面跟着一堆"未知"字节。
- 题面提示"24 帧每秒""第 1 帧开始""慢放看看"。

## 二、原理

- **容器结构是抓手**：MP4 是 box（`size(4) type(4) payload`）树，顶层依次 `ftyp` / `moov` / `mdat` / `free`。`size=0` 表示延伸到文件尾，`size=1` 时使用 64 位 largesize。**任何 box 之后、`mdat` 之后追加的数据（尾部数据）播放器一律忽略**，是最廉价的隐写位置。
- **`moov` 里的元数据是第二抓手**：`udta` → `meta` → `ilst` 里可以放任意 `©xxx` 项（`©nam`、`©cmt`、`©too`），改一行就能塞 key。MKV 则是 `Tags` → `SimpleTag`。
- **帧级隐写**分三种：
  1. 单帧承载内容（某一帧放整张二维码），需要逐帧导出。
  2. 每帧取极少像素做 LSB，需要把 N 帧拼成一条长位流。
  3. 帧间差异（只改关键帧、或 I/P/B 帧类型序列本身编码信息）。
- **未使用区域**：H.264 的 slice 末尾有 trailing bits，`avcC` 里有 SPS/PPS，理论上都能承载，但工具少、手写脚本为主。
- **时间维度泄漏**：PTS/DTS 的微调、帧率不变但最后一帧重复次数不同，都能编码少量 bit。

## 三、操作步骤

1. **容器结构走查**：用 python 脚本按 box 递归打印，找 `size` 与实际不符、`free`/`skip` 超大的位置。
2. **尾部数据检查**：`binwalk`，再从 `mdat` 结束偏移 `dd` 出尾部。
3. **元数据检查**：`ffprobe -show_format -show_streams`、`exiftool`、`mkvinfo -v`。
4. **拆帧**：`ffmpeg -i in.mp4 frames/%05d.png`，然后对关键帧单独跑 zsteg/exiftool。
5. **帧间差异**：用 `compare` 或 python(OpenCV/PIL) 求相邻帧差，定位"唯一不同的那一帧"。
6. **LSB 跨帧组装**：把每帧某一行/某一列提取出来，按帧顺序拼接成二进制。
7. **音轨也别放过**：视频里的音频先导成 wav，按音频隐写思路走（频谱、LSB、SSTV）。

## 四、命令 / 脚本

```bash
# 结构与元数据
ffprobe -v error -show_format -show_streams target.mp4
ffprobe -v error -count_frames -show_entries stream=nb_read_frames,r_frame_rate,avg_frame_rate,duration target.mp4
exiftool -a -u -g1 target.mp4
mkvinfo -v target.mkv
MP4Box -info target.mp4 2>&1 | head -40

# 尾部/嵌入数据
binwalk target.mp4
strings -n 8 target.mp4 | grep -iE 'flag|key|ctf|pass'

# 拆帧（全部）
mkdir -p frames && ffmpeg -v error -i target.mp4 frames/%05d.png
# 只抽每隔 10 帧 / 只抽前 20 帧
ffmpeg -v error -i target.mp4 -vf "select='not(mod(n,10))'" -vsync 0 frames/step_%05d.png
ffmpeg -v error -i target.mp4 -frames:v 20 frames/first_%05d.png

# 音轨导出
ffmpeg -v error -i target.mp4 -vn -acodec pcm_s16le audio.wav
```

```python
#!/usr/bin/env python3
# MP4 box 树打印 + 尾部数据检测
import struct, sys

CONTAINERS = {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'udta',
              b'meta', b'ilst', b'edts', b'dinf'}

def walk(d, start, end, depth=0):
    p = start
    while p + 8 <= end:
        size, typ = struct.unpack('>I4s', d[p:p+8])
        hdr = 8
        if size == 1:
            size = struct.unpack('>Q', d[p+8:p+16])[0]; hdr = 16
        elif size == 0:
            size = end - p
        if size < hdr or p + size > end:
            print('  ' * depth + '[!] 非法 box size=%d type=%r @%d' % (size, typ, p))
            break
        print('  ' * depth + '%-4s size=%-9d off=%d' %
              (typ.decode('latin1', 'replace'), size, p))
        if typ in CONTAINERS:
            child = p + hdr
            if typ == b'meta':          # meta 多 4 字节 version/flags
                child += 4
            walk(d, child, p + size, depth + 1)
        elif typ == b'mdat':
            print('  ' * (depth + 1) + '--> mdat 结束于 %d，文件总长 %d' % (p + size, end))
        p += size
    if p < end:
        print('[+] %d 字节尾部数据 @%d' % (end - p, p))
        open('tail.bin', 'wb').write(d[p:end])

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    walk(d, 0, len(d))
```

```python
#!/usr/bin/env python3
# 帧差检测：找出与前一帧差异最大的帧
import sys, glob
from PIL import Image, ImageChops

files = sorted(glob.glob(sys.argv[1]))
prev, scores = None, []
for f in files:
    im = Image.open(f).convert('L')
    if prev is not None:
        diff = ImageChops.difference(prev, im)
        hist = diff.histogram()
        scores.append((sum(i * h for i, h in enumerate(hist)), f))
    prev = im
scores.sort(reverse=True)
for s, f in scores[:10]:
    print('%12d  %s' % (s, f))
```

## 五、常见坑 / 变体

- **`size=0` 的 mdat**：很多录制工具把 mdat 写成延伸到文件尾，此时"尾部分析"会误判为没有尾部数据，要按"最后一个已知 box 的结束位置"手工确认。
- **moov 在 mdat 之后**（`faststart` 之外的常规顺序）：说明 moov 是剪辑软件重新写的，`udta` 里常带软件名和时间戳。
- **帧序号从 0 还是 1 开始**：`ffmpeg` 的 `%05d` 从 1 起，`select=n` 里 n 从 0 起，题目说"第 100 帧"时要对齐清楚。
- **抽帧别用 `-vsync 0` 默认丢帧**：变帧率视频会导致帧数与预期不符，加 `-vsync 0` 或 `-fps_mode passthrough`。
- **MKV 是 EBML 可变长整数**，`SimpleTag` 里的 `String` 元素直接把 flag 写成二进制；用 `mkvextract tags` 一步导出。
- **视频里嵌入另一个完整文件**：`binwalk -e` 命中后直接 `dd`；常见 `IEND` + `PK` 组合。
- **LSB 跨帧的提取参数**：需要知道"取哪些像素、哪一位、什么顺序"，题目通常给出"每秒一个 bit"之类的元信息，没有的话就用暴力组合脚本扫。
- **不要忘了字幕轨**：MKV 的 `Subtitle` 轨可以是 `S_TEXT/UTF8`，`mkvextract tracks x.mkv 2:sub.srt` 直接读。

## 六、参考来源

- [MP4 容器格式详解（box/atom 结构）](https://agama.tv/demystifying-the-mp4-container-format/)
- [MP4 文件结构：Boxes、Atoms、Tracks（ftyp/moov/mdat）](https://www.simalabs.ai/resources/mp4-file-structure-explained-boxes-atoms-tracks)
- [ffmpeg 抽帧常用参数讨论（-vf select / fps_mode）](https://stackoverflow.com/questions/8679390/ffmpeg-extracting-20-images-from-a-video-of-variable-length)
- [Matroska 官方规范（EBML 与 Tags 元素）](https://www.matroska.org/technical/specs/index.html)
- [CTF-Wiki：Misc 隐写技巧总览](https://ctf-wiki.org/misc/introduction/)

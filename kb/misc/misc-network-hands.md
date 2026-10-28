---
title: 流量包入门（pcap 快速定位与数据提取）
category: misc
tags: [pcap, 流量分析, wireshark, tshark, 导出对象, 追踪流]
signals: [附件是 pcap/pcapng, 题目说你截到了流量, 流量文件很大, 需要找上传的文件, 需要还原登录密码, 流量里有大量重复请求]
difficulty: easy
source: "CTF-Wiki 流量包分析简介 / Wireshark 用户手册 / tshark 手册"
tools: [wireshark, tshark, tcpdump, editcap, capinfos, NetworkMiner]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `.pcap` / `.pcapng` / `.cap`，题干「我们捕获到一段流量」。
- 让你「找出黑客上传的文件」「还原管理员密码」「分析攻击手法」。
- 流量文件几十 MB 但真正有效载荷只有几条。
- `file` 说是 `tcpdump capture` 但打不开（文件头被改）。

## 二、原理

pcap 是**链路层帧序列**：`全局头(24B) + 多条 [记录头(16B) + 原始帧]`。分析流程本质是「**筛选 → 重组 → 提取**」：

1. **筛选**：按协议/端口/IP/关键字过滤，缩小到几十条。
2. **重组**：TCP 是字节流，需要按序号拼回完整会话（Wireshark 的 "Follow TCP Stream" 就是干这个）。
3. **提取**：导出 HTTP 对象、FTP 文件、SMB 文件、USB 键值、DNS 查询名、TLS 明文。

**魔数**：pcap 小端 `d4 c3 b2 a1`，纳秒版 `4d 3c b2 a1`；pcapng `0a 0d 0d 0a`。文件头被改时，改回魔数 + 正确的 linktype 即可打开。

## 三、操作步骤

1. **体检**：`capinfos` 看时长/包数/协议；`tshark -r x.pcap -q -z io,phs` 看协议分层统计。
2. **挑会话**：`Statistics → Conversations`，按字节数排序，异常会话通常就是目标。
3. **找关键字**：`tshark -r x.pcap -Y 'frame contains "flag"'`，或 `-T fields -e http.file_data`。
4. **追踪流**：Wireshark `Follow → TCP/HTTP Stream`，看明文与文件。
5. **导出对象**：`File → Export Objects → HTTP/SMB/FTP`。
6. **继续套娃**：导出的图片/压缩包再走 misc 流程。

## 四、命令/脚本

### 基础信息

```bash
capinfos target.pcap                 # 包数、时长、链路类型、哈希
tshark -r target.pcap -q -z io,phs   # 协议分层统计
tshark -r target.pcap -c 20          # 只看前 20 个包
editcap -A '2026-01-01 00:00:00' target.pcap out.pcap   # 时间裁剪
```

### 会话与端点

```bash
tshark -r target.pcap -q -z conv,tcp | sort -k5 -n -r | head
tshark -r target.pcap -q -z endpoints,ip
tshark -r target.pcap -q -z http,tree
tshark -r target.pcap -q -z follow,tcp,ascii,0    # 第 0 条 TCP 流的 ASCII
```

### 关键字搜索与字段提取

```bash
tshark -r target.pcap -Y 'frame contains "flag"' -T fields -e frame.number -e _ws.col.Info
tshark -r target.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri | sort -u
tshark -r target.pcap -Y 'http.response' -T fields -e http.content_type -e http.content_length | sort | uniq -c
tshark -r target.pcap -Y 'dns.qry.name' -T fields -e dns.qry.name | sort -u | head -50
tshark -r target.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.dst -e tcp.dstport | sort | uniq -c
```

### 导出文件（不靠 GUI）

```bash
# 所有 HTTP 对象
tshark -r target.pcap --export-objects http,out_http
ls -la out_http/
# 所有 SMB/DCERPC 对象（Wireshark 4.x）
tshark -r target.pcap --export-objects smb,out_smb
# 把某条流的原始字节写出来
tshark -r target.pcap -q -z follow,tcp,raw,0 | sed '1,2d;$d' | tr -d ' \n' | xxd -r -p > stream0.bin
```

### 修复被改坏的 pcap 头

```python
#!/usr/bin/env python3
# pcap_fix.py —— 抢救被抹掉/改错的 pcap 全局头
import struct, sys
d = bytearray(open(sys.argv[1], 'rb').read())
sigs = {b'\xd4\xc3\xb2\xa1': 1, b'\xa1\xb2\xc3\xd4': 1,
        b'\x4d\x3c\xb2\xa1': 1, b'\xa1\xb2\x3c\x4d': 1}
if d[:4] not in sigs:
    print('[!] 头不对，尝试按 pcapng 或修补')
    if d[:4] != b'\x0a\x0d\x0d\x0a':
        d[:4] = b'\xd4\xc3\xb2\xa1'
        # linktype=1 (Ethernet)，version 2.4
        d[4:24] = struct.pack('<HHiIII', 2, 4, 0, 0, 65535, 1)
        open(sys.argv[1].replace('.pcap', '_fixed.pcap'), 'wb').write(d)
        print('[+] 已重建 pcap 头 -> *_fixed.pcap')
else:
    print('[i] 头正常:', d[:4].hex(), 'linktype =', struct.unpack('<I', d[20:24])[0])
```

### 用 scapy 做自定义重组

```python
#!/usr/bin/env python3
# pcap_extract.py —— 提取所有 TCP 载荷并输出可读文本
from scapy.all import rdpcap, TCP, Raw
sessions = {}
for p in rdpcap('target.pcap'):
    if TCP in p and Raw in p:
        key = (p[TCP].sport, p[TCP].dport)
        sessions.setdefault(key, bytearray()).extend(bytes(p[Raw].load))
for k, v in sorted(sessions.items(), key=lambda kv: -len(kv[1]))[:5]:
    print('==', k, len(v))
    print(bytes(v[:300]))
```

## 五、常见坑 / 变体

- **链路类型不对**：非以太网（USB/Linux SLL/WiFi）要 `editcap -T` 或按 `linktype` 选解析器。
- **pcapng 与 pcap 混用**：`editcap -F pcap in.pcapng out.pcap` 转换。
- **时间戳异常**：排序后前几条时间颠倒，说明被 `editcap` 混过，按 `frame.number` 看。
- **gzip/megacap**：`tcpdump -z gzip` 生成的带 `.gz` 后缀，先解压。
- **大文件**：`tshark` 加 `-2` 两遍分析、`-Y` 过滤再处理，避免内存爆掉。
- **USB 流量**：见 `kb/forensics/` 的流量隐写与键盘流量篇；Wireshark 里 `usb.capdata`。
- **misc 与 forensics 交叉**：入门只看这里，深入（TCP 重组、HTTPS 解密、隧道识别）见 forensics 目录。

## 六、参考来源

- [CTF Wiki - 流量包分析简介](https://ctf-wiki.org/misc/traffic/introduction/)
- [CTF Wiki - 数据提取](https://ctf-wiki.org/misc/traffic/data/)
- [Wireshark 用户手册](https://www.wireshark.org/docs/wsug_html_chunked/)
- [tshark 手册（man page）](https://www.wireshark.org/docs/man-pages/tshark.html)
- [Scapy 文档](https://scapy.readthedocs.io/en/latest/)
- [pcap 文件格式说明（tcpdump.org）](https://www.tcpdump.org/manpages/pcap-savefile.5.html)

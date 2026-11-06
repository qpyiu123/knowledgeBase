---
title: 流量分析基础（Wireshark 追踪流 / 导出对象 / TCP 重组）
category: forensics
tags: [wireshark, tshark, pcap, 追踪流, 导出对象, tcp重组]
signals: [附件是 pcap, 需要还原上传的文件, 需要找管理员密码, 流量包很大, 题目问 hacker 做了什么, 需要看 htt p 明文, 需要还原登录名密码]
difficulty: easy
source: "CTF-Wiki 流量包分析 / Wireshark 用户手册 / tshark 手册页"
tools: [wireshark, tshark, capinfos, editcap, tcpflow, NetworkMiner, scapy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `capture.pcap`，题干「分析这段流量，找出被泄露的数据」。
- 题目问「黑客上传了什么文件」「管理员的账号密码是多少」。
- 流量几十 MB，`Statistics → Protocol Hierarchy` 里 HTTP 占比很高。
- 需要看某条 HTTP 请求的完整 body（比如 POST 上传的附件）。

## 二、原理

TCP 是**有重叠、乱序、可能丢包**的字节流。Wireshark 的分析能力建立在三件事上：

1. **TCP 流重组**：按四元组（srcIP, sport, dstIP, dport）+ 序列号把分片拼回连续字节流。`Follow → TCP Stream` 和 `-z follow,tcp` 都是这个。
2. **协议解析（dissector）**：认出 HTTP 后，把 body 交给 `http.file_data`，于是能"导出对象"。
3. **过滤器**：BPF 抓包语法 + 显示过滤（`http.request.uri contains "admin"`）。

**导出对象** 的底层逻辑：对每个 HTTP response，若 `Content-Type` 或 `Content-Disposition` 表明是文件，就把 body 落盘，文件名取自 URL 末段或 `Content-Disposition`。

### USB 抓包：先确认接口类型

先分 PCAP 和 PCAPNG 两种文件容器，再读链路类型。经典 PCAP 的类型在文件头；PCAPNG 可有多个接口，要用每个数据包的接口编号找对应的接口描述块。类型 220 对应 Linux 的 64 字节 usbmon 头；类型 249 对应 Windows USBPcap。两种包头的字段位置不同。认对头后再按方向、端点和传输类型筛选键盘等设备的数据。

## 三、操作步骤

1. **宏观**：`capinfos` + `io,phs`（协议分层）→ 判断主要协议。
2. **会话**：`conv,tcp`/`endpoints,ip` 排序 → 找最大的那几条流。
3. **过滤**：按 host / uri / method 列请求，找 `/upload`、`/admin`、`/login`。
4. **追踪流**：对可疑流 `Follow HTTP Stream`，看请求头和响应体。
5. **导出**：`--export-objects http,out`，把文件落盘后 `file` 判类型。
6. **深挖**：拿到的图片/压缩包 → 走 misc 流程；拿到的密码 → 找后续登录请求。

## 四、命令/脚本

### 宏观统计

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z io,phs
tshark -r capture.pcap -q -z conv,tcp | head -20
tshark -r capture.pcap -q -z http,tree
tshark -r capture.pcap -q -z io,stat,1,"COUNT(frame) frame"
```

### 找可疑流量

```bash
# 所有 HTTP 请求行
tshark -r capture.pcap -Y http.request -T fields \
  -e frame.number -e ip.src -e http.host -e http.request.method -e http.request.uri
# 只看 POST（上传）
tshark -r capture.pcap -Y 'http.request.method=="POST"' -T fields \
  -e frame.number -e http.request.uri -e http.content_length
# 关键字
tshark -r capture.pcap -Y 'frame contains "password" or frame contains "flag"' \
  -T fields -e frame.number -e _ws.col.Info
# 登录表单（明文 HTTP POST）
tshark -r capture.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data | head -c 500
```

### 导出对象

```bash
tshark -r capture.pcap --export-objects http,out_http
ls -la out_http
for f in out_http/*; do echo "$f: $(file -b "$f")"; done
# SMB / FTP（Wireshark 4.x 支持 smb）
tshark -r capture.pcap --export-objects smb,out_smb
tshark -r capture.pcap -Y 'ftp-data' -T fields -e data.data
```

### 追踪某条流（命令行）

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,3      # 第 3 条 TCP 流
tshark -r capture.pcap -q -z follow,http,ascii,3
# 导出该流原始字节
tshark -r capture.pcap -q -z follow,tcp,raw,3 | sed '1,2d;$d' | tr -d ' \n' | xxd -r -p > stream3.bin
```

### 用 Python 重组（需要更精细控制时）

```python
#!/usr/bin/env python3
# reassemble.py —— 按四元组重组 TCP 流，按序列号排序，处理重传与重叠
import collections
from scapy.all import rdpcap, IP, TCP, Raw

flows = collections.defaultdict(dict)
for p in rdpcap('capture.pcap'):
    if IP in p and TCP in p and Raw in p:
        k = (p[IP].src, p[TCP].sport, p[IP].dst, p[TCP].dport)
        seq = p[TCP].seq
        flows[k][seq] = bytes(p[Raw].load)      # 同 seq 覆盖（保留最后一次）

for k, seg in sorted(flows.items(), key=lambda kv: -sum(len(v) for v in kv[1].values()))[:5]:
    out, next_seq = bytearray(), None
    for s in sorted(seg):
        d = seg[s]
        if next_seq is None:
            out += d; next_seq = s + len(d)
        elif s < next_seq:                       # 重叠，跳过已收到的部分
            out += d[next_seq - s:]
            if s + len(d) > next_seq:
                next_seq = s + len(d)
        else:                                    # 空洞，补齐 0x00 以便对齐
            out += b'\x00' * (s - next_seq); out += d; next_seq = s + len(d)
    name = f'flow_{k[0]}_{k[1]}_{k[2]}_{k[3]}.bin'
    open(name, 'wb').write(bytes(out))
    print(name, len(out), repr(bytes(out[:80])))
```

### tcpflow / 一键分文件

```bash
apt install -y tcpflow
tcpflow -r capture.pcap -o flows/
ls flows/ | head
# 每个四元组一个文件，直接 strings 找 flag
grep -ral 'flag{' flows/
```

## 五、常见坑 / 变体

- **Wireshark "追踪流"看不到内容**：可能是 TLS（走 `sslkeylogfile`），或协议端口异常（把 HTTP 放在 8080，需 `Decode As`）。
- **导出对象为空**：`Content-Type` 是 `application/octet-stream` 且无 filename 时，Wireshark 不导出，需要手工 `-z follow,tcp,raw`。
- **重组出乱码**：中间有丢包/乱序，用脚本按 seq 排序，或 `tcpflow` 更稳。
- **HTTP/2 的 pcap**：明文 h2 需要 `Decode As HTTP2`，加密的见 `http2-and-quic` 篇。
- **大包内存**：`tshark -2` 两遍模式吃内存，先 `editcap -A/-B` 按时间裁。
- **前置任务**：文件头坏了的 pcap 先用 `pcap_fix` 思路修复（见 misc 的 `misc-network-hands`）。

## 六、参考来源

- [CTF Wiki - 流量包分析（Wireshark/HTTP/DNS/USB）](https://ctf-wiki.org/misc/traffic/introduction/)
- [CTF Wiki - 协议分析 - Wireshark](https://ctf-wiki.org/misc/traffic/protocols/wireshark/)
- [Wireshark 用户手册（Follow Stream / Export Objects）](https://www.wireshark.org/docs/wsug_html_chunked/)
- [tshark 手册页](https://www.wireshark.org/docs/man-pages/tshark.html)
- [tcpflow 官方站](https://github.com/simsong/tcpflow)
- [Scapy 文档](https://scapy.readthedocs.io/en/latest/)

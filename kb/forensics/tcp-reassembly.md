---
title: TCP 流重组与端口扫描识别
category: forensics
tags: [tcp, 重组, 端口扫描, syn扫描, 时序, 异常流量]
signals: [流量里有大量 S YN 包, 同一源 IP 扫了很多端口, 需要判断扫描类型, 需要还原一次完整会话, 存在重传与乱序, 需要统计被扫端口]
difficulty: medium
source: "Wireshark 用户手册 / Nmap 端口扫描原理 / RFC 793 / tcpflow 文档"
tools: [tshark, wireshark, nmap, tcpflow, pyshark, scapy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目问「攻击者扫描了哪些端口 / 用了什么扫描方式」。
- 流量里 `TCP SYN` 数量远大于 `ACK`，且目标端口递增。
- 大量 `RST, ACK` 回复——典型的**半开扫描**特征。
- 需要还原一段被切碎/乱序的会话（比如跨几十个包传一个大文件）。
- 流量里出现 `TCP Out-Of-Order`、`TCP Retransmission` 提示。

## 二、原理

**TCP 三次握手**：`SYN → SYN,ACK → ACK`。扫描器利用对握手的响应差异判断端口状态：

| 扫描类型 | 发送 | 开放端口响应 | 关闭端口响应 |
| --- | --- | --- | --- |
| TCP Connect (`-sT`) | 完整三次握手 | 握手成功后主动 RST | RST,ACK |
| SYN 半开 (`-sS`) | 只发 SYN | SYN,ACK（扫描器不再回 ACK） | RST,ACK |
| FIN/NULL/XMAS (`-sF/-sN/-sX`) | 特殊标志位 | **无响应** | RST,ACK |
| ACK (`-sA`) | 只发 ACK | RST | RST（用于判断防火墙） |
| 全连接速率 | 端口递增 1 | 有若干 SYN,ACK | 绝大多数 RST,ACK |

**统计特征**：扫描流量一般表现为"**同一源 IP → 同一目标 IP，短时间内 dst port 高度离散**，绝大多数会话只有 1~2 个包"。而正常业务是"少数几条长会话"。

**流重组**：按 `(src,sport,dst,dport)` 分组，再用 `seq` 排序拼接。需要注意：
- 重叠段（retransmission with different data）取**先到的**（Linux 实现通常是先到的胜出）。
- 空洞不要填补进正文，否则解析错位。

## 三、操作步骤

1. **扫描识别**：`tshark -Y 'tcp.flags.syn==1 && tcp.flags.ack==0'` 统计源/目的端口分布。
2. **判定类型**：看是否有对应的 `SYN,ACK` 和 `RST`：
   - 有 SYN,ACK 但没后续 ACK → `-sS`；
   - 只有 RST,ACK → `-sF/-sN/-sX` 或者被防火墙拒绝；
   - 有完整握手 → `-sT`。
3. **列出被扫端口**：提取所有 `dstport`，排序去重。
4. **找突破点**：被扫端口中"有实际数据交互"的那几个就是靶点。
5. **重组会话**：对靶点端口 `Follow TCP Stream` 或 tcpflow。
6. **补充证据**：时间线、包间隔、User-Agent（如果有应用层）。

## 四、命令/脚本

### SYN 包统计

```bash
# 所有 SYN（不含 SYN,ACK）
tshark -r scan.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn | head -30
# 被扫端口列表
tshark -r scan.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e tcp.dstport | sort -n | uniq | tr '\n' ' '
# 完整握手数量（判断 -sT）
tshark -r scan.pcap -Y 'tcp.flags==0x12' -T fields -e tcp.dstport | sort -n | uniq -c
# RST 响应
tshark -r scan.pcap -Y 'tcp.flags.reset==1' -T fields -e ip.src -e tcp.srcport | sort | uniq -c | head
```

```python
#!/usr/bin/env python3
# scan_classify.py —— 统计每种扫描的指纹，推断扫描方式
import collections
from scapy.all import rdpcap, IP, TCP

syn = collections.Counter(); synack = collections.Counter()
rst = collections.Counter(); ack = collections.Counter()
fin = collections.Counter(); nullp = collections.Counter()
pairs = collections.Counter()

for p in rdpcap('scan.pcap'):
    if IP not in p or TCP not in p:
        continue
    f = int(p[TCP].flags)
    dport = p[TCP].dport
    if f == 0x02:
        syn[dport] += 1; pairs[(p[IP].src, p[IP].dst)] += 1
    elif f == 0x12:
        synack[dport] += 1
    elif f & 0x04:
        rst[dport] += 1
    elif f == 0x10:
        ack[dport] += 1
    elif f & 0x01 and f & 0x08:
        fin[dport] += 1
    elif f == 0:
        nullp[dport] += 1

print('top src->dst:', pairs.most_common(3))
print('SYN  ports:', len(syn),  'top:', syn.most_common(5))
print('SYNACK ports:', len(synack), '=> 开放:', sorted(synack))
print('RST  ports:', len(rst))
print('FIN ports:', len(fin), 'NULL ports:', len(nullp))
if synack and len(syn) > 3 * len(synack):
    print('结论: 半开 SYN 扫描 (-sS)')
elif len(fin) or len(nullp):
    print('结论: FIN/NULL/XMAS 隐蔽扫描')
elif len(ack) > len(syn):
    print('结论: ACK 扫描（探测防火墙）')
else:
    print('结论: 全连接扫描 (-sT) 或普通连接')
```

### 时间线（判断速率与分组）

```bash
tshark -r scan.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e frame.time_relative -e tcp.dstport | head -40
# 每秒 SYN 数
tshark -r scan.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_epoch | \
  awk '{printf "%d\n", $1}' | uniq -c
```

### 会话重组（重点：看应用层数据）

```bash
# 先找出真正有数据的流（载荷非空）
tshark -r scan.pcap -Y 'tcp.len>0' -T fields -e tcp.stream -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn | head
# 按流号跟随
tshark -r scan.pcap -q -z follow,tcp,ascii,42
# 全部落盘，每个四元组一个文件
tcpflow -r scan.pcap -o flows/ && grep -ral 'flag{' flows/
```

### 用 scapy 精确重组（考虑重叠与空洞）

```python
#!/usr/bin/env python3
# reassemble_strict.py —— 以接收端视角重组，先到先得，记录空洞
import collections, sys
from scapy.all import rdpcap, IP, TCP, Raw

target = int(sys.argv[1]) if len(sys.argv) > 1 else 0
streams = collections.defaultdict(list)
for p in rdpcap(sys.argv[2] if len(sys.argv) > 2 else 'scan.pcap'):
    if IP in p and TCP in p and Raw in p:
        if p[TCP].dport == target or p[TCP].sport == target:
            streams[(p[IP].src, p[TCP].sport, p[IP].dst, p[TCP].dport)].append(
                (p[TCP].seq, bytes(p[Raw].load)))

for k, segs in streams.items():
    buf, base = {}, None
    for seq, d in segs:
        if base is None:
            base = seq
        for i, b in enumerate(d):
            buf.setdefault(seq + i, b)          # 先到先得
    lo, hi = min(buf), max(buf)
    out = bytes(buf.get(i, 0) for i in range(lo, hi + 1))
    holes = sum(1 for i in range(lo, hi + 1) if i not in buf)
    print(k, 'bytes', len(out), 'holes', holes)
    print(out[:200])
```

## 五、常见坑 / 变体

- **扫描源是多个 IP**：分布式扫描，别只按第一个源 IP 统计。
- **`RST` 也可能来自中间设备**：防火墙拒绝 vs 主机关闭，看 TTL 是否变化。
- **UDP 扫描**：`-sU` 没有 SYN，看 `ICMP port unreachable` 数量。
- **应用层识别**：有些题会在扫描后跟一次暴力破解（大量 401/200），用 `http.response.code` 统计。
- **重组流号变化**：`tcp.stream` 是 Wireshark 内部编号，脚本处理时用四元组更稳。
- **IPv6**：`ipv6.src` 字段，过滤器要改。
- **时间被改过**：`frame.time_relative` 可能被截断，需要 `editcap` 修复。

## 六、参考来源

- [CTF Wiki - 流量分析概述](https://ctf-wiki.org/misc/traffic/introduction/)
- [CTF Wiki - 协议分析](https://ctf-wiki.org/misc/traffic/protocols/readme/)
- [Wireshark 显示过滤器参考](https://www.wireshark.org/docs/dfref/)
- [Nmap 端口扫描技术（官方文档）](https://nmap.org/book/man-port-scanning-techniques.html)
- [RFC 793 - TCP 规范](https://datatracker.ietf.org/doc/html/rfc793)
- [tshark follow 与统计功能](https://www.wireshark.org/docs/man-pages/tshark.html)

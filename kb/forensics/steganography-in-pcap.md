---
title: 流量中的隐写（ICMP/DNS 隧道与隐蔽信道）
category: forensics
tags: [流量隐写, icmp隧道, dns隧道, 隐蔽信道, tunneling, covert channel]
signals: [大量 icmp 包 payload 很长, dns 查询域名特别长, 一个域名下大量子域, 定时定量的心跳包, 流量总字节数异常, 只有出站没有入站]
difficulty: hard
source: "CTF-Wiki DNS 流量分析 / Wireshark 隧道检测 / dns2tcp/iodine 实现"
tools: [tshark, wireshark, dnschef, dnscat2, script1002, python, scapy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 流量里 ICMP 包很多，且每个 `echo request` 的 payload 是 32/56 字节的**随机 16 进制或 base64**。
- DNS 查询里出现 `aGVsbG8=.evil.com`、`x1.2.3.tunnel.io` 这类**超长子域**。
- 同一个域名下短时间内几百条不同子域的 `A/TXT/MX` 查询。
- 出站流量远大于入站，且目标 IP 固定、端口可疑（53/5353/8080）。
- 题目说「数据是偷偷运出去的」。

## 二、原理

隧道（tunneling）本质是**把数据编码进协议允许的自定义字段**：

| 协议 | 可载字段 | 典型工具 | 可观测特征 |
| --- | --- | --- | --- |
| ICMP | Echo 的 `data` 字段 | ping tunnel、icmpsh | payload 长度固定且不为 0，内容高熵 |
| DNS | 左侧标签（子域）+ `TXT` 记录 | iodine、dnscat2、dns2tcp | 子域长度 > 30、字符集是 base32/base64 |
| HTTP | `Cookie`、`X-*` 头、URI | 各种 C2 | 请求 URI 极长、Cookie 高熵 |
| TCP | 保留位/URG 指针 | 少见 | 无数据会话却有异常标志 |
| IPv6 | 扩展头的 payload | | 少见 |

**ICMP 隐写**：标准 ping 的 data 常是 0x41 填充或递增序列；若 data 是**随机字节**或 base64 文本，几乎可以确定是隧道。还原方法：按 `icmp.seq` 排序，把每个包的 `data.data` 拼接（先去重前 8 字节的时间戳头）。

**DNS 隐写**：数据编码在子域里，通常每包 20~60 字节。解码流程 = 取所有查询名 → 切掉隧道域名后缀 → 按 id/序号排序 → base32/base64 解码 → 拼接。

## 三、操作步骤

1. **协议占比**：`io,phs` 判断是 ICMP 还是 DNS 主导。
2. **提取 payload**：`icmp.data.data` 或 `dns.qry.name` 字段，导出为文本。
3. **判编码**：字符集是 `[a-z0-9]` → base36/base32；含 `=` 或 `+/` → base64。
4. **排序**：按 `icmp.seq` / DNS 的 `id` 或时间戳排序。
5. **解码**：`base64 -d` / `base32 -d`，或自定义字母表。
6. **验证**：解出的内容 `file` 判类型，常是 zip/png/明文。

## 四、命令/脚本

### ICMP 隧道提取

```bash
# 先看 ICMP 概况
tshark -r tunnel.pcap -Y icmp -T fields -e frame.number -e ip.src -e icmp.type -e icmp.seq -e data.len | head -20
# 导出 data 字段（hex）
tshark -r tunnel.pcap -Y 'icmp.type==8' -T fields -e icmp.seq -e data.data > icmp.txt
head -3 icmp.txt
```

```python
#!/usr/bin/env python3
# icmp_extract.py —— 按 seq 排序 ICMP payload，清理固定头部后拼成文件
import sys, binascii, base64, re

rows = []
for line in open(sys.argv[1], encoding='utf8', errors='ignore'):
    parts = line.strip().split('\t')
    if len(parts) < 2 or not parts[1]:
        continue
    rows.append((int(parts[0]), parts[1].replace(':', '')))

rows.sort()
raw = [binascii.unhexlify(h) for _, h in rows]
print('packets:', len(rows), 'first lens:', [len(r) for r in raw[:8]])

# 很多隧道工具前一包带固定头（时间戳 8 字节），先统计所有包的公共前缀长度
common = 0
if raw:
    while common < min(len(r) for r in raw) and \
            len({r[common] for r in raw}) == 1:
        common += 1
    print('common prefix bytes:', common, raw[0][:common].hex())

data = b''.join(r[common:] for r in raw)
open('icmp_raw.bin', 'wb').write(data)

# 尝试把每包当独立 base64 段解码
dec = []
for r in raw:
    s = re.sub(rb'[^A-Za-z0-9+/=]', b'', r)
    try:
        dec.append(base64.b64decode(s + b'=' * (-len(s) % 4)))
    except Exception:
        pass
open('icmp_b64.bin', 'wb').write(b''.join(dec))
print('b64 out:', sum(map(len, dec)))
```

```bash
python icmp_extract.py icmp.txt
file icmp_raw.bin icmp_b64.bin
strings -n 5 icmp_b64.bin | head
```

### DNS 隧道提取

```bash
# 所有查询名
tshark -r tunnel.pcap -Y 'dns.flags.response==0' -T fields -e frame.number -e dns.qry.name | head -20
tshark -r tunnel.pcap -Y 'dns.qry.name' -T fields -e dns.qry.name > dns.txt
# 统计隧道域名（出现次数最多的后缀）
awk -F. '{print $(NF-1)"."$NF}' dns.txt | sort | uniq -c | sort -rn | head
# 统计子域长度（正常 < 25，隧道往往 > 40）
awk -F. '{print length($1)}' dns.txt | sort -n | uniq -c | tail -5
```

```python
#!/usr/bin/env python3
# dns_extract.py —— 从 DNS 查询名中提取隐蔽数据并解码
import re, base64, sys, collections

names = [l.strip() for l in open(sys.argv[1]) if l.strip()]
# 后缀 = 出现最频繁的两级域名
suffix = collections.Counter(
    '.'.join(n.split('.')[-2:]) for n in names).most_common(1)[0][0]
print('tunnel suffix:', suffix, 'queries:', len(names))

labels = []
for n in names:
    if n.endswith(suffix):
        sub = n[: -len(suffix) - 1]
        # 取最长的那一段（dnscat2/iodine 把数据放在最左）
        labels.append(max(sub.split('.'), key=len))

text = ''.join(labels)
print('chars:', len(text), 'sample:', text[:80])

for enc in ('base32', 'base64'):
    payload = text.upper() if enc == 'base32' else text
    try:
        if enc == 'base32':
            raw = base64.b32decode(payload + '=' * (-len(payload) % 8))
        else:
            raw = base64.b64decode(re.sub(r'[^A-Za-z0-9+/=]', '', payload)
                                   + '=' * 4)
        open(f'dns_{enc}.bin', 'wb').write(raw)
        print(f'[{enc}] {len(raw)} bytes -> dns_{enc}.bin', raw[:40])
    except Exception as e:
        print(f'[{enc}] failed: {e}')

# 十六进制线路
if re.fullmatch(r'[0-9a-fA-F]+', text[:200] or 'x') and len(text) % 2 == 0:
    try:
        open('dns_hex.bin', 'wb').write(bytes.fromhex(text))
        print('[hex] ok')
    except Exception as e:
        print('[hex] failed', e)
```

### 其他隐蔽信道

```bash
# HTTP Cookie / X 头
tshark -r x.pcap -Y 'http.cookie' -T fields -e http.cookie | sort -u | head
tshark -r x.pcap -Y 'http.request' -T fields -e http.request.uri | awk '{print length($0)}' | sort -n | tail -5
# TCP 保留位（无数据但有标志的异常包）
tshark -r x.pcap -Y 'tcp.len==0 && tcp.flags.res!=0' -T fields -e frame.number
# 时序信道：包间隔编码
tshark -r x.pcap -Y 'ip.src==10.0.0.5' -T fields -e frame.time_delta | \
  python3 -c "
import sys
v=[float(x) for x in sys.stdin if x.strip()]
bits=''.join('1' if d>0.5 else '0' for d in v)
print(bytes(int(bits[i:i+8],2) for i in range(0,len(bits)-7,8))[:80])"
```

### 判断是哪种工具（指纹）

```bash
# iodine: 子域多为 base32，含 'a' 开头
# dnscat2: 子域形如 'xxxxxxxxxxxxxxxxxxxxx' + 固定前缀
# dns2tcp: 请求中含 'i'/'c' 类型前缀
tshark -r x.pcap -Y dns -T fields -e dns.qry.name | cut -c1-12 | head -20
```

## 五、常见坑 / 变体

- **ICMP data 含 checksum/时间戳**：不同内核 ping 的固定头不同，先看前 8 字节是否全相同，相同就去掉。
- **DNS 包乱序**：必须按 `dnscat2` 的序号字段排序，字母序拼会得到乱码。
- **base32 vs base36**：字符集只含 `0-9a-v` 是 base32（小写），含全字母是 base36。
- **每次查询携带多段**：有的工具把数据切在中间标签而非最左。
- **配合加密**：解出后是密文，需在题目别处找密钥（常见为固定字符串/KDF）。
- **ICMPv6**：字段是 `icmpv6`，`data.data` 依然可用。
- **DNS over HTTPS**：那就是 TLS 流量，见 `http2-and-quic` 篇解密。

## 六、参考来源

- [CTF Wiki - DNS 流量分析](https://ctf-wiki.org/misc/traffic/protocols/dns/)
- [CTF Wiki - 数据提取](https://ctf-wiki.org/misc/traffic/data/)
- [Wireshark 显示过滤器（icmp/dns 字段）](https://www.wireshark.org/docs/dfref/)
- [iodine - DNS 隧道工具（原理说明）](https://github.com/yarrick/iodine)
- [dnscat2 - DNS 隐蔽信道](https://github.com/iagox86/dnscat2)
- [icmptunnel 实现](https://github.com/jamesbarlow/icmptunnel)

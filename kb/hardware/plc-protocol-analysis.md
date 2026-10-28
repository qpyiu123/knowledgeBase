---
title: 工控协议（Modbus 与 S7comm 报文分析）
category: hardware
tags: [modbus, s7comm, ics, plc, wireshark, scapy]
signals: [抓包里有 502 或 102 端口, 题目说这是工控网络流量, 需要还原 PLC 寄存器被写入的值, 报文里出现协议 ID 0x32, wireshark 识别为 Modbus/TCP, 题目问攻击者改了哪个寄存器]
difficulty: medium
source: "Wireshark 官方 Modbus/TCP 与 S7comm 显示过滤器文档 / 工控协议公开规范"
tools: [python, wireshark, tshark, pymodbus, snap7, scapy]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 抓包里出现 `502`（Modbus/TCP）或 `102`（S7comm/ISO-TSAP）端口。
- 题面说"某工厂被植入后门""PLC 被篡改"，要求还原写入的值。
- Wireshark 直接解析为 `Modbus/TCP` 或 `S7 Communication`。
- ARP 里 PLC 与 HMI 之间周期性通信，单位 ID（unit id）固定。
- 存在 `0x10`（写多寄存器）、`0x06`（写单寄存器）这类写操作。
- 题目问"哪个寄存器被改成了多少"。

## 二、原理

**Modbus/TCP（502）**：MBAP 头 7 字节：

```
Transaction ID(2) Protocol ID(2)=0x0000 Length(2) Unit ID(1) Function Code(1) Data...
```

功能码：`0x01` 读线圈、`0x03` 读保持寄存器、`0x05` 写单线圈、`0x06` 写单寄存器、`0x10` 写多寄存器、`0x2B` 设备标识。

**S7comm（102，ISO-on-TCP）**：TPKT + COTP + S7 三层：

- `0x03 00` 是 TPKT 版本与保留；
- COTP 里 `0xE0` 是连接请求，`0xF0` 是数据；
- S7 头 `0x32` 是协议 ID（S7comm），`0x72` 是 S7comm-plus；
- 功能：`0x04` Read Var、`0x05` Write Var、`0x1A` 请求下载。

**写操作语义**：Modbus 的 `0x10` 报文里 `Starting Address(2) Quantity(2) Byte Count(1) Values...`，每个寄存器 2 字节；把 Values 按顺序填回地址空间即可还原 PLC 内存。

## 三、操作步骤

1. **确认协议**：`tshark -r x.pcap -q -z io,phs` 看协议层次。
2. **筛写操作**：Modbus 用 `mbtcp.func==16 || mbtcp.func==6`，S7 用 `s7comm.header.rosctr==1`。
3. **提取地址与值**：逐包解析起始地址与数据，按时间排序。
4. **重建寄存器快照**：用字典 `reg[addr] = value` 回放所有写操作。
5. **找关键寄存器**：题目通常指明地址，或要你找出第一个非默认值。
6. **交叉验证**：用 `pymodbus` 定义描述或直接 dump 成表。

## 四、命令 / 脚本

```bash
# 协议层次与端口
tshark -r ics.pcap -q -z io,phs
# Modbus 写操作
tshark -r ics.pcap -Y 'mbtcp.func==16 || mbtcp.func==6' \
  -T fields -e frame.number -e mbtcp.reference_num -e mbtcp.word_cnt -e mbtcp.regval
# S7comm 请求
tshark -r ics.pcap -Y 's7comm.header.rosctr==1' \
  -T fields -e frame.number -e ip.src -e s7comm.param.func
# 全部 Modbus 报文摘要
tshark -r ics.pcap -Y mbtcp -T fields -e frame.number -e ip.src -e ip.dst -e mbtcp.func -e mbtcp.reference_num
```

```python
#!/usr/bin/env python3
# Modbus/TCP 写操作回放：从 pcap 还原寄存器最终值
from scapy.all import rdpcap, TCP, Raw
import struct, sys

def parse_mbap(pkt):
    payload = bytes(pkt[Raw].load) if Raw in pkt else b''
    if len(payload) < 8:
        return None
    tid, pid, length, uid = struct.unpack('>HHHB', payload[:7])
    if pid != 0:
        return None
    return tid, uid, payload[7], payload[8:]

def replay(path):
    regs, coil = {}, {}
    for p in rdpcap(path):
        if not (TCP in p and p[TCP].dport == 502):
            continue
        r = parse_mbap(p)
        if not r:
            continue
        tid, uid, func, data = r
        if func == 0x10 and len(data) >= 5:               # 写多寄存器
            addr, qty, bc = struct.unpack('>HHB', data[:5])
            vals = [struct.unpack('>H', data[5 + i*2:7 + i*2])[0] for i in range(qty)]
            for i, v in enumerate(vals):
                regs[addr + i] = v
            print('WRITE @%d qty=%d -> %s' % (addr, qty, vals))
        elif func == 0x06 and len(data) >= 4:             # 写单寄存器
            addr, val = struct.unpack('>HH', data[:4])
            regs[addr] = val
            print('WRITE @%d -> %d' % (addr, val))
        elif func == 0x05 and len(data) >= 4:             # 写单线圈
            addr, val = struct.unpack('>HH', data[:4])
            coil[addr] = 1 if val == 0xFF00 else 0
            print('COIL  @%d -> %d' % (addr, coil[addr]))
    return regs, coil

if __name__ == '__main__':
    regs, coil = replay(sys.argv[1])
    print('\n最终寄存器快照:', dict(sorted(regs.items())))
```

```python
#!/usr/bin/env python3
# S7comm WriteVar 解析（0x32 + ROSCTR=1 + func=5）
import struct

def parse_s7_write(payload):
    if payload[0] != 0x32 or payload[1] != 0x01:
        return None
    pdu_ref, plen_dl, plen_dr = struct.unpack('>HHH', payload[4:10])
    param = payload[10:10 + plen_dl]
    if param[0] != 0x05:
        return None
    count, out, off = param[1], [], 2
    for _ in range(count):
        item = param[off:off + 12]
        db = struct.unpack('>H', item[4:6])[0]
        addr = (item[7] << 16) | (item[8] << 8) | item[9]
        out.append((item[6], db, addr))
        off += 12
    data = payload[10 + plen_dl:10 + plen_dl + plen_dr]
    return out, data.hex()

if __name__ == '__main__':
    print(parse_s7_write(bytes.fromhex('320100000001000e0005000101120a1002000000010000')))
```

## 五、常见坑 / 变体

- **Modbus 地址基准**：报文里 `reference_num` 从 0 开始，文档常写 `40001` 起，差 1；题面给 `40001` 时要减一。
- **`0x10` 的 Byte Count**：是字节数（值数量 ×2），算错就会多读/少读。
- **S7comm 的 TPKT 分段**：报文可能被 TCP 分段，`scapy` 直接取 `Raw` 会拿到半包，要先做流重组。
- **S7comm-plus（0x72）**：S7-1500 默认使用，字段完全不同，无法直接读值。
- **单位 ID 混淆**：一个网关上多个从站，`unit id` 不同代表不同 PLC，聚合时要带上。
- **变体**：DNP3（`0xC0 0x01` 起始）、IEC 104（`0x68` 起始的 APCI）、OPC-UA、EtherNet/IP（CIP 封装）。

## 六、参考来源

- [Wireshark 官方：Modbus/TCP 显示过滤器参考](https://www.wireshark.org/docs/dfref/m/mbtcp.html)
- [Wireshark Wiki：S7comm 协议字段说明（协议 ID 0x32）](https://wiki.wireshark.org/S7comm)
- [Wireshark 抓 Modbus TCP 并诊断（chipkin）](https://docs.chipkin.com/articles/wireshark-modbus-tcp-capture-filter-diagnose/)
- [pymodbus 官方文档（寄存器语义）](https://pymodbus.readthedocs.io/en/latest/)
- [snap7：S7 协议通讯库与抓包对照](https://github.com/SCADACS/snap7)

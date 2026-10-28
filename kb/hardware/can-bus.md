---
title: CAN 总线攻击（车载/工控报文分析）
category: hardware
tags: [can总线, can-utils, obd, 车载, 报文注入, ICS]
signals: [附件是 can 报文日志, 题目提到车载或工控总线, 需要还原 can 帧里的数据, 有大量 id 相同的帧, 需要重放某个 id 序列]
difficulty: medium
source: "can-utils 文档 / CiA CAN 规范概览 / ICS 安全实践（CTF-Wiki ICS）"
tools: [can-utils, python-can, canmatrix, SavvyCAN, ICSim, Wireshark]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.asc`（Candump ASCII）、`.blf`（Vector）、`.log`（candump）格式。
- 题目说「车主说车被黑了」「从 CAN 总线抓包」。
- 日志里每行形如 `(1620000000.123456) can0 7DF#0201050000000000`。
- 需要根据车速/转速变化找 flag。

## 二、原理

CAN 是**多主广播**总线：所有节点共享两条差分线（CAN_H/CAN_L），帧结构：

```
SOF(1) | Identifier(11 或 29 bit) | RTR | IDE | r0 | DLC(4) | Data(0~8B) | CRC(15) | ACK | EOF(7)
```

要点：

- **ID 不是地址，是优先级**：ID 越小优先级越高。0x7DF 是 OBD-II 的功能寻址请求 ID。
- **没有认证/加密**：任何节点都能注入任意 ID 与数据 → 重放、伪造、DoS 都可行。
- **OBD-II**：标准 500 kbps，请求/响应模式，`0x7DF` 发请求，`0x7E8~0x7EF` 收响应。
- **现代车用 CAN-FD**（64 字节负载）+ 网关/域控做隔离，但老车与工控设备仍纯 CAN。

**常见攻击**：重放（记录刹车/门锁帧再发）、伪造速度/转速、总线泛洪导致 ECU 掉线、诊断模式下 `UDS` 请求（`0x02 0x10 0x03` 进扩展会话）。

## 三、操作步骤

1. **格式化日志**：`.asc`/`.blf` 转 text，统一成 `timestamp id#data`。
2. **统计 ID 分布**：找出现频率最高/最低的 ID，异常 ID 往往是攻击注入的。
3. **按 ID 看数据变化**：转速随车速变化，观察一段时间序列。
4. **对比正常/异常时段**：题面常给两个日志，diff 出差异 ID。
5. **提取数据**：把某个 ID 的 payload 按时间拼起来，`strings`/hex 解码。
6. **重放**：在模拟环境里用 `cansend` 复现。

## 四、命令/脚本

### 解析日志

```bash
# candump 日志转人类可读
candump -L -r can.log 2>/dev/null | head      # 回放模式读取
# .asc 是 Vector ASCII，直接文本处理
head -20 capture.asc
# 统计每个 ID 出现次数
awk '{print $4}' can.log 2>/dev/null | cut -d'#' -f1 | sort | uniq -c | sort -rn | head
# 只看某个 ID
grep ' 7E8#' can.log | head
```

```python
#!/usr/bin/env python3
# can_parse.py —— 解析 Candump/ASC 日志，按 ID 还原时序
import re, sys, collections

LINE = re.compile(
    r'(?:\((?P<t>[\d.]+)\)|(?P<t2>[\d.]+))\s+(?P<ch>\S+)\s+'
    r'(?P<id>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)')
rows = []
for line in open(sys.argv[1], errors='ignore'):
    m = LINE.search(line)
    if not m:
        continue
    rows.append((float(m.group('t') or m.group('t2')),
                 int(m.group('id'), 16), m.group('data').upper()))

print('frames:', len(rows))
cnt = collections.Counter(r[1] for r in rows)
print('top IDs:', [(hex(k), v) for k, v in cnt.most_common(10)])

# 找出"只出现极少次"的 ID（可疑注入）
rare = [hex(k) for k, v in cnt.items() if v <= 3]
print('rare IDs:', rare[:20])

# 按 ID 打印数据变化
for tid in [int(x, 16) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(cnt)[:3]:
    vals = [(t, d) for t, i, d in rows if i == tid]
    print(f'== {hex(tid)} n={len(vals)}')
    for t, d in vals[:12]:
        print(f'  {t:.3f} {d}')

# 把某 ID 的最后一字节拼成字符串（常见隐写手法）
tail = ''.join(d[-2:] for t, i, d in rows if i in
               ([int(x, 16) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else cnt))
raw = bytes.fromhex(tail)
print('reassembled tail bytes:', raw[:80])
print('as text:', ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[:200]))
```

### 虚拟 CAN 环境复现

```bash
sudo apt install -y can-utils
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
# 发一帧
cansend vcan0 7DF#0201050000000000
# 收
candump vcan0
# 重放日志到虚拟总线
canplayer -I can.log vcan0=can0 &
candump -l vcan0
# 泛洪/模糊测试（仅在自建虚拟总线/授权环境）
cangen vcan0 -g 0 -I 7E0 -L 8 -D 00 -n 1000
```

```python
#!/usr/bin/env python3
# can_replay.py —— 用 python-can 重放并收集响应
import can, time
bus = can.interface.Bus(interface='socketcan', channel='vcan0', bitrate=500000)
for msg_sid, data in [(0x7DF, [0x02, 0x01, 0x0C, 0, 0, 0, 0, 0]),
                      (0x7DF, [0x02, 0x01, 0x0D, 0, 0, 0, 0, 0])]:
    bus.send(can.Message(arbitration_id=msg_sid, data=bytes(data[:8]),
                         is_extended_id=False))
    for resp in bus:
        if 0x7E8 <= resp.arbitration_id <= 0x7EF:
            print(hex(resp.arbitration_id), resp.data.hex())
            break
        time.sleep(0.001)
```

### .blf / .asc 转换

```bash
# Wireshark 支持 CAN 导入：wiretap 的 BLF 与 ASC 读入后
tshark -r capture.blf -T fields -e can.id -e can.data | head
tshark -r capture.asc -Y 'can.id==0x7e8' -T fields -e can.data
# canmatrix 转换 DBC
pip install canmatrix
canconvert capture.dbc capture.dbc.json
```

### UDS / 诊断帧识别

```bash
# 请求 0x7DF，数据首字节为服务号
# 0x10 会话控制 / 0x22 读数据 / 0x27 安全访问 / 0x31 例程 / 0x2E 写数据
grep -E ' 7DF#(02|03)1[0-9]' can.log | head
grep ' 7DF#022[0-9A-F]' can.log | head
# 安全访问（0x27）的 seed/key 交换
grep -E ' 7(DF|E8)#' can.log | grep -E '#0[23]27' | head
```

## 五、常见坑 / 变体

- **ID 大小写**：日志里 `7e8` 与 `7E8` 混用，脚本统一 `int(x,16)`。
- **CAN-FD 长度**：DLC 可能是 12~64 字节，按字节切片要读 DLC 而不是固定 8。
- **扩展帧（29 位 ID）**：用 `#` 前的 8 位十六进制表示，且 `can.log` 里可能带标志位。
- **时间戳单位**：`candump -l` 是秒，`.asc` 可能是毫秒，比较前统一。
- **网关过滤**：某些帧是网关伪造的，两段日志对比更可靠。
- **重放目标**：只在自建 vcan 或演示硬件（如 ICSim）上做，真实车辆未经授权不可操作。
- **CRC 不校验**：CAN 硬件自动补 CRC，注入帧只要 ID/数据即可。

## 六、参考来源

- [can-utils 官方仓库（candump/cansend/cangen）](https://github.com/linux-can/can-utils)
- [python-can 文档（socketcan 接口）](https://github.com/hardbyte/python-can)
- [CiA - CAN 规范与科普资源](https://www.can-cia.org/)
- [ICSim - 车载仪表盘模拟器（练习注入）](https://github.com/ICSim/)
- [CTF Wiki - ICS CTF 概述](https://ctf-wiki.org/ics/ctfs/)
- [CTF Wiki - ICS 利用](https://ctf-wiki.org/ics/exploit/)

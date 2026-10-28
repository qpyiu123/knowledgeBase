---
title: RFID / NFC / 蓝牙 BLE 抓包与攻击
category: hardware
tags: [rfid, nfc, mifare, ble, 蓝牙, hackrf]
signals: [题目给出门禁卡数据, 需要解密 mifare classic, 需要嗅探 ble 通信, 附件是 nfc dump 文件, 题面提到 125khz 或 13.56mhz]
difficulty: hard
source: "Proxmark3 文档 / Ubertooth 文档 / HackRF 官方文档 / NFC 论坛规范"
tools: [proxmark3, mfoc, mfcuk, ubertooth, hackrf, bettercap, sniffer, nfc-tools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件 `card.mfd`、`dump.bin`、`.nfc`、`.eml`（Proxmark 导出的卡片转储）。
- 题目说「还原门禁卡」「破解这张卡里的扇区」。
- 需要从 BLE 流量里找传感器数据包或配对密钥。
- 题面出现 `MIFARE`、`Ultralight`、`NTAG213`、`HID Prox`。

## 二、原理

**RFID/NFC 常用频率与协议**：

| 频段 | 协议 | 常见场景 | 能否轻易破解 |
| --- | --- | --- | --- |
| 125 kHz | EM4100 / HID Prox（低频 ID 卡） | 老门禁、考勤 | **无加密**，读出来即可复制 |
| 13.56 MHz | **MIFARE Classic**（ISO 14443A） | 门禁、公交卡 | Crypto-1 已被破，可离线解出密钥 |
| 13.56 MHz | MIFARE DESFire / Ultralight-C | 现代门禁、交通 | AES/3DES，需要真实漏洞或密钥泄露 |
| 13.56 MHz | NTAG / Type 2 | 贴纸/防伪 | 可读可写，可能被克隆 |
| 2.4 GHz | **BLE** | 手环、门锁、传感器 | 未加密的 GATT 可被读；配对口令强度是关键 |

**MIFARE Classic**：1K 卡有 16 个扇区，每扇区 4 块 × 16 字节，最后一块是 **sector trailer**（两个 6 字节密钥 A/B + 访问位）。Crypto-1 流密码存在**嵌套认证**漏洞，用 `mfoc`/`mfcuk` 可恢复全部密钥；一旦有任一扇区密钥就能用 `darkside` 攻击。

**BLE**：广播包（ADV_IND）里含设备名与厂商数据；连接后是 GATT 读写。若未启用配对加密，用 nRF52/Xiao 等嗅探器 + `bettercap` 就能读写特征值。

## 三、操作步骤

1. **判断卡类型**：`proxmark3` 的 `hf search` / `lf search`（13.56 MHz vs 125 kHz）。
2. **读 dump**：`hf mf dump` 或 `lf em 410x read`。
3. **解密钥**：`hf mf autopwn`（Proxmark3 新版一条命令）；或 `mfoc -O card.mfd`。
4. **分析内容**：dump 里的扇区如果全 `00` 说明是空卡；有用的通常是明文 ASCII 或 hex。
5. **BLE**：`ubertooth-btle -f` 抓包 → `.pcap` 用 Wireshark 看 ATT 特征值。
6. **提取**：把 GATT 值或 dump 里的 hex 按时间/扇区拼成字符串。

## 四、命令/脚本

### Proxmark3 常用命令

```bash
# 交互式客户端
proxmark3 /dev/ttyACM0
# 卡片搜索（自动判断高频/低频）
[usb] pm3 --> hf search
[usb] pm3 --> lf search
# MIFARE Classic：自动破解全部密钥并 dump
[usb] pm3 --> hf mf autopwn
[usb] pm3 --> hf mf dump
# 读取单个块（key A = FFFFFFFFFFFF）
[usb] pm3 --> hf mf rdbl --blk 4 -a -k FFFFFFFFFFFF
# 写回 / 克隆
[usb] pm3 --> hf mf cload -f dump.bin
# 低频 125kHz ID 卡
[usb] pm3 --> lf em 410x_read
[usb] pm3 --> lf em 410x_sim        # 模拟
# NTAG / Ultralight
[usb] pm3 --> hf mf ndefread
```

### mfoc / mfcuk（无 Proxmark 时用 ACR122U）

```bash
sudo apt install -y mfoc mfcuk libnfc-bin
mfoc -O card.mfd                         # 已知一个密钥时快速恢复其余
mfcuk -C -R 0:A0A1A2A3A4A5 -T 1         # 全密钥未知时的 darkside
```

### dump 文件解析

```python
#!/usr/bin/env python3
# mifare_dump.py —— 把 MIFARE Classic 1K dump 按扇区/块打印，找可读文本
import sys
data = open(sys.argv[1], 'rb').read()
print('size:', len(data), 'expected 1024 for MF1K')
for sec in range(len(data) // 64):
    print(f'== sector {sec:02d}  keyA={data[sec*64+48:sec*64+54].hex()} '
          f'acc={data[sec*64+54:sec*64+57].hex()} keyB={data[sec*64+58:sec*64+64].hex()}')
    for blk in range(3):
        off = sec * 64 + blk * 16
        row = data[off:off+16]
        txt = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row)
        print(f'  blk{sec*4+blk:2d} {row.hex(" ")}  |{txt}|')
# 全卡 ASCII 拼接
txt = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
print('--- all ascii ---')
print(txt[:800])
```

```bash
python mifare_dump.py card.mfd
strings -n 4 card.mfd | grep -iE 'flag|key|pass'
```

### BLE 嗅探

```bash
# Ubertooth One（或 nRF52840 + sniffer 固件）
ubertooth-btle -f -A 37 -t targets.txt -c capture.pcap     # 跟指定地址
ubertooth-btle -f -c capture.pcap                          # 全通道跟随
tshark -r capture.pcap -Y 'btatt' -T fields -e btatt.handle -e btatt.value | head -30

# 用 bettercap 做 BLE 枚举与读写（在支持 BLE 的适配器上）
sudo bettercap -iface hci0
> ble.recon on
> ble.show
> ble.enum AA:BB:CC:DD:EE:FF
```

```python
#!/usr/bin/env python3
# ble_sniff.py —— 枚举 BLE 设备并读取所有可读特征值
import asyncio
from bleak import BleakScanner, BleakClient

async def main():
    devs = await BleakScanner.discover(timeout=8)
    for d in devs:
        print(f'{d.address} {d.name} rssi={d.rssi} mfr={d.metadata.get("manufacturer_data")}')
    if not devs:
        return
    target = devs[0].address
    async with BleakClient(target) as c:
        for s in c.services:
            for ch in s.characteristics:
                if 'read' in ch.properties:
                    try:
                        v = await c.read_gatt_char(ch)
                        print(ch.uuid, v, v.hex())
                    except Exception as e:
                        print(ch.uuid, 'err', e)

asyncio.run(main())
```

### HackRF + GNU Radio（通用射频）

```bash
# 扫描 2.4GHz，定位 BLE 广播信道并录制 IQ
hackrf_info
hackrf_transfer -r ble.iq -f 2402000000 -s 8000000 -a 1 -g 20 -n 80000000
# 用 gr-ble / gr-bluetooth 的 flowgraph 解析，或交给 Universal Radio Hacker 看调制
```

## 五、常见坑 / 变体

- **dump 尺寸**：MF1K 是 1024 字节（16×64），MF4K 是 4096；尺寸不对说明导出不完整。
- **密钥全未知**：`mfoc` 需要一个已知密钥才能启动，全空卡要先 `mfcuk` 打 darkside，耗时长。
- **访问位（Access Bits）**：`ff0780` 是默认（密钥 A 可读写，key B 只读）；`787788` 之类非默认值可能把某块设为只读。
- **加密扇区**：内容不是明文时可能是写卡程序自己加密的，需要结合固件/APP 逆向。
- **BLE 地址随机化**：设备每次换 MAC，要按厂商数据/名称过滤。
- **BLE 配对加密**：Just Works 配对可中间人；LE Secure Connections 需更强攻击。
- **合规**：射频发射类操作会干扰他人设备，只在隔离环境/授权资产上做。

## 六、参考来源

- [Proxmark3 官方文档（hf mf autopwn 等命令）](https://github.com/RfidResearchGroup/proxmark3)
- [proxmark/proxmark3 主仓库与 wiki](https://github.com/proxmark/proxmark3)
- [Ubertooth 文档（BTLE 嗅探）](https://ubertooth.readthedocs.io/)
- [Great Scott Gadgets - Ubertooth 产品页](https://greatscottgadgets.com/hackrf/)
- [HackRF 官方文档](https://github.com/greatscottgadgets/hackrf)
- [GNU Radio 官方站](https://www.gnuradio.org/)
- [CTF Wiki - ICS 发现（无线/射频枚举思路）](https://ctf-wiki.org/ics/discover/)

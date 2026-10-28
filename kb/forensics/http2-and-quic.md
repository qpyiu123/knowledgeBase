---
title: 高级协议分析（HTTP/2 与 QUIC 解密）
category: forensics
tags: [http2, quic, h2c, sslkeylogfile, tls1.3, 解密]
signals: [流量里有 h2 或 h3 协议, wireshark 显示 encrypted alert, 需要解密 TLS1.3, 给了 sslkeylog 文件, 流量在 UDP 443 端口, 请求头是二进制]
difficulty: hard
source: "Wireshark QUIC/TLS 文档 / RFC 9113 HTTP/2 / RFC 9000 QUIC / NSS Key Log Format"
tools: [wireshark, tshark, nghttp2, qlog, curl, openssl, nss-keylog]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 流量里出现 `h2`、`h3`、`HTTP2`，Wireshark 大量显示 `Encrypted Alert`。
- 题目附带 `sslkeylog.txt` 或 `keys.log`（NSS Key Log Format）。
- 有大量 **UDP 443** 流量且包长不规则 → 疑似 QUIC。
- HTTP/2 的头部全是二进制/压缩块（HPACK），肉眼无法读。
- 题面要求"还原某次请求的 UA / cookie"。

## 二、原理

**HTTP/2**：二进制分帧协议。所有数据被切成 `HEADERS/DATA/SETTINGS/WINDOW_UPDATE` 帧，头部用 **HPACK**（静态表 + 动态表 + Huffman）压缩，因此不能直接用 `strings`。分两条路线：

- **明文 h2c**（`Upgrade: h2c` 或直接 prior knowledge）：Wireshark 会自动解析，注意端口不是 80 时要 `Decode As → HTTP2`。
- **TLS 上的 h2**：必须先解密。

**TLS 解密**：主流方法是 `SSLKEYLOGFILE`——客户端（Chrome/Firefox/curl with `--keylogfile`）会把每个连接的 `CLIENT_RANDOM` 与 `CLIENT_TRAFFIC_SECRET_0` 等写进 keylog 文件，Wireshark 用 `(Protocols → TLS → Master-Secret log filename)` 指定后即可解密 **TLS1.2 与 TLS1.3**。

**QUIC**：跑在 UDP 上，握手用 TLS1.3（Initial 包的密钥由连接 ID 派生，因此 Initial 可以解），后续 1-RTT 包需要 TLS 导出的密钥。Wireshark 4.x 支持：
- 用 keylog 解密 QUIC h3；
- 对 Initial 包用 `QUIC → TLS key log`；
- 新支持 **qlog** 辅助分析。

## 三、操作步骤

1. **识别协议版本**：`tshark -r x.pcap -Y 'tls.handshake.extensions_alpn_str' -T fields -e tls.handshake.extensions_alpn_str`，看到 `h2`/`h3` 即确认。
2. **有 keylog 就配置**：Wireshark 首选项里设置 `TLS keylog filename`；tshark 用 `-o tls.keylog_file:keys.log`。
3. **没有 keylog**：找 `CLIENT_RANDOM` 碰撞（已知明文 difficult），或从流量里找服务器私钥（RSA 密钥交换已淘汰，TLS1.3 不可行）。
4. **h2 明文**：对非 443 端口 `Decode As → HTTP2`，过滤器 `http2.headers`。
5. **QUIC**：过滤器 `quic`，`Decode As → QUIC`；配合 keylog 看 `http3`。
6. **提取**：h2 的 DATA 帧拼成 body；h3 用 `http3.data`。

## 四、命令/脚本

### 判断协议与端点

```bash
tshark -r target.pcap -Y 'tcp.port==443' -T fields \
  -e tls.handshake.extensions_alpn_str -e ip.dst | sort | uniq -c | head
tshark -r target.pcap -Y 'tls.handshake.type==1' -T fields \
  -e ip.src -e tls.handshake.extensions_server_name | head -20      # SNI
tshark -r target.pcap -Y 'udp.port==443' -c 20 -V | head -80          # QUIC 概览
```

### 用 keylog 解密（Wireshark / tshark）

```bash
# 关键：先确认 keylog 里确实是目标连接的 secret
grep -E 'CLIENT_TRAFFIC_SECRET_0|CLIENT_RANDOM' keys.log | head -3
tshark -r target.pcap -o tls.keylog_file:keys.log -Y 'http2.headers' -V | head -80
tshark -r target.pcap -o tls.keylog_file:keys.log -Y 'http.request' -T fields \
  -e http.host -e http.request.uri
```

> Wireshark GUI 路径：`Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename`，填 keylog 后重启捕获即生效（对已打开的包需要 File → Reopen）。

### 生成 keylog（自己复现抓包时）

```bash
# curl（TLS1.3）
SSLKEYLOGFILE=$PWD/keys.log curl -s https://TARGET/ -o /dev/null
# python requests（浏览器早已支持：Chrome 需要 --ssl-key-log-file 启动参数）
SSLKEYLOGFILE=$PWD/keys.log python3 -c "import requests;requests.get('https://TARGET/')"
# 用 tcpdump 同步抓包
sudo tcpdump -i any -w cap.pcap 'host TARGET_IP'
```

### HTTP/2 明文提取

```bash
# 对非 443 上的 h2c
tshark -r target.pcap -o 'uat:http2_ports:"80,8080,8443"' -Y 'http2' -V | head -100
tshark -r target.pcap -Y 'http2.headers' -T fields \
  -e http2.headers.method -e http2.headers.path -e tcp.stream
# 提取 DATA 帧内容（body）
tshark -r target.pcap -Y 'http2.type==0' -T fields -e http2.data.data
```

### 用 nghttp2 客户端复现请求

```bash
apt install -y nghttp2-client
nghttp -nv https://TARGET/upload              # 打印帧级细节
nghttp --no-tls -v http://TARGET:8080/        # h2c prior knowledge 模式
```

### QUIC / HTTP3

```bash
tshark -r quic.pcap -Y 'quic' -V | head -120
# 有 keylog 时
tshark -r quic.pcap -o tls.keylog_file:keys.log -Y 'http3' -V | head -80
# qlog 输出（Wireshark 4.2+）
tshark -r quic.pcap -q -z quic,json 2>/dev/null | head -40
# 用 curl 抓 h3 并附 keylog
SSLKEYLOGFILE=$PWD/keys.log curl --http3 -v https://TARGET/ 2>&1 | head
```

### HPACK 解码（不想开 Wireshark 时）

```bash
pip install hpack h2
python - <<'PY'
import hpack
d = hpack.Decoder()
block = bytes.fromhex('828684418cf1e3c2e5f23a6ba0ab90f4ff')
print(d.decode(block, raw=True))
PY
```

```python
#!/usr/bin/env python3
# h2_from_pcap.py —— 从 pcap 里抓 HEADERS 帧十六进制串并解码
import subprocess, hpack
out = subprocess.run(
    ['tshark', '-r', 'target.pcap', '-Y', 'http2.type==1',
     '-T', 'fields', '-e', 'http2.headers.padding', '-e', 'frame.number'],
    capture_output=True, text=True).stdout
print(out[:500])
d = hpack.Decoder()
# 若拿到原始 HPACK 字节串（hex），可直接：d.decode(bytes.fromhex(hx))
```

## 五、常见坑 / 变体

- **keylog 不匹配**：keylog 里有 secret 但解不开，多半是抓包与 keylog 不是同一次连接（时间/进程不对）。
- **TLS 1.3 的前向保密**：拿到服务器私钥**也无法**解密 1-RTT，必须有 keylog（TLS 1.2 RSA 套件除外）。
- **端口伪装**：h2 跑在 8443、h3 跑在 UDP 8443，要 `Decode As`。
- **早期数据（0-RTT）**：客户端第一包就可能带数据，靠 keylog 里的 `CLIENT_EARLY_TRAFFIC_SECRET`。
- **QUIC 无 keylog**：只能看 Initial（可从 SNI/证书大小推断目标），1-RTT 内容不可见。
- **大流量 + h2**：`tshark -2` 需要两遍，内存压力大，先按 stream 过滤。
- **证书检测**：即使加密，也可以从 `Certificate` 明文里拿到 SNI 和证书信息做溯源（属 OSINT 交叉）。

## 六、参考来源

- [CTF Wiki - HTTPS 流量分析](https://ctf-wiki.org/misc/traffic/protocols/https/)
- [RFC 9113 - HTTP/2 规范](https://datatracker.ietf.org/doc/html/rfc9113)
- [RFC 9000 - QUIC 传输协议](https://datatracker.ietf.org/doc/html/rfc9000)
- [Wireshark TLS 解密（keylog）官方说明](https://wiki.wireshark.org/TLS)
- [keylogfile 格式草案（IETF）](https://www.ietf.org/archive/id/draft-thomson-tls-keylogfile-00.html)
- [nghttp2 客户端工具文档](https://nghttp2.org/documentation/)

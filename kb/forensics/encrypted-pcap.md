---
title: 加密流量解密（SSLKEYLOGFILE / HTTPS 分析）
category: forensics
tags: [https, tls, sslkeylogfile, 解密, nss, pcap]
signals: [流量全是 tls 加密, 题目说分析 https 流量, wireshark 显示 cannot decrypt, 给了 keys.log, 需要还原 https 上传内容]
difficulty: medium
source: "Wireshark TLS 文档 / IETF keylogfile 草案 / Mozilla NSS 文档"
tools: [wireshark, tshark, openssl, curl, mitmproxy, nss-keylog, editcap]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- pcap 里 90% 是 `TLSv1.2 Application Data`，看不到明文。
- 题目额外给了一个 `sslkeylog.txt` / `keys.log` / `key.log` 文本文件。
- 题目给了服务器私钥 `server.key`（用于 RSA 密钥交换的老流量）。
- 题干说「分析这次 HTTPS 上传」。

## 二、原理

TLS 会话密钥的派生路径：
- **TLS 1.2（RSA 密钥交换，已淘汰）**：客户端用服务器公钥加密 `pre_master_secret`，有私钥就能解。
- **TLS 1.2（ECDHE）与 TLS 1.3**：**前向保密**，密钥只在内存里，抓包+私钥都无解，**必须拿到 keylog**。
- **keylog 格式（NSS Key Log）**：每行 `<标签> <CLIENT_RANDOM> <密钥>`，例如：
  ```
  CLIENT_RANDOM 11ee... 9d0c...
  CLIENT_HANDSHAKE_TRAFFIC_SECRET 11ee... a0b1...
  CLIENT_TRAFFIC_SECRET_0 11ee... f3c2...
  SERVER_TRAFFIC_SECRET_0 11ee... 77aa...
  ```
  其中 `CLIENT_RANDOM` 就是 ClientHello 里的 32 字节随机数，Wireshark 用它把 keylog 行与 pcap 里的连接对上。

Wireshark 支持 TLS1.3 的全部标签，也支持 QUIC（h3）的 keylog 解密。

## 三、操作步骤

1. **确认从哪里取 keylog**：
   - 题目直接给的 → 直接用。
   - 需要自己复现 → 用 `SSLKEYLOGFILE` 环境变量 + `curl`/`python-requests`/`mitmproxy`。
2. **加载 keylog**：
   - GUI：`Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename`。
   - CLI：`tshark -o tls.keylog_file:keys.log`。
3. **验证解密生效**：过滤器 `http2 || http`，能看到明文的 `:path` 或 `GET` 行即成功。
4. **提取数据**：`--export-objects http`，或 `follow,tcp`。
5. **私钥路线**（老流量）：`tls.keys_list` 里指定 `IP,port,protocol,keyfile`。

## 四、命令/脚本

### 用 keylog 解密

```bash
# 1) 看 keylog 内容与格式
head -3 keys.log
grep -c 'CLIENT_RANDOM' keys.log
# 2) tshark 解密
tshark -r cap.pcap -o tls.keylog_file:keys.log -Y 'http.request' -T fields \
  -e http.host -e http.request.uri
tshark -r cap.pcap -o tls.keylog_file:keys.log -Y 'http2.headers' -V | head -60
# 3) 解密后导出 HTTP 对象
tshark -r cap.pcap -o tls.keylog_file:keys.log --export-objects http,out/
ls -la out/
# 4) 确认哪些流被成功解密
tshark -r cap.pcap -o tls.keylog_file:keys.log -Y 'http || http2' -T fields -e tcp.stream | sort -u
```

> GUI 里如果看不到效果，需要 `File → Reopen`（keylog 不会对已经打开并处理的包追溯生效）。

### 私钥路线（TLS1.2 RSA 套件）

```bash
tshark -r cap.pcap -o "tls.keys_list:192.0.2.10,443,http,server.key" \
       -Y 'http.request' -T fields -e http.host -e http.request.uri
# 私钥需是 PEM 未加密格式：
openssl rsa -in server.key -out server_plain.key
```

### 生成 keylog（本地复现）

```bash
# curl
SSLKEYLOGFILE=$PWD/keys.log curl -sS https://TARGET/api/login -d 'u=a&p=b'
# python requests
SSLKEYLOGFILE=$PWD/keys.log python3 -c "
import requests; print(requests.post('https://TARGET/', data={'a':1}).status_code)"
# mitmproxy（代理抓包 + 自动写 keylog）
SSLKEYLOGFILE=$PWD/keys.log mitmdump -w cap.mitm &
# Chrome（需重启，且只对新连接生效）
chrome.exe --ssl-key-log-file=C:\CTF\keys.log
# 同步抓包
sudo tcpdump -i any -w cap.pcap 'host TARGET and port 443'
```

### 用 RSA 私钥 + 已知明文推导（无 keylog 时）

```bash
# TLS1.2 RSA 套件且只有密文时：利用应用层已知明文 + Bleichenbacher 式攻击
# 实战可用 RsaCtfTool 的 tls 模式或 openssl 手工尝试；TLS1.3 无解。
openssl s_client -connect TARGET:443 -tls1_2 -cipher AES128-SHA -keylogfile=keys.log
```

### 其他常用过滤器

```bash
tshark -r cap.pcap -Y 'tls.handshake.type==1' -T fields \
  -e ip.src -e tls.handshake.extensions_server_name -e tls.handshake.extensions_alpn_str | head
tshark -r cap.pcap -Y 'tls.record.content_type==22' -c 10 -V | head -60   # 握手记录
tshark -r cap.pcap -Y 'x509sat.uTF8String' -T fields -e x509sat.uTF8String | head
```

### pcapng 转换与合并

```bash
editcap -F pcap in.pcapng out.pcap            # 转老格式（部分工具只认 pcap）
mergecap -w merged.pcap cap1.pcap cap2.pcap   # 合并
editcap -d in.pcap out.pcap                   # 去重（keylog 重放时有用）
```

## 五、常见坑 / 变体

- **keylog 与 pcap 不匹配**：`CLIENT_RANDOM` 对不上，常见原因是抓包和客户端不是同一次连接，或中间经过代理重生成了 TLS。
- **TLS 1.3 的 0-RTT**：需要 `CLIENT_EARLY_TRAFFIC_SECRET`，不是所有客户端都写。
- **HPACK 解不开**：即使密钥对，h2 头是 HPACK，Wireshark 4.x 会自动解；tshark 要 `-o http2.capture_headers:TRUE`（视版本）。
- **私钥无效**：必须是**服务器**私钥，客户端私钥无用。
- **QUIC**：UDP 443 的 h3 也要用同一套 keylog（`tls.keylog_file` 同样生效）。
- **重放/重传**：`editcap -d` 去重后再喂给 Wireshark，避免重复解密。
- **非标准端口**：直接用 `Decode As` 指定 TLS 或 HTTP。

## 六、参考来源

- [CTF Wiki - HTTPS 流量分析](https://ctf-wiki.org/misc/traffic/protocols/https/)
- [Wireshark TLS 解密 wiki（keylog 与私钥）](https://wiki.wireshark.org/TLS)
- [keylogfile 格式草案（IETF draft-thomson-tls-keylogfile）](https://www.ietf.org/archive/id/draft-thomson-tls-keylogfile-00.html)
- [tshark 手册页（tls.keylog_file 选项）](https://www.wireshark.org/docs/man-pages/tshark.html)
- [mitmproxy 官方文档](https://docs.mitmproxy.org/stable/)
- [OpenSSL s_client 文档](https://docs.openssl.org/master/man1/openssl-s_client/)

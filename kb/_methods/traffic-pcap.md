---
title: 方法卡 · 流量包协议还原（HTTP/DNS/自定义）
category: forensics
tags: [pcap, wireshark, tshark, dns, http, 流量分析]
signals:
  - "附件是 .pcap/.pcapng，题面问访问了哪个地址、传了什么"
  - "文件头为 D4 C3 B2 A1 或 0A 0D 0D 0A"
  - "正常流量的 follow stream 末尾有异常字符串"
  - "DNS 查询名长得很像 base64 或十六进制"
  - "tcp contains \"flag\" 能筛出一两条包"
  - "导出对象里有个 1MB 的 application/octet-stream"
difficulty: medium
source: kb/forensics/steganalysis-workflow.md, kb/_imported_cats/misc/File signatures__helloctf-21ca8b99eee52c.md
updated: 2026-11-03
tools: [python3, tshark, wireshark, tcpdump, editcap]
---
## 适用场景

题目给一个抓包文件。绝大多数赛题的答案落在三处：**应用层载荷**（HTTP 请求体、
自定义协议的 body）、**DNS 查询名**（被当作隐蔽信道）、**TCP 流重组后的文件**
（导出的图片/压缩包）。先按协议分层剥开，再回到内容层找可疑串，比直接
`strings cap.pcap` 命中率高得多。

## 前置条件

- 知道文件是不是经典 pcap：前 4 字节 `D4 C3 B2 A1`（小端微秒）、`A1 B2 C3 D4`
  （大端微秒，或纳秒变体）、`0A 0D 0D 0A`（pcapng）。
- pcapng 需要 `editcap -F pcap in.pcapng out.pcap` 转成经典 pcap 再手工解析。
- 有 tshark 时优先 `tshark -r cap.pcap -Y "http" -T fields -e http.request.uri`。
- 无工具时用本卡脚本（纯标准库），只解 Ethernet/SLL/RAW 三种链路层。

## 步骤

1. **认容器与链路层**：读全局头拿 linktype（1=Ethernet、113=Linux cooked、101=RAW），
   链路层猜错会得到一堆乱码，这个字段是第一步要核对的。
2. **建流表**：按五元组分组，丢掉重传干扰，先看每条流的字节量排序，
   异常的"小数目流"往往就是隐蔽信道。
3. **应用层特判**：TCP 载荷以 `GET /`/`POST /` 开头就是 HTTP，直接取请求行与 body；
   UDP 目的端口 53 就是 DNS，解析 12 字节头之后的长度前缀标签拿到查询名。
4. **可疑串扫描**：对每条流的载荷拼起来扫 `flag{`、`PK\x03\x04`、`\x89PNG`、`%PDF-`、
   gzip 头；命中文件头的流手动导出再按文件格式分析。
5. **重组导出**：`tshark --export-objects http,out/` 或在 wireshark 里
   follow TCP stream 存 raw，导出的文件交给 `file_carving` / `steg_png_bmp`。
6. **DNS 隧道**：查询名按 base32/base64 解码后拼接，注意去掉域名后缀再解。

## 立即可用脚本

`kb/_methods/scripts/traffic_pcap.py`（纯标准库，离线只读）

```
python traffic_pcap.py --file cap.pcap
python traffic_pcap.py --file cap.pcap --stream 1 --hex
python traffic_pcap.py --file cap.pcap --dns
python traffic_pcap.py --selftest
```

参数：

- `--file`：pcap 路径（必填，除非 `--selftest`）。
- `--stream N`：展开第 N 条流（按首次出现顺序），打印每包时间戳与载荷前缀。
- `--hex`：配合 `--stream`，额外打印载荷十六进制。
- `--dns`：只输出 DNS 查询名。
- `--selftest`：内置断言（DNS 解析、非法魔数拒绝、截断记录、固定输入可复现、可疑串）。

失败行为：pcapng、文件过短、魔数不认识都在 stderr 打印 `失败：…` 返回 2；
自检通过打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ python traffic_pcap.py --file cap.pcap
记录 2 条，链路类型 1，流 2 条
  [0] 10.0.0.2:40000->8.8.8.8:53               包=1 字节=34
  [1] 10.0.0.2:40001->8.8.8.8:80               包=1 字节=35
  HTTP #1    GET /flag?a=1 HTTP/1.1
$ python traffic_pcap.py --file cap.pcap --dns
  #0    flag.example.com
$ tshark -r cap.pcap -Y "dns" -T fields -e dns.qry.name | sort -u
flag.example.com
```

## 失效场景

- IP 分片、TCP 乱序/重传：本脚本只按包顺序拼接，不重组 TCP 段，长文件导出会不完整。
- 非标准链路层（Wi-Fi 802.11、PPPoE、VLAN 双层 tag）：直接报"非 IP"，需要用 tshark 转换。
- TLS/SSH 等加密流：载荷全是密文，只能看握手 SNI 与长度特征。
- pcapng 带多个接口/自定义块：必须先 `editcap` 转换，否则解析会静默丢包。

## 相关文档

- `kb/forensics/steganalysis-workflow.md`：容器层与载荷层的处理顺序。
- `kb/forensics/file-carving.md`：从流里导出的半截文件如何继续雕刻。
- `kb/_methods/steg-png-bmp.md`：导出图片后继续做隐写分析。
- `kb/_methods/enc_chain_decode.md`：DNS 查询名/base64 body 逐层解码。

## 目录与收录说明

- 卡片：`kb/_methods/traffic-pcap.md`；脚本：`kb/_methods/scripts/traffic_pcap.py`。
- 对应 backlog 项 `traffic-pcap`（category=forensics），源文档
  `kb/forensics/steganalysis-workflow.md` 与
  `kb/_imported_cats/misc/File signatures__helloctf-21ca8b99eee52c.md`。

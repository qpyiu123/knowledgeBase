#!/usr/bin/env python3
"""经典 pcap 流量包协议还原（纯标准库，离线只读）。

对齐 kb/forensics/steganalysis-workflow.md 的"容器层/协议层"与
kb/_imported_cats/misc/File signatures 的 pcap 魔数：
  D4 C3 B2 A1  小端微秒
  A1 B2 C3 D4  大端微秒
  4D 3C B2 A1  小端纳秒
  A1 B2 3C 4D  大端纳秒
  0A 0D 0D 0A  pcapng（本脚本只报类型，不解析）
链路层回溯 Ethernet(1) / Linux SLL(113) / RAW IP(101)，
传输层解 TCP(6)/UDP(17)，应用层解 HTTP 请求行与 DNS 查询名，
并对每条流的载荷做可疑字符串扫描（flag{、base64、PK 头等）。

用法：
  python traffic_pcap.py --file cap.pcap
  python traffic_pcap.py --file cap.pcap --stream 1 --hex
  python traffic_pcap.py --file cap.pcap --dns
  python traffic_pcap.py --selftest
"""
from __future__ import annotations

import argparse
import struct
import sys

MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("<", "us"),
    b"\xa1\xb2\xc3\xd4": (">", "us"),
    b"\x4d\x3c\xb2\xa1": ("<", "ns"),
    b"\xa1\xb2\x3c\x4d": (">", "ns"),
    b"\x0a\x0d\x0d\x0a": (None, "pcapng"),
}


def read_pcap(data: bytes):
    """返回 (records, linktype)；records = [(idx, ts, payload)]。"""
    if len(data) < 24:
        raise ValueError("文件太短（经典 pcap 全局头 24 字节）")
    m = data[:4]
    if m not in MAGIC:
        raise ValueError("不是经典 pcap（魔数应为 D4C3B2A1/A1B2C3D4 等）")
    endian, res = MAGIC[m]
    if endian is None:
        raise ValueError("这是 pcapng，本脚本只解析经典 pcap（先 editcap 转换）")
    linktype = struct.unpack(endian + "I", data[20:24])[0] & 0x0FFFFFFF
    recs, p, idx = [], 24, 0
    while p + 16 <= len(data):
        ts_s, ts_f, incl, orig = struct.unpack(endian + "IIII", data[p:p + 16])
        p += 16
        if p + incl > len(data):
            break
        ts = ts_s + (ts_f / 1e9 if res == "ns" else ts_f / 1e6)
        recs.append((idx, ts, data[p:p + incl]))
        idx += 1
        p += incl
    return recs, linktype


def l3_payload(frame: bytes, linktype: int):
    """剥链路层，返回 (ip_proto, src, dst, l4payload) ；非 IP 返回 None。"""
    if linktype == 1:  # Ethernet
        if len(frame) < 14:
            return None
        ihl = (frame[14] & 0x0F) * 4 if frame[14] >> 4 == 4 else 20
        eth_type = struct.unpack(">H", frame[12:14])[0]
        if eth_type != 0x0800:
            return None
        ip = frame[14:]
        return _ip(ip)
    if linktype == 113:  # Linux cooked
        if len(frame) < 16 or struct.unpack(">H", frame[14:16])[0] != 0x0800:
            return None
        return _ip(frame[16:])
    if linktype == 101:  # RAW
        return _ip(frame)
    return None


def _ip(ip: bytes):
    if len(ip) < 20 or ip[0] >> 4 != 4:
        return None
    ihl = (ip[0] & 0x0F) * 4
    proto = ip[9]
    src = ".".join(str(b) for b in ip[12:16])
    dst = ".".join(str(b) for b in ip[16:20])
    return proto, src, dst, ip[ihl:]


def l4(pkt, proto: int, src: str, dst: str):
    """返回 (四元组键, 载荷)；UDP/TCP 头被剥掉。"""
    if proto == 6 and len(pkt) >= 20:
        doff = (pkt[12] >> 4) * 4
        sport, dport = struct.unpack(">HH", pkt[0:4])
        return ("%s:%d->%s:%d" % (src, sport, dst, dport)), pkt[doff:]
    if proto == 17 and len(pkt) >= 8:
        sport, dport = struct.unpack(">HH", pkt[0:4])
        return ("%s:%d->%s:%d" % (src, sport, dst, dport)), pkt[8:]
    return None


def dns_qname(payload: bytes) -> str:
    """解析 DNS 查询名（跳过 12 字节头，按长度前缀取标签）。"""
    if len(payload) < 13:
        raise ValueError("DNS 载荷太短")
    labels, p = [], 12
    while p < len(payload):
        n = payload[p]
        if n == 0:
            break
        if n > 63 or p + 1 + n > len(payload):
            raise ValueError("DNS 标签长度非法")
        labels.append(payload[p + 1:p + 1 + n].decode("latin1"))
        p += 1 + n
    return ".".join(labels)


def http_first_line(payload: bytes) -> str:
    line = payload.split(b"\r\n", 1)[0]
    if not line.endswith(b" HTTP/1.1") and not line.endswith(b" HTTP/1.0"):
        return ""
    return line.decode("latin1")


def scan_streams(recs, linktype: int) -> dict:
    streams, dns, http = {}, [], []
    for idx, ts, frame in recs:
        l3 = l3_payload(frame, linktype)
        if not l3:
            continue
        proto, src, dst, pkt = l3
        got = l4(pkt, proto, src, dst)
        if not got:
            continue
        key, payload = got
        streams.setdefault(key, []).append((idx, ts, payload))
        if proto == 17:
            src_port, dst_port = struct.unpack(">HH", pkt[0:4])
            if src_port == 53 or dst_port == 53:
                try:
                    dns.append((idx, dns_qname(payload)))
                except ValueError:
                    pass
        if payload[:8].split(b" ")[0] in (b"GET", b"POST", b"PUT", b"HEAD"):
            line = http_first_line(payload)
            if line:
                http.append((idx, line))
    return {"streams": streams, "dns": dns, "http": http}


def suspicious(blob: bytes):
    """可疑片段：flag 明文、文件头、长相像 base64 的长串。"""
    hits = []
    for pat in (b"flag{", b"PK\x03\x04", b"\x89PNG", b"%PDF-", b"\x1f\x8b\x08"):
        if pat in blob:
            hits.append(pat.decode("latin1"))
    if b"==" in blob or b"==" in blob[:200]:
        hits.append("base64?")
    return hits


def build_pcap(frames, linktype=1) -> bytes:
    out = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, linktype)
    for i, fr in enumerate(frames):
        out += struct.pack("<IIII", 1700000000 + i, i * 1000, len(fr), len(fr)) + fr
    return out


def _eth_ipv4_udp(payload: bytes, sport=40000, dport=53) -> bytes:
    udp = struct.pack(">HHHH", sport, dport, 8 + len(payload), 0) + payload
    ip = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17, 0,
                     bytes([10, 0, 0, 2]), bytes([8, 8, 8, 8])) + udp
    return bytes(12) + b"\x08\x00" + ip


def _dns_query(name: str) -> bytes:
    q = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    for part in name.split("."):
        q += bytes([len(part)]) + part.encode()
    return q + b"\x00\x00\x01\x00\x01"


def selftest() -> int:
    fails = []
    # 1) 正常路径：构造一个 UDP/DNS 包，能解析出链路层与查询名
    q = _dns_query("flag.example.com")
    cap = build_pcap([_eth_ipv4_udp(q)])
    recs, lt = read_pcap(cap)
    if lt != 1 or len(recs) != 1:
        fails.append("case1: 全局头/记录解析错误 linktype=%r n=%d" % (lt, len(recs)))
    res = scan_streams(recs, lt)
    if ("10.0.0.2:40000->8.8.8.8:53") not in res["streams"]:
        fails.append("case1: 四元组键不正确 %r" % (list(res["streams"]),))
    if not res["dns"] or res["dns"][0][1] != "flag.example.com":
        fails.append("case1: DNS 查询名解析错误 %r" % (res["dns"],))
    # 2) 边界拒绝：pcapng 魔数 / 过短文件 / 非 pcap
    for blob, msg in ((b"\x0a\x0d\x0d\x0a" + bytes(40), "pcapng"),
                      (b"\xd4\xc3\xb2\xa1" + bytes(8), "不足 24 字节"),
                      (b"GIF89a" + bytes(40), "非 pcap")):
        try:
            read_pcap(blob)
            fails.append("case2: %s 未被拒绝" % msg)
        except ValueError:
            pass
    # 3) 参数不足：截断记录不崩，DNS 载荷过短报错
    trunc = cap[:-30]
    recs2, lt2 = read_pcap(trunc)
    if len(recs2) != 0:
        fails.append("case3: 截断记录应被丢弃，实得 %d" % len(recs2))
    try:
        dns_qname(b"\x12\x34")
        fails.append("case3: 过短 DNS 载荷未被拒绝")
    except ValueError:
        pass
    # 4) 固定输入可复现：同一份 pcap 两次解析结果完全相同
    a = sorted(scan_streams(read_pcap(cap)[0], 1)["streams"])
    b = sorted(scan_streams(read_pcap(cap)[0], 1)["streams"])
    if a != b:
        fails.append("case4: 两次解析结果不一致")
    # 5) 载荷扫描 + HTTP 请求行
    http_frame = _eth_ipv4_udp(b"GET /flag?a=1 HTTP/1.1\r\nHost: x\r\n\r\n", 40001, 80)
    if http_first_line(b"GET /flag HTTP/1.1\r\n") != "GET /flag HTTP/1.1":
        fails.append("case5: HTTP 请求行识别失败")
    if "flag{" not in suspicious(b"xx flag{abc} yy"):
        fails.append("case5: 可疑串扫描漏掉 flag{")
    if suspicious(b"plain") != []:
        fails.append("case5: 干净载荷不应报可疑")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（DNS 解析、非法魔数拒绝、截断记录丢弃、"
          "固定输入可复现、可疑串扫描）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="经典 pcap 协议还原")
    ap.add_argument("--file", help="pcap 文件")
    ap.add_argument("--stream", type=int, help="只看第 N 条流（按出现顺序）")
    ap.add_argument("--hex", action="store_true", help="打印载荷十六进制")
    ap.add_argument("--dns", action="store_true", help="只列 DNS 查询")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("必须提供 --file（或 --selftest）")
    try:
        with open(args.file, "rb") as fh:
            data = fh.read()
        recs, lt = read_pcap(data)
        res = scan_streams(recs, lt)
    except (ValueError, OSError, struct.error) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2

    keys = list(res["streams"])
    print("记录 %d 条，链路类型 %d，流 %d 条" % (len(recs), lt, len(keys)))
    if args.dns:
        for idx, name in res["dns"]:
            print("  #%-4d %s" % (idx, name))
        return 0
    for i, key in enumerate(keys):
        pkts = res["streams"][key]
        blob = b"".join(p for _, _, p in pkts)
        mark = suspicious(blob)
        print("  [%d] %-40s 包=%d 字节=%d %s"
              % (i, key, len(pkts), len(blob), ("可疑:" + ",".join(mark)) if mark else ""))
        if args.stream is not None and i == args.stream:
            for idx, ts, payload in pkts:
                print("      #%d t=%.6f len=%d %r" % (idx, ts, len(payload), payload[:80]))
                if args.hex:
                    print("      " + payload[:64].hex())
    for idx, line in res["http"][:20]:
        print("  HTTP #%-4d %s" % (idx, line))
    return 0


if __name__ == "__main__":
    sys.exit(main())

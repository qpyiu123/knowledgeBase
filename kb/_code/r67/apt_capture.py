"""读取本地经典 PCAP 的 APT 单会话记录，检查每条 CBC 填充反馈。

用法：python apt_capture.py input.pcap
仅支持该赛题的 Linux SLL2、IPv4/TCP 和逐行响应格式；不会连接原服务。
"""

import argparse
import base64
from pathlib import Path
from struct import Struct

from padding_transcript import recover


def extract(path, port=10005):
    raw = path.read_bytes()
    endian = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">"}.get(raw[:4])
    if (
        not endian
        or len(raw) < 24
        or Struct(endian + "I").unpack_from(raw, 20)[0] != 276
    ):
        raise ValueError("需要链路类型为 Linux SLL2（276）的经典 PCAP。")
    record = Struct(endian + "IIII")
    offset = 24
    flow = None
    seen, end = {}, {}
    streams = {True: bytearray(), False: bytearray()}
    original, pending, queries = None, None, []
    while offset < len(raw):
        _, _, caplen, _ = record.unpack_from(raw, offset)
        offset += record.size
        frame = raw[offset : offset + caplen]
        if len(frame) != caplen:
            raise ValueError("抓包记录不完整。")
        offset += caplen
        if len(frame) < 60 or frame[:2] != b"\x08\x00":
            continue
        ip = frame[20:]
        if ip[0] >> 4 != 4 or ip[9] != 6:
            continue
        ihl = (ip[0] & 15) * 4
        length = int.from_bytes(ip[2:4], "big")
        tcp = ip[ihl:length]
        if len(tcp) < 20:
            continue
        sport, dport = Struct(">HH").unpack_from(tcp)
        if port not in (sport, dport):
            continue
        if len(ip) < length or int.from_bytes(ip[6:8], "big") & 0x3FFF:
            raise ValueError("抓包有截断或分片，需要先完整重组。")
        server = sport == port
        key = (ip[12:16], sport, ip[16:20], dport)
        canonical = key if server else (key[2], key[3], key[0], key[1])
        seq = int.from_bytes(tcp[4:8], "big")
        data = tcp[(tcp[12] >> 4) * 4 :]
        if not data:
            continue
        flow = flow or canonical
        if canonical != flow:
            raise ValueError("抓包中有多个会话，请先分流。")
        if (key, seq) in seen:
            if data != seen[key, seq]:
                raise ValueError("相同序号出现不一致的数据。")
            continue
        if seq != end.get(key, seq):
            raise ValueError("TCP 序号不连续，请先完成重组。")
        end[key] = (seq + len(data)) & 0xFFFFFFFF
        seen[key, seq] = data
        buf = streams[server]
        buf.extend(data)
        while (line_end := buf.find(b"\n")) >= 0:
            line = bytes(buf[:line_end]).strip().lstrip(b"> ")
            del buf[: line_end + 1]
            if server and line in (b"False", b"Data update"):
                if pending is None:
                    raise ValueError("反馈缺少对应请求。")
                queries.append((pending, line == b"Data update"))
                pending = None
                continue
            try:
                item = base64.b64decode(line, validate=True)
            except ValueError:
                continue
            if server and len(item) >= 32 and not len(item) % 16:
                if original is not None and original != item:
                    raise ValueError("发现不同的初始密文，需先确定会话。")
                original = item
            elif not server and len(item) == 32:
                if pending is not None:
                    raise ValueError("发现尚未收到反馈的上一条请求。")
                pending = item
    if original is None or pending is not None:
        raise ValueError("缺初始密文或成对反馈。")
    return original, queries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap", type=Path)
    parser.add_argument("--port", type=int, default=10005)
    args = parser.parse_args()
    _, report = recover(*extract(args.pcap, args.port))
    print(
        f"已核对 {report['queries_verified']} 条反馈，其中 {report['successes_verified']} 条成功。"
    )


if __name__ == "__main__":
    main()

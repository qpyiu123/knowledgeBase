---
title: "软件系统安全赛-traffic_hunt"
category: forensics
tags: ["软件系统安全赛", "forensics", "Behinder-webshell", "AES-ECB-MD5", "pcap-analysis", "traffic-encryption"]
signals: ["软件系统安全赛 2026", "Behinder-webshell", "AES-ECB-MD5", "pcap-analysis", "traffic-encryption", "tshark", "AES-GCM", "python-pack", "C2-implant", "forensic_disk", "traffic_hunt", "AES-ECB", "MD5", "blockIndex"]
difficulty: hard
source: "https://www.ctfiot.com/302168.html"
tools: ["Python", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 软件系统安全赛-traffic_hunt

> 赛事：软件系统安全赛 2026 | 方向：forensics | 难度：hard | 工具：Python、tshark

## 一句话总结

软件系统安全赛traffic_hunt流量分析,冰蝎马AES-ECB+MD5(p)密钥推导+分片文件上传(blockIndex乱序重组)+Python pyc C2植入物+AES-GCM后渗透通信解密。

## 攻击链

1. HTTP协议前半部分:目录扫描(404状态)
2. 第404205包开始:植入Java class文件(冰蝎马第一阶段)
3. 反编译class:使用p参数值的MD5前16字节作为AES ECB密钥
4. p=HWmc2TLDoihdlr0N,key=1f2c8075acd3d118
5. 后续流量:AES ECB加密的冰蝎载荷,tshark提取frame.number 404652-412212的POST data
6. 攻击者用冰蝎文件上传模块,文件分片(blockIndex乱序)
7. 前10文件顺序:404339(2)→404376(5)→404433(4)→404440(9)→404461(0)→404488(7)→404513(3)→404575(8)→404578(1)→404615(6)
8. 11-349文件按blockIndex顺序,最后3个:412223(351)→412240(349)→412271(350)
9. 拼接得ELF文件,运行发现是python打包
10. pycdc反编译pyc:C2植入物,AES-GCM加密,key=IhbJfHI98nuSvs5JweD5qsNvSQ/HHcE/SNLyEBU9Phs=
11. 报文:4 bytes长度|12 bytes nonce|n bytes密文|16 bytes GCM tag
12. 解密冰蝎后流量得flag: dart{d9850b27-85cb-4777-85e0-df0b78fdb722}

## 关键 payload

```
dart{d9850b27-85cb-4777-85e0-df0b78fdb722}
```

## 经验教训

冰蝎马用MD5(p)前16字节作AES-ECB密钥是标准实现;分片文件上传blockIndex乱序是流量侧的检测规避;Python打包的ELF+pyc反编译是C2分析常见路径;AES-GCM(4B长度+12B nonce+n字节密文+16B tag)是自定义协议稳定格式。

## 标签

Behinder-webshell、AES-ECB-MD5、pcap-analysis、traffic-encryption、tshark、AES-GCM、python-pack、C2-implant、base64-extract、ELF-reassemble

## 参考来源

- https://www.ctfiot.com/302168.html
- 原文件：软件系统安全赛-traffic_hunt.full.md

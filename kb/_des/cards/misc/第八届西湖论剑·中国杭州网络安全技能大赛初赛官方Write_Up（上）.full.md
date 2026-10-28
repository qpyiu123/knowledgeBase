---
title: "第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write Up(上)"
category: misc
tags: ["西湖论剑", "misc", "Crypto-随机数shuffle", "预言机+Coppersmall_roots", "矩阵RSA+non-commutative", "QuarticRing"]
signals: ["西湖论剑 2025", "Crypto-随机数shuffle", "预言机+Coppersmall_roots", "矩阵RSA+non-commutative", "QuarticRing", "DigitalSig-DSA篡改", "内存取证Win7SP1", "AntSword编码", "IOT-u-boot", "rce", "sha256", "shuffle", "matrixRSA", "Coppersmall_roots"]
difficulty: hard
source: "https://www.ctfiot.com/225639.html"
tools: ["C", "ROP", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write Up(上)

> 赛事：西湖论剑 2025 | 方向：misc | 难度：hard | 工具：C、ROP、tshark

## 一句话总结

第八届西湖论剑初赛官方上半:420所高校758队3960人,涵盖已悟(sha256+shuffle预言机)+matrixRSA(p0+Coppersmall_roots+矩阵RSA+non-commutative)+NewYearRing4+DSASignatureData(DSA verify识别篡改)+easyrawencode(volatility+AES-EAX+RC4签名)+IOT(blink/u-boot/Wavlink-CSRF+libwebutil JALR+sharkp)

## 攻击链

1. 已悟: 10w个key爆破hashlib.sha256(str(key))→random.seed→random.shuffle(S1)→S1.index(id)==S1[id] and S1[id]+id==15找(S1[id],id)|matrixRSA: 已知p0+100bit小根x,PolynomialRing+small_roots解p完整→矩阵RSA φ=(p²-1)(p²-p)(q²-1)(q²-q)求d|CSCS: 已知p,q,n (差6)→d=inverse(e,phi)→RSA私钥生成→PKCS1_v1_5解密→AES-128+HMAC-SHA256→DEC_UnMunge2|COM_UnMunge2 (XOR seq+_LongSwap+表)|DSASignatureData: pyshark抓pcapng HTTP POST json→DSA verify(name/idcard/phone SHA256)找出篡改数据|easyrawencode: volatility envars hackkey+AES EAX解CSV+RC4解签名|blink: QEMU u-boot.rom load ide 0:2 0x0000000 flag|easy-uboot: qemu -bios u-boot.rom|linkon: Wavlink CGI CSRF Referer伪造→libwebutil.so pop {lr}/do_system+JALR|sharkp: 摄像头流量分析RCE接口名+C2 IP

## 关键 payload

```
S1.index(id)==S1[id] and S1[id]+id==15|p0<<100+x, f.monic(), f.small_roots(X=2^100, beta=0.4)|d=inverse(e, (p²-1)(p²-p)(q²-1)(q²-q))|p=7605291...6221, q=7605291...6527, e=0x10001|COM_UnMunge2(c, len, seq[0]): c ^= seq; c ^= (0xa5 | (j<<j) | j | mungify_table2[(i+j)&0xf]); c = _LongSwap(c); c ^= ~seq|tshark -Y ''http.request.uri.query.parameter'' -T fields|libwebutil_base=0x77e1e000, fmt=0x578b8, rop=0x7970, gp=0x5d550
```

## 经验教训

1) 预言机攻击:通过观察S1[0..15] shuffle结果找不变对(S1[i]+i=15)反推sha256 key; 2) Coppersmith small_roots:已知p0(高位)+未知x(低位),多项式f=p0*2^kbits+x, f.small_roots(X=2^kbits)解x; 3) 矩阵RSA:矩阵C,φ=(p²-1)(p²-p)(q²-1)(q²-q),d=inverse(e,φ),M=C^d元素级long_to_bytes; 4) Com_UnMunge2算法:c^=seq→c^(0xa5|j<<j|j|mungify_table2[(i+j)&0xf])→_LongSwap→c^=~seq; 5) DSA非对称验证:每个字段独立签名,改一个字段只影响该字段签名; 6) Wavlink CSRF绕过:Referer必为 wifi.wavlink.com + POST /cgi-bin/login.cgi page=Goto_chidx&wlanUrl=140字节ROP; 7) MIPS ROP:libwebutil_base+0x7970(lw $gp;do_system;jalr $t9); 8) QEMU u-boot.rom:load ide 0:2 0x0000000 加载vmlinux

## 标签

Crypto-随机数shuffle、预言机+Coppersmall_roots、矩阵RSA+non-commutative、QuarticRing、DigitalSig-DSA篡改、内存取证Win7SP1、AntSword编码、IOT-u-boot、IOT-Wavlink-CSRF、MIPS-ROP、流量包USB-HID

## 参考来源

- https://www.ctfiot.com/225639.html
- 原文件：第八届西湖论剑·中国杭州网络安全技能大赛初赛官方Write_Up（上）.full.md

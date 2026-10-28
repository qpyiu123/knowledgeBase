---
title: "第十五届蓝桥杯大赛网络安全赛项个人赛Writeup"
category: web
tags: ["蓝桥杯网络安全", "web", "Web-robots.txt", "Misc-流量包追踪", "Crypto-RSA-yafu分解n", "DWT-水印DWT+Arnold"]
signals: ["蓝桥杯网络安全 2024", "Web-robots.txt", "Misc-流量包追踪", "Crypto-RSA-yafu分解n", "DWT-水印DWT+Arnold", "Re-XXTEA", "Re-RC4", "Pwn-UAF", "ECDSA同k攻击", "heap_exploit", "robots", "txt", "DWT", "Arnold"]
difficulty: medium
source: "https://www.ctfiot.com/176353.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第十五届蓝桥杯大赛网络安全赛项个人赛Writeup

> 赛事：蓝桥杯网络安全 2024 | 方向：web | 难度：medium

## 一句话总结

第十五届蓝桥杯网络安全7题:robots.txt+流量包追踪+DWT水印+Arnold逆+yafu分解RSA(差206)+魔改XXTEA(rounds=(415/n)+114)+RC4(gamelab@)+UAF(tcache+fastbin+free_hook)+ECDSA同k攻击

## 攻击链

1. 爬虫协议: /robots.txt→3个disallow路径→找flag|packet: ctrl+F搜flag+追踪流+base64解码|缺失的数据: 压缩包密码pavilion爆破+DWT水印逆+Arnold逆变换|Theorem: yafu分解n(p,q差206)|欢乐时光: 魔改XXTEA rounds=(415/n)+114 delta=0x61C88647+key=''79696755 67346f6c 69231231 5f674231''|rc4: key=''gamelab@''+42字节密文RC4解密|ezheap: 0x202405菜单选项触发UAF+tcache满转fastbin+0x430堆叠+free_hook覆盖+system|signature: ECDSA同k攻击(hi., hello.同k)

## 关键 payload

```
/robots.txt + 追踪流|pavilion (DWT+Arnold)|yafu factor(n=94581028682900113123648734937784634645486813867065294159875516514520556881461611966096883566806571691879115766917833117123695776131443081658364855087575006641022211136751071900710589699171982563753011439999297865781908255529833932820965169382130385236359802696280004495552191520878864368741633686036192501791)|XXTEA rounds=int((415/n)+114); delta=0x61C88647; key=[0x79696755, 0x67346f6c, 0x69231231, 0x674231]|RC4 key='gamelab@' + 42字节密文|sendlineafter("4.exit", str(0x202405)) → delete_item(p, 1) + delete_item(p, 0)|k = ((h1 - h2) * mod_inverse(s1 - s2, n)) % n, dA = (mod_inverse(r1, n) * (k * s1 - h1)) % n
```

## 经验教训

1) robots.txt:3个Disallow路径逐个访问找flag; 2) DWT+Arnold水印逆:pywt.wavedec2(db2, level=3) + deArnold; 3) RSA yafu分解:差206的两个P154因子直接被分解; 4) XXTEA rounds魔改:rounds=(415/n)+114; 5) RC4标准实现:KSA+PRGA生成器+XOR; 6) 菜单题UAF:sendlineafter("4.exit", str(0x202405))触发特殊选项; 7) ECDSA同k:k=(h1-h2)/mod_inverse(s1-s2,n); dA=(k*s1-h1)/r1 mod n

## 标签

Web-robots.txt、Misc-流量包追踪、Crypto-RSA-yafu分解n、DWT-水印DWT+Arnold、Re-XXTEA、Re-RC4、Pwn-UAF、ECDSA同k攻击

## 参考来源

- https://www.ctfiot.com/176353.html
- 原文件：第十五届蓝桥杯大赛网络安全赛项个人赛Writeup.full.md

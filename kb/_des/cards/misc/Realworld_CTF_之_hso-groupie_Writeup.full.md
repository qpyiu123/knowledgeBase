---
title: "Realworld CTF 之 hso-groupie Writeup (xpdf 4.03 JBIG2 RCE)"
category: misc
tags: ["Realworld CTF", "misc", "xpdf", "pdftohtml", "jbig2-decode", "integer-overflow"]
signals: ["Realworld CTF 2022", "xpdf", "pdftohtml", "jbig2-decode", "integer-overflow", "heap-overflow", "turing-complete", "jbig2-encoder", "project-zero", "misc_unknown", "Realworld", "CTF", "hso-groupie", "JBIG2Stream"]
difficulty: hard
source: "https://www.ctfiot.com/25951.html"
tools: ["Python", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Realworld CTF 之 hso-groupie Writeup (xpdf 4.03 JBIG2 RCE)

> 赛事：Realworld CTF 2022 | 方向：misc | 难度：hard | 工具：Python、ROP

## 一句话总结

Realworld CTF 之 hso-groupie：xpdf 4.03 JBIG2Stream 整数溢出 + 堆风水覆盖 GList 后备存储 + 图灵完备 (全加器 + 5 种 bit 操作) + ROP/Shellcode 完整 exp PDF。

## 攻击链

1. Project Zero 启示: NSO 0-click iMessage 漏洞 = JBIG2Stream 整数溢出 + 图灵完备运算
2. 题目: xpdf 4.03 pdftohtml Clone-and-Pwn + flag in /run/secrets/flag
3. jbig2enc fcd14492 标准 + jbjbarith.cpython 算术编码库 + sploit.py 利用脚本
4. 漏洞点: JBIG2Stream::readTextRegionSeg numSyms += getSize() 整数溢出
5. gmallocn(numSyms, sizeof(JBIG2Bitmap *)) 分配过小 → syms[] 堆溢出
6. 关键构造: refSegs 中一些 seg->getSize() 很大 (4GB) 但实际可控制 segment 类型
7. 堆风水: 溢出块覆盖 GList 后备存储指针
8. 大 size segment 指针被替换为 jbig2SegBitmap 跳过检索
9. 利用 chain: 整数溢出 → 堆溢出 → 写 pageBitmap.Width/Height
10. pageBitmap.expand 越界读写 + combine (与/或/异或/替换) 5 种运算
11. 利用 pageBitmap 与其它 bitmaps 的与或非运算构建图灵完备小型计算机
12. 全加器 → ROP 构造 → 栈上 shellcode
13. PDF 构造: MyStream1 (FlateDecode) + MyStream2 (JBIG2Decode) + JBIG2Globals 引用
14. JBIG2Segment: EOFSeg / SymbolDictSeg / PageInfoSeg / GenericRegionSeg
15. combine 函数: dest |= src1 & m2 / dest &= src1 | m1 等 5 种
16. 完整 exp: jbig2enc + python3 sploit.py + python2 pdf.py sploit > sploit.pdf
17. gdbserver --cap-add=SYS_PTRACE --security-opt seccomp=unconfined docker 调试

## 关键 payload

```
gmallocn(numSyms, sizeof(JBIG2Bitmap*)) 整数溢出后 syms[k++] = symbolDict->getBitmap(k) 堆溢出
```

## 经验教训

JBIG2 算术编码 + pageBitmap 与/或/异或/替换 5 种运算可以构建图灵完备计算机；整数溢出 + 堆风水是 Project Zero 0-click 攻击核心思路；Clone-and-Pwn 模式需看最近 CVE 修复记录。

## 标签

xpdf、pdftohtml、jbig2-decode、integer-overflow、heap-overflow、turing-complete、jbig2-encoder、project-zero、arith-coder、bitmap

## 参考来源

- https://www.ctfiot.com/25951.html
- 原文件：Realworld_CTF_之_hso-groupie_Writeup.full.md

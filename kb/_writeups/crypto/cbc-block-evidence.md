---
title: "CBC：用公开的分组解密值或离线填充反馈恢复明文"
category: "crypto"
kind: "writeup"
tags: ["CBC", "ECB 分组解密", "离线填充反馈", "PCAP"]
signals: ["IV 拼在密文前", "Data update", "PKCS#7"]
source: "https://www.ctfplus.cn/problem-detail/1862864615294111744/description"
origin_id: "r67-cbc-block-evidence"
relates_to: ["crypto/rsa-padding-oracle.md", "forensics/pcap-basics.md"]
verification: "本机用附件公开数据回验"
---

# CBC：用公开的分组解密值或离线填充反馈恢复明文

## 先看这一步

CBC 的明文块是单块解密值与前一块的异或。附件若已给单块解密输出，就直接按块对齐；只有填充反馈时，先从记录恢复中间值。

**适用时**：直接对照的两份数据来自同一密钥和密文；抓包还需有完整、能配对的请求和反馈。

**留意**：APT 的每块成功响应按填充长度 1 到 16 排列。换抓包先查缺包、乱序和假阳性。

## 不用谢喵：已经给出单块解密值

题目把初始向量 IV 放在密文前，再把整串交给 ECB 解密打印。ECB 独立解每块，所以第一块是 `D(IV)`，后面才是 `D(C1)、D(C2)…`。丢掉第一块。剩余输出依次与原来的 IV 或上一密文块异或，得到 CBC 的原文。本次核对了两块，没用题目展示的示意密钥。

## APT：只有已经记录的填充反馈

先读经典 PCAP 的链路类型 276（Linux SLL2），再按同一个 TCP 会话重组并去重传。样本中 32 字节请求的前半是修改后的 IV，后半是目标块；`Data update` 表示接受，`False` 表示拒绝。确认某次成功的填充长度为 `j` 后，用修改后 IV 的倒数第 `j` 个字节异或 `j`，就是目标解密值的对应字节。

## 怎么回验

这份抓包有 3 个目标块，每块依次有 16 条成功反馈。还原后重算全部 5,849 条请求的接受或拒绝，再按 PKCS#7（按长度重复填充字节）核对原文尾部。若第一条接受来自更长的已有填充，直接按顺序还原会冲突。遇到缺包、乱序或这种假命中，先复查反馈，不补猜状态。脚本只读取本地抓包。

## 配套代码

`kb/_code/r67/case_relations.py`、`kb/_code/r67/apt_capture.py`、`kb/_code/r67/padding_transcript.py`。函数接收题目的公开数值；不会运行题目源码。

重放抓包：在代码目录运行 `python apt_capture.py input.pcap`。

## 出处

- [不用谢喵](https://www.ctfplus.cn/problem-detail/1862864615294111744/description)：汇编中的 `题目/ctfplus-1862864615294111744/WP.md`。
- APT：离线填充反馈抓包：汇编中的 `题目/zhejiang-APT/WP.md`。
- [NIST SP 800-38A：CBC 分组关系](https://csrc.nist.gov/pubs/sp/800/38/a/final)。

---
title: "RSA 數字簽名"
category: crypto
tags: [licensed chinese reference]
signals: [RSA 數字簽名]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/signature/rsa.md"
tools: []
origin: imported
origin_id: ctf-wiki-814deedc7117d1
origin_sha256: 8dabd1c82745b61d3bded407dd43389a38c2d9741e5843caf15a63c764a75605
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# RSA 數字簽名

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/signature/rsa.md

# RSA 數字簽名

## 原理

原理類似於 RSA 加密，只是這裏使用私鑰進行加密，將加密後的結果作爲簽名。

## 2018 Backdoor Awesome mix1

首先，可以簡單分析源碼，這裏程序使用 PKCS1_V1.5 進行了 RSA 簽名，這會對明文消息進行擴展，具體擴展規則請參考 https://www.emc.com/collateral/white-papers/h11300-pkcs-1v2-2-rsa-cryptography-standard-wp.pdf 。這裏給出對應擴展腳本，對應於題目中的 `from Util import PKCS1_pad as pad` 


程序希望我們給出 `n,e` 使得程序滿足 

$h(m)^e mod \ n=pad(m)$

這裏我們已經知道 `h(m)，pad(m)`。顯然如果我們控制 `e=1`的話，那麼

$h(m)-pad(m)=kn$

那麼如果我們可以設置 k=1，既可以得到 n。

本地部署 `socat TCP4-LISTEN:12345,fork EXEC:./mix1.py`。

exp 如下


效果如下


## 2018 Backdoor Awesome mix2

本地部署 `socat TCP4-LISTEN:12345,fork EXEC:./service.py`。

題目類似於上面的題目，唯一的區別在於對於 e 有約束，必須大於 3，所以我們不能使用 1 了。

$h(m)^e mod \ n=pad(m)$

這裏我們已經知道 `h(m)，pad(m)`。我們只需要構造剩下的數即可，這裏我們構造 n 爲素數，使得 n-1是一個光滑數，這樣就可以使用 pohlig_hellman 算法了。


有兩點需要注意

1. 由於 $g^x=y$ 中的 g 和 y 都是給定的，我們新找到的 n，不一定 g 的冪次構成的羣會包含 y，所以可能求解失敗，所以需要多次求解。
2. 源代碼中雖然 `n.bit_length() <= 1025`，但是其實 n 在滿足不小於 signature 的條件時，必須滿足如下條件（pycrypto 源碼）


所以我們最好設置 n 爲1024 比特位。

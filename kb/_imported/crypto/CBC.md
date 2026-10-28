---
title: "CBC"
category: crypto
tags: [licensed chinese reference]
signals: [CBC]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/blockcipher/mode/cbc.md"
tools: []
origin: imported
origin_id: ctf-wiki-8ceed905d1c718
origin_sha256: 51f679098693e0516f885b8dae465b7e122feb52fda5ba1ebc9dcb0c72f2f61d
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# CBC

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/blockcipher/mode/cbc.md

# CBC

CBC全稱爲密碼分組鏈接（Cipher-block chaining） 模式，這裏

- IV 不要求保密
- IV 必須是不可預測的，而且要保證完整性。

## 加密

〔原图省略〕

## 解密

〔原图省略〕

## 優缺點

### 優點

1. 密文塊不僅和當前密文塊相關，而且和前一個密文塊或 IV 相關，隱藏了明文的統計特性。
2. 具有有限的兩步錯誤傳播特性，即密文塊中的一位變化只會影響當前密文塊和下一密文塊。
3. 具有自同步特性，即第 k 塊起密文正確，則第 k+1 塊就能正常解密。

### 缺點

1. 加密不能並行，解密可以並行。

## 應用

CBC 應用十分廣泛

- 常見的數據加密和 TLS 加密。
- 完整性認證和身份認證。

## 攻擊

###  字節反轉攻擊

#### 原理
字節反轉的原理十分簡單，我們觀察**解密過程**可以發現如下特性:

- IV 向量影響第一個明文分組
- 第 n 個密文分組可以影響第 n + 1 個明文分組

假設第$n$個密文分組爲$C_n$，解密後的第$n$個明文分組爲爲$P_n$。

然後$P_{n+1}=C_n~\text{xor}~f(C_{n+1})$。

其中$f$函數爲圖中的$\text{Block Cipher Decryption}$。

對於某個信息已知的原文和密文，然後我們可以修改第$n$個密文塊$C_n$爲$C_n~\text{xor}~P_{n+1}~\text{xor}~A$。然後再對這條密文進行解密，那麼解密後的第$n$個明文快將會變成$A$。

#### 例題


可見題目希望我們提供一個加密的字符串，如果這個字符串解密後最後的內容爲admin。程序將會輸出明文。所以題目流程爲先隨便提供一個明文，然後將密文進行修改，使得解密後的字符串最後的內容爲admin,我們可以枚舉flag的長度來確定我們需要在什麼位置進行修改。

以下是exp.py

### Padding Oracle Attack
具體參見下面的介紹。

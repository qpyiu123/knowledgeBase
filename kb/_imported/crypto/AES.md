---
title: "AES"
category: crypto
tags: [licensed chinese reference]
signals: [AES]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/blockcipher/aes.md"
tools: []
origin: imported
origin_id: ctf-wiki-8977e94c8d31bd
origin_sha256: 54b28829c097960883060aa09b54a60124c75c6d65539c62876643343378af2a
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# AES

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/blockcipher/aes.md

# AES

## 基本介紹

Advanced Encryption Standard（AES），高級加密標準，是典型的塊加密，被設計來取代 DES，由 Joan Daemen 和 Vincent Rijmen 所設計。其基本信息如下

- 輸入：128 比特。
- 輸出：128 比特。
- SPN 網絡結構。

其迭代輪數與密鑰長度有關係，如下

| 密鑰長度（比特） | 迭代輪數 |
| :--------------: | :------: |
|       128        |    10    |
|       192        |    12    |
|       256        |    14    |

## 基本流程

### 基本概念

在 AES 加解密過程中，每一塊都是 128 比特，所以我們這裏明確一些基本概念。

〔原图省略〕

在 AES 中，塊與 State 之間的轉換過程如下

〔原图省略〕

所以，可以看出，每一個 block 中的字節是按照列排列進入到狀態數組的。

而對於明文來說，一般我們會選擇使用其十六進制進行編碼。

〔原图省略〕


### 加解密過程

這裏給個看雪上比較好的 [圖例](http://bbs.pediy.com/thread-90722.htm) ，以便於介紹基本的流程，每一輪主要包括

- 輪密鑰加，AddRoundKey
- 字節替換，SubBytes
- 行移位，ShiftRows
- 列混淆，MixColumns

〔原图省略〕

上面的列混淆的矩陣乘法等號左邊的列向量應該在右邊。

這裏再給一張其加解密的全圖，其解密算法的正確性很顯然。

〔原图省略〕

我們這裏重點關注一下以下。

#### 字節替換

在字節替換的背後，其實是有對應的數學規則來定義對應的替換表的，如下

〔原图省略〕

這裏的運算均定義在 $GF(2^8)$ 內。

#### 列混淆

這裏的運算也是定義在 $GF(2^8)$ 上，使用的模多項式爲 $x^8+x^4+x^3+1$。

#### 密鑰擴展

〔原图省略〕

## 等價解密算法

簡單分析一下，我們可以發現

- 交換逆向行移位和逆向字節代替並不影響結果。
- 交換輪密鑰加和逆向列混淆並不影響結果，關鍵在於
  - 首先可以把異或看成域上的多項式加法
  - 然後多項式中乘法對加法具有分配率。

## 攻擊方法

- 積分攻擊

## 2018 國賽 Crackmec

通過簡單分析這個算法，我們可以發現這個算法是一個簡化版的 AES，其基本操作爲

- 9 輪迭代

如下


根據程序流程，我們已知程序加密的結果，而 subbytes 和 shift_row 又是可逆的，所以我們可以獲取最後一輪加密後的結果。此時，我們還知道 box 對應的常數，我們只是不知道上一輪中 `cipher[4*j]` 對應的值，一共 32 位，如果我們直接爆破的話，顯然不可取，因爲每一輪都需要這麼爆破，時間不可接受。那麼有沒有其它辦法呢？其實有的，我們可以考慮中間相遇攻擊，即首先枚舉所有的 `cipher[4*j]` 與`cipher[4*j+1]` 的字節組合，一共256\*256 種。在枚舉剩下兩個字節時，我們可以先計算出其與密文的異或值，然後去之前的組閤中找，如果找到的話，我們就認爲是正確的。這樣複雜度瞬間降到 $O(2^{16})$。

代碼如下


運行結果


## 題目

- 2018 強網杯 決賽 revolver

## 參考文獻

- https://zh.wikipedia.org/wiki/%E9%AB%98%E7%BA%A7%E5%8A%A0%E5%AF%86%E6%A0%87%E5%87%86
- Cryptography and Network Security， Advanced Encryption Standard  ppt

---
title: "GIF"
category: misc
tags: [licensed chinese reference]
signals: [GIF]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/picture/gif.md"
tools: []
origin: imported
origin_id: ctf-wiki-5021f6a46edf45
origin_sha256: e234a2d9e60f9257b906bd23b3d1f00de4207c70835101d969e3a3bd4a26082b
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# GIF

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/picture/gif.md

# GIF

## 文件結構

一個GIF文件的結構可分爲

-   文件頭（File Header）
-   GIF 數據流（GIF Data Stream）
-   文件終結器（Trailer）

下表顯示了一個 GIF 文件的組成結構：

〔原图省略〕

中間的那個大塊可以被重複任意次

### 文件頭

GIF 署名（Signature）和版本號（Version）。GIF 署名用來確認一個文件是否是 GIF 格式的文件，這一部分由三個字符組成：`GIF`；文件版本號也是由三個字節組成，可以爲 `87a` 或 `89a`。

### 邏輯屏幕標識符（Logical Screen Descriptor）

Logical Screen Descriptor（邏輯屏幕描述符）緊跟在 header 後面。這個塊告訴 decoder（解碼器）圖片需要佔用的空間。它的大小固定爲 7 個字節，以 canvas width（畫布寬度）和 canvas height（畫布高度）開始。

### 全局顏色列表（Global Color Table）

GIF格式可以擁有global color table，或用於針對每個子圖片集，提供local color table。每個color
table由一個RGB（就像通常我們見到的（255，0，0）紅色 那種）列表組成。

### 圖像標識符（Image Descriptor）

一個 GIF 文件一般包含多個圖片。之前的圖片渲染模式一般是將多個圖片繪製到一個大的（virtual
canvas）虛擬畫布上，而現在一般將這些圖片集用於實現動畫。

每個 image 都以一個 image descriptor block（圖像描述塊）作爲開頭，這個塊固定爲 10 字節。

〔原图省略〕

### 圖像數據（Image Data）

終於到了圖片數據實際存儲的地方。Image Data是由一系列的輸出編碼（output codes）構成，它們告訴decoder（解碼器）需要繪製在畫布上的每個顏色信息。這些編碼以字節碼的形式組織在這個塊中。

### 文件終結器（Trailer）

該塊爲一個單字段塊，用來指示該數據流的結束。取固定值0x3b.

更多參見 [gif 格式圖片詳細解析](http://www.jianshu.com/p/df52f1511cf8)

## 空間軸

由於GIF的動態特性，由一幀幀的圖片構成，所以每一幀的圖片，多幀圖片間的結合，都成了隱藏信息的一種載體。

對於需要分離的GIF文件,可以使用`convert`命令將其每一幀分割開來


### 例題

> WDCTF-2017:3-2

打開gif後，思路很清晰，分離每一幀圖片後，將起合併得到完整的二維碼即可


掃碼後得到一串16進制字符串

`03f30d0ab8c1aa5....74080006030908`

開頭`03f3`爲`pyc`文件的頭，恢復爲`python`腳本後直接運行得到flag

## 時間軸

GIF文件每一幀間的時間間隔也可以作爲信息隱藏的載體。

例如在當時在XMan選拔賽出的一題

> XMAN-2017:100.gif

通過`identify`命令清晰的打印出每一幀的時間間隔


推斷 `20 & 10`  分別代表 `0 & 1`，提取每一幀間隔並進行轉化。


最後轉 ASCII 碼得到 flag。

## 隱寫軟件

- [F5-steganography](https://github.com/matthewgao/F5-steganography)

---
title: "DNS"
category: misc
tags: [licensed chinese reference]
signals: [DNS]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/dns.md"
tools: []
origin: imported
origin_id: ctf-wiki-240bf9afd231fb
origin_sha256: 009590df9513bba58d34cf268c2859ed46e80345d935c4013c13b72c0439c060
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# DNS

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/misc/traffic/protocols/dns.md

# DNS

## 簡介


`DNS` 通常爲 `UDP` 協議,報文格式


查詢包只有頭部和問題兩個部分， `DNS` 收到查詢包後，根據查詢到的信息追加回答信息、授權機構、額外資源記錄，並且修改了包頭的相關標識再返回給客戶端。

每個 `question` 部分


- `QNAME` ：爲查詢的域名，是可變長的，編碼格式爲：將域名用.號劃分爲多個部分，每個部分前面加上一個字節表示該部分的長度，最後加一個 `0` 字節表示結束
- `QTYPE` ：佔 `16` 位，表示查詢類型，共有 `16` 種，常用值有：`1` ( `A` 記錄，請求主機 `IP` 地址)、`2` ( `NS` ，請求授權 `DNS` 服務器)、`5` ( `CNAME` 別名查詢)


## 例題

> 題目：`BSides San Francisco CTF 2017` ： `dnscap.pcap` 

我們通過 `wireshark` 打開發現全部爲 `DNS` 協議,查詢名爲大量字符串`([\w\.]+)\.skullseclabs\.org`

我們通過 `tshark -r dnscap.pcap -T fields -e dns.qry.name > hex`提取後，利用 `python` 轉碼：


我們發現了幾條關鍵信息：


`flag` 確實包含在其中,但是有大量重複信息,一是應爲`question` 。在 `dns` 協議中查詢和反饋時都會用到，` -Y "ip.src == 192.168.43.91"`進行過濾後發現還是有不少重複部分。


根據發現的 `dnscat` 找到 https://github.com/iagox86/dnscat2/blob/master/doc/protocol.md 這裏介紹了 `dnscat` 協議的相關信息,這是一種通過 `DNS` 傳遞數據的變種協議,題目文件中應該未使用加密,所以直接看這裏的數據塊信息


在`qry.name`中去除其餘字段,只留下 `data` 快,從而合併數據,再從 `16` 進制中檢索`89504e.....6082`提取`png`,得到 `flag` 。


*flag*

〔原图省略〕


## 相關題目

- [IceCTF-2016:Search](https://mrpnkt.github.io/2016/icectf-2016-search/)
- [EIS-2017:DNS 101](https://github.com/susers/Writeups/blob/master/2017/EIS/Misc/DNS%20101/Write-up.md)

## 參考文獻

- https://github.com/lisijie/homepage/blob/master/posts/tech/dns%E5%8D%8F%E8%AE%AE%E8%A7%A3%E6%9E%90.md
- https://xpnsec.tumblr.com/post/157479786806/bsidessf-ctf-dnscap-walkthrough

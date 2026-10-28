---
title: "SSRF"
category: web
tags: [licensed chinese reference]
signals: [SSRF]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/ssrf.md"
tools: []
origin: imported
origin_id: ctf-wiki-a26ef54539a038
origin_sha256: b6319e1a968f6f8043d3674d0085e67c3fe8516256a58f9485a743feb824a624
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# SSRF

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/ssrf.md

# SSRF

## SSRF 簡介

SSRF，Server-Side Request Forgery，服務端請求僞造，是一種由攻擊者構造形成由服務器端發起請求的一個漏洞。一般情況下，SSRF 攻擊的目標是從外網無法訪問的內部系統。

漏洞形成的原因大多是因爲服務端提供了從其他服務器應用獲取數據的功能且沒有對目標地址作過濾和限制。

攻擊者可以利用 SSRF 實現的攻擊主要有 5 種：

1.  可以對外網、服務器所在內網、本地進行端口掃描，獲取一些服務的 banner 信息
2.  攻擊運行在內網或本地的應用程序（比如溢出）
3.  對內網 WEB 應用進行指紋識別，通過訪問默認文件實現
4.  攻擊內外網的 web 應用，主要是使用 GET 參數就可以實現的攻擊（比如 Struts2，sqli 等）
5.  利用 `file` 協議讀取本地文件等

## SSRF 漏洞出現的場景

-   能夠對外發起網絡請求的地方，就可能存在 SSRF 漏洞
-   從遠程服務器請求資源（Upload from URL，Import & Export RSS Feed）
-   數據庫內置功能（Oracle、MongoDB、MSSQL、Postgres、CouchDB）
-   Webmail 收取其他郵箱郵件（POP3、IMAP、SMTP）
-   文件處理、編碼處理、屬性信息處理（ffmpeg、ImageMagic、DOCX、PDF、XML）

## 常用的後端實現

1.  `file_get_contents`


2.  `fsockopen()`


3.  `curl_exec()`


## 阻礙 SSRF 漏洞利用的場景

-   服務器開啓 OpenSSL 無法進行交互利用
-   服務端需要鑑權（Cookies & User：Pass）不能完美利用
-   限制請求的端口爲http常用的端口，比如，80,443,8080,8090。
-   禁用不需要的協議。僅僅允許http和https請求。可以防止類似於file:///,gopher://,ftp:// 等引起的問題。
-   統一錯誤信息，避免用戶可以根據錯誤信息來判斷遠端服務器的端口狀態。
## 利用 SSRF 進行端口掃描

根據服務器的返回信息進行判斷，大部分應用不會判別端口，可通過返回的 banner 信息判斷端口狀態。

後端實現


構造一個前端頁面


請求非 HTTP 的端口可以返回 banner 信息。

或可利用 302 跳轉繞過 HTTP 協議的限制。

輔助腳本


[騰訊某處 SSRF 漏洞（非常好的利用點）附利用腳本](https://_thorns.gitbooks.io/sec/content/teng_xun_mou_chu_ssrf_lou_6d1e28_fei_chang_hao_de_.html)

## 協議利用

-   Dict 協議


-   Gopher 協議


-   File 協議

## 繞過姿勢
1.  更改IP地址寫法

2.  利用URL解析問題
## 危害

* 可以對外網、服務器所在內網、本地進行端口掃描，獲取一些服務的banner信息;
* 攻擊運行在內網或本地的應用程序（比如溢出）;
* 對內網web應用進行指紋識別，通過訪問默認文件實現;
* 攻擊內外網的web應用，主要是使用get參數就可以實現的攻擊（比如struts2，sqli等）;
* 利用file協議讀取本地文件等。

## 參考資料

-   [《Build Your SSRF EXP Autowork》豬豬俠](http://tools.40huo.cn/#!papers.md)
-   [騰訊某處 SSRF 漏洞（非常好的利用點）附利用腳本](https://_thorns.gitbooks.io/sec/content/teng_xun_mou_chu_ssrf_lou_6d1e28_fei_chang_hao_de_.html)
-   [bilibili 某分站從信息泄露到 ssrf 再到命令執行](https://_thorns.gitbooks.io/sec/content/bilibilimou_fen_zhan_cong_xin_xi_xie_lu_dao_ssrf_z.html)

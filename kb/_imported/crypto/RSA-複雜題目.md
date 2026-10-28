---
title: "RSA 複雜題目"
category: crypto
tags: [licensed chinese reference]
signals: [RSA 複雜題目]
difficulty: medium
source: "https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/asymmetric/rsa/rsa_complex.md"
tools: []
origin: imported
origin_id: ctf-wiki-9dcf3703633111
origin_sha256: aea7eb20d66487f95e4d0aaca9c96df9f8022fd1f3dbd24477c54d7ec58f3296
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# RSA 複雜題目

> 来源：https://github.com/ctf-wiki/ctf-wiki/blob/e225ddfcd420a7f54a5940f47336ebdf8c29b875/docs/zh-tw/docs/crypto/asymmetric/rsa/rsa_complex.md

# RSA 複雜題目

## 2018 Tokyo Western Mixed Cipher

題目給的信息如下所示：


- 每次交互可以維持的時間長度約爲 5 分鐘
- 每次交互中中n是確定的 1024 bit，但是未知， e 爲 65537
- 使用 aes 加密了 flag，密鑰和 IV 均不知道
- 每次密鑰是固定的，但是 IV 每次都會隨機
- 可以使用 encrypt 功能隨意使用 rsa 和 aes 進行加密，其中每次加密都會對 aes 的 iv 進行隨機
- 可以使用 decrypt 對隨意的密文進行解密，但是隻能知道最後一個字節是什麼
- 可以使用 print_flag 獲取 flag 密文
- 可以使用 print_key 獲取 rsa 加密的 aes 密鑰

本題目看似一個題目，實則是 3 個題目，需要分步驟解決。在此之前，我們準備好交互的函數


### GCD attack n

第一步我們需要把沒有給出的 n 算出來，因爲我們可以利用 encrypt 功能對我們輸入的明文 x 進行 rsa 加密，那麼可以利用整除的性質算 n

我們可以構造足夠多的 x，算出最夠多的 x ^ e - c，從而計算最大公約數，得到 n。


可以利用加密進行 check


### RSA parity oracle

利用 leak 的的最後一個字節，我們可以進行選擇密文攻擊，使用 RSA parity oracle 回覆 aes 的祕鑰


### PRNG Predict

這裏我們可以解密 flag 的16字節之後的內容了，但是前16個字節沒有 IV 是解密不了的。這時我們可以發現，IV 生成使用的隨機數使用了 getrandbits，並且我們可以獲取到足夠多的隨機數量，那麼我們可以進行 PRNG 的 predict，從而直接獲取隨機數

這裏使用了一個現成的的 java 進行 PRNG 的 Predict


寫了一個 python 直接調用 java


### EXP

整體攻擊代碼如下：


## 2016 ASIS Find the flag

這裏我們以 ASIS 2016 線上賽中 Find the flag 爲例進行介紹。

文件解壓出來，有一個密文，一個公鑰，一個 py 腳本。看一下公鑰。


這麼小的一個 $N$，先分解一下。


再看給的 py 腳本。


邏輯很簡單，讀取 flag，重複 30 遍爲密文。隨機取 $p$ 和 $q$，生成一個公鑰，寫入 `pubkey.pem`，再用腳本中的 `ext_rsa_encrypt` 函數進行加密，最後將密文寫入 `flag.enc`。

嘗試一下解密，提示密文過長，再看加密函數，原來當加密失敗時，函數會跳到異常處理，以一定算法重新取更大的 $p$ 和 $q$，直到加密成功。

那麼我們只要也寫一個相應的解密函數即可。


拿到 flag


## SCTF RSA1

這裏我們以 SCTF RSA1 爲例進行介紹，首先解壓壓縮包後，得到如下文件


嘗試解壓縮了一下 level1.zip 現需要密碼。然後根據 level1.passwd.enc 可知，應該是我們需要解密這個文件才能得到對應的密碼。查看公鑰


發現雖然說是 2048 位，但是顯然模數沒有那麼長，嘗試分解下，得到


然後就可以構造，並且解密，代碼如下


發現不對


這時候就要考慮其他情況了，一般來說現實中實現的 RSA 都不會直接用原生的 RSA，都會加一些填充比如 OAEP，我們這裏試試，修改代碼


果然如此，得到


得到解壓密碼。繼續，查看 level1 中的公鑰


似乎還是不是很大，再次分解，然後試了 factordb 不行，試試 yafu。結果分解出來了。


可以發現這兩個數非常相近，可能是 factordb 沒有實現這類分解。

繼而下面的操作類似於 level0。只是這次是直接解密就好，沒啥填充，試了填充反而錯

得到密碼 `fA35ORI11TLoN_Att1Ck_cL0sE_PrI8e_4acTorS`。繼續下一步，查看公鑰


發現私鑰 e 和 n 幾乎一樣大，考慮 d 比較小，使用 Wiener's Attack。得到 d，當然也可以再次驗證一遍。


這時我們解密密文，解密代碼如下


利用末尾的字符串 `wIe6ER1s_1TtA3k_e_t00_larg3` 解密壓縮包，注意去掉 B。至此全部解密結束，得到 flag。

## 2018 WCTF RSA

題目基本描述爲


這個題目現在已經沒有辦法在線獲取 binary 了，現在得到的 binary 是之前已經下載好的，我們當時需要登錄用戶的 admin 來下載對應的 generator。

通過簡單逆向這個 generator，我們可以發現這個程序是這麼工作的

- 利用用戶給定的 license（32 個字節），迭代解密某個**固定位置**之後的數據，每 32 個字節一組，與密鑰相異或得到結果。
- 密鑰的生成方法爲 

其中，固定位置就是在找源文件 `generator` 中第二次出現 `ENCRYPTED` 的位置，然後再次偏移 32 個字節。


同時，我們需要確保生成的文件的校驗對應的哈希值恰好爲指定的值，由於文件最後是一個 exe 文件，所以我們可以認爲最後的文件頭就是標準的 exe 文件，因此就不需要知道原始的 license 文件，進而我們可以編寫 python 腳本生成 exe。

在生成的 exe 中，我們分析出程序的基本流程爲

1. 讀取 license
2. 使用 license 作爲 seed 分別生成 pq
3. 利用 p，q 生成 n，e，d。

其漏洞出現在生成 p，q 的方法上，而且生成 p 和 q 的方法類似。

我們如果仔細分析下生成素數的函數的話，可以看到每個素數都是分爲兩部分生成的

1. 生成左半部分 512 位。
2. 生成右半部分 512 位。
3. 左右構成 1024 比特位，判斷是不是素數，是素數就成功，不是素數，繼續生成。

其中生成每部分的方式相同，方式爲


 只有 v9 會有所變化，但是它的範圍卻是固定的。

那麼，如果我們表示 p，q 爲

$p=a*2^{512}+b$

$q=c*2^{512}+d$

那麼

$n=pq=ac*2^{1024}+(ad+bc)*2^{512}+bd$

那麼

$n \equiv bd \bmod 2^{512}$

而且由於 p 和 q 在生成時，a，b，c，d 均只有 1000000007 種可能性。

進而，我們可以枚舉所有的可能性，首先計算出 b 可能的集合爲 S，同時我們使用中間相遇攻擊，計算

$n/d \equiv b \bmod 2^{512}$

這裏由於 b 和 d 都是 p 的尾數，所以一定不會是 2 的倍數，進而必然存在逆元。

這樣做雖然可以，然而，我們可以簡單算一下存儲空間

$64*1000000007 / 1024 / 1024 / 1024=59$

也就是說需要 59 G，太大了，，所以我們仍然需要進一步考慮

$n \equiv bd \bmod 2^{64}$

這樣，我們的內存需求瞬間就降到了 8 G左右。我們仍然使用枚舉的方法進行運算。

其次，我們不能使用 python，，python 佔據空間太大，因此需要使用 c/c++ 編寫。

枚舉所有可能的 d 計算對應的值 $n/d$ 如果對應的值在集合 S 中，那麼我們就可以認爲找到了一對合法的 b 和 d，因此我們就可以恢復 p 和 q 的一半。

之後，我們根據

$n-bd=ac*2^{1024}+(ad+bc)*2^{512}$

可以得到

$\frac{n-bd}{2^{512}} = ac*2^{512}+ad+bc$

$\frac{n-bd}{2^{512}} \equiv ad+bc \bmod 2^{512}$

類似地，我們可以計算出 a 和 c，從而我們就可以完全恢復出 p 和 q。

在具體求解的過程中，在求 p 和 q 的一部分時，可以發現因爲是模 $2^{64}$，所以可能存在碰撞（但其實就是一個是 p，另外一個是q，恰好對稱。）。下面我們就求得了 b 對應的 v9。

**注意：這裏枚舉出來的空間大約佔用 11 個 G（包括索引），所以請選擇合適的位置。**


其實，我們在真正得到 p 或者 q 的一部分後，另外一部分完全可以使用暴力枚舉的方式獲取，因爲計算量幾乎都是一樣的，最後結果爲


最後我們便拿到 flag 了。

**詳細的利用代碼請參見 ctf-challenge 倉庫。**

相關編譯指令，需要鏈接相關的庫。


## 參考

- https://upbhack.de/posts/wctf-2018-writeup-rsa/

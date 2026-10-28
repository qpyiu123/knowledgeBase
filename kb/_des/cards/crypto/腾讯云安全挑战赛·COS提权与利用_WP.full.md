---
title: "腾讯云安全挑战赛·COS提权与利用 WP"
category: crypto
tags: ["腾讯云安全挑战赛 2025", "crypto", "Java-CrackMe", "AES-ECB", "XOR-deobfuscate", "COS-bucket-policy"]
signals: ["腾讯云安全挑战赛 2025 2025", "Java-CrackMe", "AES-ECB", "XOR-deobfuscate", "COS-bucket-policy", "Tencent-Cloud-API", "CVM-ResetInstancesPassword", "COS-PutBucketACL-Deny", "IP-not-equal", "crypto_oracle", "COS", "Java", "CrackMe", "XOR"]
difficulty: hard
source: "https://www.ctfiot.com/271105.html"
tools: ["Java", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 腾讯云安全挑战赛·COS提权与利用 WP

> 赛事：腾讯云安全挑战赛 2025 2025 | 方向：crypto | 难度：hard | 工具：Java、Python

## 一句话总结

腾讯云安全挑战赛COS提权与利用WP,Java CrackMe反编译AES-ECB+XOR deobfuscate解出AK/SK/Token,COS Bucket Policy分析(IPCAM not-equal限制+PutBucketACL),CVM ResetInstancesPassword+SSRF绕过链。

## 攻击链

1. Java CrackMe:AbstractHashMap+密钥LiLiLLLiiiLLiiLLi="Q8Ro9cHYVAdBaRD8"(AES)
2. 静态初始化GIiIiLA.add(20+条base64)
3. AES-ECB解密每个base64
4. 再做XOR deobfuscate:i_start=(11963830^57816743)^(15501129^52968536),xor_key=(95558172^72233696)^(85510964^82109419)
5. 解出:secret_id="AKID3eUqV0RTdHaRQ6PeyFzouVVSsd1c5oU4dgxxMSdepyySy-3TzBV2As5bsmVZe6LW
6. secret_key="6ijalekmP0w5b4iiatUZVriHtd3iDTp98sbow/EhGGE=
7. token="8RWwthXC3rhLqqs60VtkfdrK2QVtRlua1eac99e9bd0f081699323aa8e9fbfa06...
8. region="ap-guangzhou",scheme="https
9. COS API:get_bucket_policy返回Policy,Action=name/cos:PutBucketACL+ip_not_equal
10. IP限制:["106.53.243.200","172.16.0.129"]
11. qcloud-cos-python-sdk-v5:pip install cos-python-sdk-v5 --break-system-packages
12. 绕过思路:从CVM API ResetInstancesPassword改机器密码+SSRF到PutBucketACL
13. CommonClient cvm.tencentcloudapi.com,Region=ap-guangzhou,Action=ResetInstancesPassword
14. params={"InstanceIds":["ins-xxx"],"Password":"Aa112211.","UserName":"root","ForceStop":true}

## 关键 payload

```
AES+deobfuscate AKID3eUqV0RTdHaRQ6PeyFzouVVSsd1c5oU4dgxxMSdepyySy-3TzBV2As5bsmVZe6LW
```

## 经验教训

云安全比赛常考"反编译获取云凭据+滥用云API提权",Java CrackMe的AES-ECB+XOR组合是典型混淆;COS Bucket Policy的ip_not_equal可被CVM SSRF绕过;ResetInstancesPassword是云提权关键API。

## 标签

Java-CrackMe、AES-ECB、XOR-deobfuscate、COS-bucket-policy、Tencent-Cloud-API、CVM-ResetInstancesPassword、COS-PutBucketACL-Deny、IP-not-equal、ip_restriction

## 参考来源

- https://www.ctfiot.com/271105.html
- 原文件：腾讯云安全挑战赛·COS提权与利用_WP.full.md

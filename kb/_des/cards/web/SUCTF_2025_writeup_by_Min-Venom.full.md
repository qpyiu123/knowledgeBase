---
title: "SUCTF 2025 writeup by Min-Venom"
category: web
tags: ["SUCTF", "web", "cakephp-5.1.4", "php-unserialize", "jinja2-pydash", "prototype-pollution"]
signals: ["SUCTF 2025", "cakephp-5.1.4", "php-unserialize", "jinja2-pydash", "prototype-pollution", "secp256k1", "signature-malleability", "solana-onchain", "deserialize", "SUCTF", "Min-Venom", "cakephp", "RejectedPromise", "ConstTypeNode"]
difficulty: medium
source: "https://www.ctfiot.com/223976.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SUCTF 2025 writeup by Min-Venom

> 赛事：SUCTF 2025 | 方向：web | 难度：medium

## 一句话总结

SUCTF 2025 Min-Venom：cakephp 5.1.4 新链 (RejectedPromise→ConstTypeNode→Table→MockClass) + pydash jinja2 + secp256k1 签名延展性。

## 攻击链

1. cakephp 5.1.4 加 __wakeup 限制，重新找入口
2. src/Internal/RejectedPromise.__destruct 拼接 reason 字符串
3. PHPStan\PhpDocParser\Ast\Type\ConstTypeNode.__toString 触发
4. 调 constExpr.__call 间接转 Cake\ORM\Table.__call
5. Table._behaviors BehaviorRegistry._methodMap = ['__tostring' => ['MockClass', 'generate']]
6. MockClass.generate() eval(classCode) call_user_func(MOCK '__phpunit_initConfigurableMethods', ...configurableMethods)
7. 构造 classCode = "system('find /etc/passwd -exec tac /flag.txt ;')
8. 序列化：RejectedPromise.reason = ConstTypeNode.constExpr = Table()
9. SU_blog: file 参数目录穿越读源码 + pydash jinja2 模板 RCE
10. 通过 __init__.__globals__.sys.modules.jinja2.runtime.exported[2] 注入
11. *;import os;os.system(''/read* >/tmp/gaoren.txt'')" 利用 2 分钟容器窗口写文件
12. SU_BBRE: 9 字节 data[i]+i 加密 + RC4 密钥 "suctf" 拼接 func1 地址 (栈溢出劫持)
13. Onchain Magician: secp256k1 签名延展性 v=28 与 v=27 + s'' = n - s
14. two signatures same signer but different signatureHash bypass
15. real_checkin: emoji 英文首字母拼 suctf{welcome_to_suctf_you_can_really_dance}
16. Onchain Checkin: Solana program address + Solana explorer 查 base58 公钥

## 关键 payload

```
signature2 = (27, r, n - s)
```

## 经验教训

椭圆曲线签名天然有两个 s 值，签名 hash 比较是常见绕过点。

## 标签

cakephp-5.1.4、php-unserialize、jinja2-pydash、prototype-pollution、secp256k1、signature-malleability、solana-onchain

## 参考来源

- https://www.ctfiot.com/223976.html
- 原文件：SUCTF_2025_writeup_by_Min-Venom.full.md

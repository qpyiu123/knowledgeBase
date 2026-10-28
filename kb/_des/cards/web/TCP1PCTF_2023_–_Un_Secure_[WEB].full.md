---
title: "TCP1PCTF 2023 – Un Secure [WEB]"
category: web
tags: ["TCP1PCTF", "web", "php-unserialize", "gadget-chain", "waf1-waf2-waf3", "eval-rce"]
signals: ["TCP1PCTF 2023", "php-unserialize", "gadget-chain", "waf1-waf2-waf3", "eval-rce", "reflection", "deserialize", "TCP1PCTF", "Secure", "PHP", "gadget", "chain", "RCE", "cookie"]
difficulty: medium
source: "https://www.ctfiot.com/139455.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TCP1PCTF 2023 – Un Secure [WEB]

> 赛事：TCP1PCTF 2023 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

TCP1PCTF 2023 Un Secure：PHP 反序列化 gadget chain 3 件套 + 反射 + 字符串拼接 RCE。

## 攻击链

1. cookie base64 反序列化
2. GadgetThree\Vuln.__toString 调 eval($this->cmd)
3. 三层 WAF 检查 waf1===1 / waf2==="\xde\xad\xbe\xef" / waf3===false
4. GadgetTwo\Echoers.__destruct 调 klass->get_x() 但 Vuln 是 __toString
5. GadgetOne\Adders.x 存 Vuln 实例
6. 链子: Echoers.klass=Adders → Adders.x=Vuln → Vuln.__toString→eval(cmd)
7. 反射拿私有属性
8. php ReflectionClass setAccessible(true) 改 waf1/waf2/waf3/cmd
9. 双 gadget: 一是反射 RCE; 二是 Adders(system(''id'')) 直接拼接

## 关键 payload

```
cookie=base64(O:17:"GadgetTwo\Echoers":1:{s:8:"*klass";O:16:"GadgetOne\Adders":1:{s:19:"GadgetOne\Addersx";O:16:"GadgetThree\Vuln":4:{...}}})
```

## 经验教训

PHP Gadget 链常以「destruct→call→toString→eval」为模板，命名空间 (GadgetOne/Two/Three) 故意制造跳转。

## 标签

php-unserialize、gadget-chain、waf1-waf2-waf3、eval-rce、reflection

## 参考来源

- https://www.ctfiot.com/139455.html
- 原文件：TCP1PCTF_2023_–_Un_Secure_[WEB].full.md

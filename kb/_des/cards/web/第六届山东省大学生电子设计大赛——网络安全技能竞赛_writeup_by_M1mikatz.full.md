---
title: "第六届山东省大学生电子设计大赛——网络安全技能竞赛 writeup by M1mikatz"
category: web
tags: ["山东省大学生电子设计大赛", "web", "Web-upload", ".htaccess", "UTF-7", "加换行"]
signals: ["山东省大学生电子设计大赛 2022", "Web-upload", ".htaccess", "UTF-7", "加换行", "反序列化", "成员数绕", "MT19937", "mt_recover", "file_upload", "M1mikatz", "payload", "define", "width"]
difficulty: medium
source: "https://www.ctfiot.com/87116.html"
tools: ["Radare2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第六届山东省大学生电子设计大赛——网络安全技能竞赛 writeup by M1mikatz

> 赛事：山东省大学生电子设计大赛 2022 | 方向：web | 难度：medium | 工具：Radare2

## 一句话总结

M1mikatz版同题合集,完整payload:#define width 1337+UTF-7+加换行+反序列化成员数绕+MT19937逆推+DSA r1=r2+蚁剑流量+RGB二维码+ezxor+arbitrary

## 攻击链

1. upload_100(同另一篇,含# define width 1337 trick+SetHandler+UTF-7+加换行)|pop_200: Show_index->Transfer->Transfer->File_operations链|签到/凯撒/三层base|mt: 32位素数+init+enc+recover+rrecover推|easy: DSA r1=r2|hacker: 蚁剑流量147流zip|draw: RGB转01+PIL画图|ezxor: x[i]^y[i]^ord(''a'')|arbitrary: read(14)+read(15)+write(-0x2)

## 关键 payload

```
# define width 1337 + SetHandler application/x-httpd-php + UTF-7+ADw?+AD0-system+换行绕关键字|class Transfer->method=Transfer->method=File_operations|recover(c)=inverse_right(18)+inverse_left_mask(15,4022730752)+inverse_left_mask(7,2636928640)+inverse_right(11)|rrecover(last)=((last-i)*inv)%n|k=(h1*r2-h2*r1)*invert(s1*r2-s2*r1,q)%q; flag=(k*s1-h1)*invert(r1,q)%q
```

## 经验教训

1) .htaccess首行#define width 1337 #define height 1337 满足尺寸限制; 2) SetHandler application/x-httpd-php+UTF-7编码(php_flag zend.multibyte 1)+加换行绕关键字; 3) 蚁剑流量特征:b1709fecc8bc5e=doL3Zhci93d3cvaHRtbC91cGxvYWQvcGFzc3dvcmQuanBn(从第二个字符开始是base64); 4) MT19937逆推:recover(4步逆XOR) + rrecover(逆init 100轮) + flag=md5(str(flag)); 5) DSA r1=r2:+已知h1,h2,s1,s2,r1,q 即可逆出k和flag

## 标签

Web-upload、.htaccess、UTF-7、加换行、反序列化、成员数绕、MT19937、mt_recover、DSA-r1r2、AntSword流量、RGB转二维码、ezxor、arbitrary

## 参考来源

- https://www.ctfiot.com/87116.html
- 原文件：第六届山东省大学生电子设计大赛——网络安全技能竞赛_writeup_by_M1mikatz.full.md

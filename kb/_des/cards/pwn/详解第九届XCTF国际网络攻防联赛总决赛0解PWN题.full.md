---
title: "详解第九届XCTF国际网络攻防联赛总决赛0解PWN题"
category: pwn
tags: ["第九届 XCTF 国际网络攻防联赛 总决赛", "pwn", "C++", "stdlib", "vtable", "type-confusion"]
signals: ["第九届 XCTF 国际网络攻防联赛 总决赛 2024", "C++", "stdlib", "vtable", "type-confusion", "vector-realloc", "cookie-check", "srand-rand", "base64-decode", "shellcode", "XCTF", "PWN", "All-Pwn-Red-Book", "App"]
difficulty: hard
source: "https://www.ctfiot.com/278572.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 详解第九届XCTF国际网络攻防联赛总决赛0解PWN题

> 赛事：第九届 XCTF 国际网络攻防联赛 总决赛 2024 | 方向：pwn | 难度：hard | 工具：C

## 一句话总结

第九届XCTF总决赛0解PWN题"All-Pwn-Red-Book App"详解,std::vector push_back realloc导致旧chunk遗留+UAF,vtable边界检查防type confusion,base64+AES+RSA加密链路。

## 攻击链

1. main用std::random_device+rand()生成salt,init srand+seccomp设置+write salt to file
2. All-Pwn-Red-Book App菜单:1.create note 2.list 3.edit 4.show 5.delete 6.exit
3. 三种Type对象:Type_A(0x18,vtable+password+val)+Type_B(0x40,vtable+password+note_content[0x30])+Type_C(0x30,vtable+password+content*+len+capacity)
4. 存放指针数量过大时重新申请chunk,旧chunk遗留note指针→UAF/double-free
5. vtable边界检查:((((vtable - vtable_TypeA) <<58) | ((unsigned__int64)(vtable - vtable_TypeA) >>6)) > 3)→ud1崩溃
6. 编辑note设置password需要满足sub_6C8A0:长度=32,所有字符'!'-'~',且至少3类(大写/小写/数字/特殊),且在特定haystack中memmem找不到
7. TypeA_edit调rand()%sub_6E750(obj_)作为val,受srand seed影响
8. 内容用base64解码后sub_6F930(256字节)做AES解密
9. sub_6C5A0生成key,sub_6E0F0存储
10. 关键漏洞:vec_push_back_ptr触发realloc时旧chunk被free,vec中ptr仍指向已释放chunk

## 关键 payload

```
All-Pwn-Red-Book app RCE
```

## 经验教训

std::vector push_back触发realloc会遗留旧指针,这是C++ PWN的经典漏洞;vtable boundary check通过差值编码((x<<58)|(x>>6))>3实现;密码学实现用C++的std::string+base64+AES+RSA要注意调用链。

## 标签

C++、stdlib、vtable、type-confusion、vector-realloc、cookie-check、srand-rand、base64-decode、AES-decrypt、rsa-cpp

## 参考来源

- https://www.ctfiot.com/278572.html
- 原文件：详解第九届XCTF国际网络攻防联赛总决赛0解PWN题.full.md

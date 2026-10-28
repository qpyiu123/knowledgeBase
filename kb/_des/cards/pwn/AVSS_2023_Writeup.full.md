---
title: "AVSS 2023 Writeup"
category: pwn
tags: ["AVSS", "pwn", "Parcel LaunchAnywhere", "broadcast GET_FLAG", "am broadcast", "kernel栈溢出"]
signals: ["AVSS 2023", "Parcel LaunchAnywhere", "broadcast GET_FLAG", "am broadcast", "kernel栈溢出", "prepare_kernel_cred", "commit_creds", "ret_to_user", "Android 7/8/9/10 arm64", "rce", "AVSS", "Parcel", "LaunchAnywhere", "broadcast"]
difficulty: hard
source: "https://www.ctfiot.com/132758.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AVSS 2023 Writeup

> 赛事：AVSS 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

AVSS 2023 移动安全+内核 — Parcel LaunchAnywhere + broadcast 触发 + Android 7/8/9/10 内核栈溢出 ROP + canary 泄漏 + mmap 共享内存 + cross-slab funcptr + msg_msg UAF。

## 攻击链

1. APP-VulnParcel: Parcel.writeInt + Bundle appendFrom 构造 Bundle[-1]=4c444e42 + VulnParcelable + Intent → LaunchAnywhere
2. APP-expReceiver: am broadcast -a com.avss.testreceiver.GET_FLAG + --es sms_body ''1'' + logcat -d | grep flag
3. Kernel-kStackOverflow: __NR_stackof 601 触发 my_ctu 栈溢出
4. 0x61 (pop rdi 错) + prepare_kernel_cred (0xFFFFFFC0000C1354) + 0x63 (ret) + commit_creds
5. 0x65 (skip) + ret_to_user + 0x67 (skip) + buf + get_root
6. Android 10: 先 leak canary (syscall len=0x108^0xdeadbeef 读 buf+0x100)
7. mmap 0xabcd00000 共享内存传 flag
8. Kernel-kHeapUserCopy: __NR_easyof 602 申请 slab + dmesg 读地址 + 改 funcptr
9. Kernel-kSysUAF: kfree 不置 NULL → msg_msg 复用 → UAF

## 关键 payload

```
Parcel Bundle 4c444e42 VulnParcelable LaunchAnywhere / am broadcast --es sms_body / 0x61 0x63 0x65 0x67 ROP / prepare_kernel_cred+commit_creds+ret_to_user / canary leak 0x100 / cross-slab funcptr / msg_msg UAF
```

## 经验教训

Parcel 数据可构造恶意 Bundle 触发 LaunchAnywhere;内核栈溢出 4 个字节 0x61/0x63/0x65/0x67 是 gadgets 占位;canary 在 Android 10 起必查,先 leak;UAF 经典走 msg_msg cross-cache。

## 标签

Parcel LaunchAnywhere、broadcast GET_FLAG、am broadcast、kernel栈溢出、prepare_kernel_cred、commit_creds、ret_to_user、Android 7/8/9/10 arm64、canary泄漏、mmap共享内存、cross-slab funcptr、msg_msg UAF、kStackOverflow、kHeapUserCopy、kSysUAF

## 参考来源

- https://www.ctfiot.com/132758.html
- 原文件：AVSS_2023_Writeup.full.md

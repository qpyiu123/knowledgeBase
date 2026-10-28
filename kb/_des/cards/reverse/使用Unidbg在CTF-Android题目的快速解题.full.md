---
title: "使用Unidbg在CTF-Android题目的快速解题"
category: reverse
tags: ["Unidbg Android CTF", "reverse", "Unidbg", "Android", "JNI", "libj.so"]
signals: ["Unidbg Android CTF 2024", "Unidbg", "Android", "JNI", "libj.so", "AbstractJni", "DvmClass", "JNIEnv", "callJniMethodObject", "reverse", "libj", "flag", "aapt", "dump"]
difficulty: medium
source: "https://www.ctfiot.com/163430.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 使用Unidbg在CTF-Android题目的快速解题

> 赛事：Unidbg Android CTF 2024 | 方向：reverse | 难度：medium | 工具：IDA

## 一句话总结

Unidbg 模拟 Android JNI 调用 libj.so 绕过动态分析，无需真机直接拿到 flag。

## 攻击链

1. aapt dump badging apk 看包名 + Activity
2. IDA 反编译 libj.so 看 JNI 函数 Java_an_droid_j_MainActivity_j/init/p
3. j() 返回 "FlagLostHelpMeGetItBack" 字符串 (内置常量, 长度 30 字节)
4. init(I) 接收 1738911344 返回 flag 字符串
5. p(I) 循环 99999 次混淆控制流
6. 用 Unidbg AndroidEmulatorBuilder.for32Bit() 创建模拟器
7. setProcessName("an.droid.j") 避免进程名校验
8. memory.setLibraryResolver(new AndroidResolver(23))
9. vm.createDalvikVM(File(apkFilePath)) 加载 APK
10. vm.loadLibrary(File(soFilePath), true) 加载 so
11. vm.setJni(this) 设置 AbstractJni
12. dvmClass.newObject(null).callJniMethodObject(emulator, "init(I)Ljava/lang/String;", temp)
13. System.out.println("flag{" + result + "}")

## 关键 payload

```
lesson4 + AndroidEmulatorBuilder + callJniMethodObject init(I)
```

## 经验教训

Unidbg 是 Android RE 的金钥匙：AndroidEmulatorBuilder + setProcessName + AndroidResolver + createDalvikVM + loadLibrary 五步走，setJni(this) 必加防报错。

## 标签

Unidbg、Android、JNI、libj.so、AbstractJni、DvmClass、JNIEnv、callJniMethodObject、模拟执行

## 参考来源

- https://www.ctfiot.com/163430.html
- 原文件：使用Unidbg在CTF-Android题目的快速解题.full.md

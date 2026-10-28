---
title: "ACTF flutter 逆向学习"
category: reverse
tags: ["ACTF", "reverse", "Flutter", "DartVM", "libapp.so", "blutter"]
signals: ["ACTF 2023", "Flutter", "DartVM", "libapp.so", "blutter", "objs.txt", "blutter_frida.js", "ida_script", "asm", "reverse", "ACTF", "IDA", "Frida", "hook"]
difficulty: medium
source: "https://www.ctfiot.com/169656.html"
tools: ["Frida", "IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ACTF flutter 逆向学习

> 赛事：ACTF 2023 | 方向：reverse | 难度：medium | 工具：Frida、IDA、Python

## 一句话总结

ACTF Flutter 逆向学习 — blutter 解析 DartVM 快照 + IDA 符号还原 + Frida hook 按钮回调 + 真机 root 动态调试。

## 攻击链

1. apk 改后缀 .zip 解压得 libapp.so (DartVM 快照)
2. reflutter/flutter 逆向助手对新 SDK 无效
3. 用 blutter 解析 libapp.so (pyelftools + capstone + libicu-dev)
4. 产物: objs.txt 对象池、blutter_frida.js、ida_script 符号还原、asm 反编译
5. AndroidKiller 改 AndroidManifest.xml 加 android:debuggable="true" + targetSdkVersion 27/28
6. adb install 重打包
7. adb push android_server64 /data/local/tmp/as + chmod 777
8. adb forward tcp:12345 tcp:12345
9. IDA 启动, 加载 libapp.so, run addName.py 还原符号
10. 看 main.dart 找按钮回调 (onChanged/onSubmitted)
11. Frida hook 输入/输出函数

## 关键 payload

```
blutter / IDA + addName.py / Frida hook 按钮回调 / targetSdkVersion 27/28 + debuggable=true / android_server64 root 真机
```

## 经验教训

Flutter 逆向核心是 DartVM 快照 (libapp.so);blutter 是开源首选工具;高 SDK 版本需降 targetSdkVersion 才能重签名;真机动态调试需 root + adb + android_server。

## 标签

Flutter、DartVM、libapp.so、blutter、objs.txt、blutter_frida.js、ida_script、asm、frida hook、IDA动态调试、root真机、AndroidKiller、debuggable、targetSdkVersion、adb push、onChanged、onSubmitted、按钮交互

## 参考来源

- https://www.ctfiot.com/169656.html
- 原文件：ACTF_flutter逆向学习.full.md

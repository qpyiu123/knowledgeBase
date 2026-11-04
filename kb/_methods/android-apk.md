---
title: 方法卡 · APK 静态排查与加固识别
category: mobile
tags: [android, apk, axml, dex, jadx, apktool]
signals:
  - APK 内有 classes.dex 和 AndroidManifest.xml
  - 反编译只看到几行代码，逻辑明显不在 dex 里
  - lib 目录下有 libjiagu、libshella 之类的 so
  - manifest 的 debuggable 或 exported 为 true
  - 题目要求改一处分支后重打包并通过签名校验
difficulty: hard
source: kb/mobile/apk-static-analysis.md, kb/mobile/frida-hook.md
tools: [python, jadx, apktool, apksigner, unzip]
updated: 2026-11-03
---

## 适用场景

拿到一个 APK，需要在**不运行**的前提下判断：是否加固、入口逻辑在哪、有没有 debuggable/exported 这类低门槛入口、
是否存在"改一个字节就能过"的校验分支。

典型信号：`classes.dex` 只有几百 KB 甚至几 KB、`lib/*/libjiagu*.so` 存在、`assets/` 下躺着 `.dex/.bin/.dat`。
反过来，如果反编译后能看到完整业务代码、dex 大小与功能量级一致，就按常规 jadx 阅读。

## 前置条件

- 只读排查用 `python` + `unzip -l` 即可；反编译需要 jadx（命令行版）与 apktool。
- 重打包需要 `apktool b` + `apksigner sign`，且设备/模拟器版本要与 targetSdk 匹配。
- 动态验证走 frida 时，frida-server 版本必须与 CLI 一致，否则连不上。

## 步骤

1. **先看容器**。`unzip -l app.apk`：确认有 `AndroidManifest.xml`（二进制 AXML）、`classes*.dex`、`lib/`、`assets/`。
2. **量 dex**。多个 `classesN.dex` 属正常分包；单 dex 很小而 APK 很大 → 主体逻辑被搬走或加密。
3. **找加固痕迹**。`libjiagu*`、`libshella*`、`libmobisec*`、`libDexHelper*` 等 so 出现即高度可疑；
   `assets/` 下的 `.dex/.bin/.dat/.jar` 往往是加密载荷，需先脱壳（frida-dexdump 或已知脱壳脚本）。
4. **读 manifest**。`debuggable="true"` 可直接 `run-as`/adb 起调试；`android:exported="true"` 的 Activity/Service 可被外部拉起；
   `usesCleartextTraffic` 与 INTERNET/READ_SMS 等权限说明题目的攻击面。
5. **反编译定位**。`jadx -d out app.apk`；加固样本改用 `apktool d` 看 smali，或先脱壳再反编译。
6. **改分支**。smali 里把 `if-eqz` 改成 `if-nez`（或反之）绕过判断，`apktool b` 重打包，`apksigner sign` 后重装验证。
7. **动态补一刀**。需要改运行时返回值时用 frida：`Java.perform` + `Interceptor.attach` 的 `onLeave` 里 `retval.replace(ptr(1))`；
   遇到反调试/反 frida（扫 `/proc/self/maps`、27042 端口）再改脚本或换端口。
8. 结论只写"证据 + 推断"：哪个文件/字段导致什么结论，避免只写"疑似加固"。

## 立即可用脚本

`kb/_methods/scripts/android_apk.py`

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe kb\_methods\scripts\android_apk.py --file app.apk
.venv\Scripts\python.exe kb\_methods\scripts\android_apk.py --file app.apk --strings
.venv\Scripts\python.exe kb\_methods\scripts\android_apk.py --selftest
```

- `--file`：任意 zip 容器，内部必须有 `AndroidManifest.xml`。
- `--strings`：附带打印 zip 条目清单，方便核对 assets/lib 布局。
- 输出：条目数、每个 dex 的大小与魔数是否正常、manifest 命中项（debuggable/exported/权限）、加固提示列表。
- 失败：非 zip、无 manifest、AXML 非二进制格式、文件不存在 → stderr 中文提示，退出码 2。
- `--selftest` 覆盖 zip 结构、加固特征、AXML 拒绝、缺文件四类断言，通过时打印 `selftest ok` 并退出 0。

## 手工示例

```
$ unzip -l app.apk | head
    16  AndroidManifest.xml
  9.8M  classes.dex
 2.1M  lib/arm64-v8a/libjiagu.so

$ python android_apk.py --file app.apk
条目 3，dex 1 个
  classes.dex  10276 字节  魔数正常
清单命中：debuggable
提示：发现加固库 lib/arm64-v8a/libjiagu.so（libjiagu）
```

边界：`--file _none.apk` → `失败：不是 zip 容器（APK 必须是 zip）：_none.apk`（退出码 2）。

## 失效场景

- **只做静态**：脚本不执行 APK，也不解壳；加固样本的 dex 内容它只能标记"可疑"，真正逻辑需脱壳后另查。
- **AXML 近似解析**：只读字符串池，不做属性→资源映射，拿不到"哪个 Activity 的 exported 是 true"这类结构化结论。
- **split APK / AAB**：分包 APK 的 `base.apk` 与配置分包分离，只看单个文件会误判资源缺失。
- **manifest 加密或自定义壳**：壳会把真正的 manifest 藏在 so 里，此时 AXML 解析失败属预期，需走脱壳或动态 dump。
- **签名/校验绕过**：脚本不重打包也不签名，改完 smali 必须自行 `apksigner`，否则 v2/v3 签名校验直接失败。

## 相关文档

- `kb/mobile/apk-static-analysis.md`：apktool/jadx/重打包的原始流程与 sed 改分支技巧。
- `kb/mobile/frida-hook.md`：动态 hook、反 frida 对抗、frida-dexdump 脱壳。
- `kb/_methods/pyjail.md`：脚本类题目里夹带 Python 逻辑时的阅读思路。

## 目录与收录说明

- 卡：`kb/_methods/android-apk.md`；脚本：`kb/_methods/scripts/android_apk.py`（纯标准库 zipfile/struct）。
- 覆盖 backlog 项 `android-apk`（category=mobile），证据来自 `kb/mobile/apk-static-analysis.md` 与 `kb/mobile/frida-hook.md`。
- 与已有卡无重叠；动态部分全部指向 `frida-hook.md`，本卡只负责静态判定。

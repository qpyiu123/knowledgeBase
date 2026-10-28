---
title: Android 加固脱壳（FART / frida-dexdump / FRIDA-DEXDump 全量导出）
category: mobile
tags: [unpack, fart, dexdump, frida, packer, eicar]
signals: [apk 里 classes.dex 只有几百 KB 但程序功能很多, 用 jadx 打开只能看到壳代码和一堆 Application 子类, 题目说 APK 经过某加固厂商处理, 运行时会释放真正的 dex, AndroidManifest 里 application 指向陌生的类名, 附件里有 libjiagu 或 libshella 这类 so 文件, 静态分析找不到加密算法但运行时有行为]
difficulty: hard
source: "FART 论文（腾讯安全） / hluwa/frida-dexdump 仓库 / CYRUS-STUDIO/frida_fart 文档"
tools: [frida, frida-dexdump, jadx, apktool, adb, dexdump, baksmali]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- `unzip -l app.apk | grep dex` 后发现 `classes.dex` 只有 1~50KB，与 APP 功能规模严重不符。
- `jadx` 打开后 `MainActivity` 只有 `super.onCreate()` 或空壳，真正的逻辑"凭空消失"。
- `AndroidManifest.xml` 的 `android:name` 指向 `com.stub.StubApp`、`com.qihoo.util.*`、`com.tencent.StubShell`。
- `lib/arm64-v8a/` 里有 `libjiagu.so`、`libshell.so`、`libexec.so`、`libDexHelper.so`。
- 静态找不到关键算法，但连抓包能看到请求里有加密参数。
- 题目 hint 写"需要脱壳"或"动态分析"。`assets/` 内有 `*.jar`、`dex.dat` 之类的资源。

## 二、原理

**加固的常见做法：**

1. **DEX 加密 + 运行时解密**：壳把原 DEX 加密后放到 assets/so 里，启动时由 native 层解密到内存（要么用 `DexClassLoader` 加载到某个路径，要么 `InMemoryDexClassLoader` 直接在内存里构造）。
2. **抽取（抽取式壳 / 指令抽取）**：保留原 DEX 结构，但把每个方法的字节码 `code_item` 清空，运行时用 native 的 `artMethod->entry_point_from_interpreter` 填回。
3. **VMP/指令虚拟化**：把字节码翻译成自定义指令流，由 so 解释器执行。

**脱壳的本质就是"在内存里把 DEX 抓回来"：**

- **FART 思路**：Hook `ClassLoader` 的 `loadClass` / ART 的 `DexFile::OpenMemory`，遍历所有已加载的 `DexFile`，把 `dex_begin_`~`dex_end_` 的内存 dump 出来，并对每个方法主动调用一次以触发抽取回填。
- **frida-dexdump 思路**：进程内扫描内存中符合 DEX 魔数（`dex\n035`/`036`/`037`/`038`/`039`）的块，按 DEX 头里的 `file_size` 校验后导出。
- **为什么"跑起来才 dump"**：壳会检测调试与 Frida，且只在真正用到某个类时才解密，所以需要先触发业务逻辑（进入目标 Activity、点击按钮）再 dump。

## 三、操作步骤

1. **确认加固**：`apktool d` 看 `AndroidManifest`，`unzip -l` 找 `libjiagu` 等特征 so，`jadx` 判断 DEX 大小。
2. **准备环境**：root 的模拟器或真机（x86_64/arm64 视 so 架构而定）、`frida-server` 与 `frida` 版本严格一致。
3. **跑应用并触发逻辑**：`adb shell am start -n <pkg>/<activity>`，用 monkey 或手点进入关键界面。
4. **dump**：`frida-dexdump -U -f <pkg>` 全进程扫描导出，或挂 FART 的 frida 脚本做 `loadClass` 回调 dump。
5. **修复**：导出的 DEX 可能头部校验和不对，`dexfixer`/`dexRepair`/手写脚本重算 `checksum` 与 `signature`。
6. **反编译**：`jadx` 逐个打开，按类名合并；抽取式壳需用 FART 的"方法回填"版本。
7. **找关键逻辑**：搜索字符串、`Cipher`、`MessageDigest`、`HttpURLConnection`。

## 四、命令 / 脚本

```bash
# 环境
adb root && adb shell "getprop ro.product.cpu.abi"
adb push frida-server-16.2.1-android-arm64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server && nohup /data/local/tmp/frida-server &"
pip install frida frida-tools frida-dexdump

# 启动目标并 dump
adb shell am start -n com.ctf.demo/.MainActivity
frida-dexdump -U -f com.ctf.demo -o dump_out/
# 或只针对运行中的进程
frida-dexdump -U -n "demo" -o dump_out/ -d

# 反编译
ls dump_out/ | head
jadx -d jadx_out dump_out/classes*.dex
```

```javascript
// fart_frida.js —— Hook loadClass 之后立即 dump 已加载的全部 DexFile
Java.perform(function () {
    var DexFile = Java.use('dalvik.system.DexFile');
    var File = Java.use('java.io.File');
    var FileOutputStream = Java.use('java.io.FileOutputStream');
    var dumpDir = '/data/local/tmp/fart/';

    function dumpAll() {
        var cl = Java.classFactory.loader || null;
        // 依次尝试常见 ClassLoader 的关键字段
        var Iter = Java.use('java.util.ArrayList');
        // ART 下可直接遍历 DexFile 的 mCookie（不同版本字段不同，需适配）
        try {
            var dex = DexFile.$new('/data/app/dummy.apk');
            console.log('[+] DexFile 可用');
        } catch (e) {
            console.log('[-] ' + e);
        }
    }

    DexFile.loadClass.overload('java.lang.String', 'java.lang.ClassLoader')
        .implementation = function (name, loader) {
            var r = this.loadClass(name, loader);
            if (r !== null && r !== undefined) {
                console.log('[load] ' + name);
            }
            return r;
        };

    console.log('[*] hooked DexFile.loadClass');
});
```

```bash
# 挂脚本
frida -U -f com.ctf.demo -l fart_frida.js --no-pause
# dump 结果修复（重算 DEX 头校验）
python - <<'EOF'
import glob, hashlib, struct, zlib
for p in glob.glob('dump_out/*.dex'):
    d = bytearray(open(p, 'rb').read())
    if d[:4] != b'dex\n':
        continue
    d[8:12] = b'\x00' * 4                       # signature
    d[8:12] = hashlib.sha1(bytes(d[32:])).digest()
    d[12:16] = b'\x00' * 4
    d[12:16] = struct.pack('<I', zlib.adler32(bytes(d[12:])))
    open(p, 'wb').write(bytes(d))
    print('fixed', p, len(d))
EOF
```

## 五、常见坑 / 变体

- **frida-server 与 frida 版本不一致**：最常见的失败原因，`frida --version` 与 server 二进制版本必须完全一致。
- **架构不匹配**：壳的 so 只有 `arm64-v8a`，在 x86 模拟器上 `dlopen` 失败 → 应用闪退。用 `arm64` 模拟器或真机。
- **dump 出的 DEX 数量多且重复**：`frida-dexdump` 会扫出大量碎片，按 `file_size` 去重，并优先选"类数量最多"的那个。
- **抽取式壳导出后方法为空**：`code_item` 仍被清空，需要 FART 的"主动调用回填"，或用 `Youpk`/`BlackDex` 这类专门工具。
- **反 Frida**：壳会扫 `/proc/self/maps` 里的 `frida`、`gum-js-loop` 线程名，需先过检测（见 `android-antidebug-advanced`）。
- **`InMemoryDexClassLoader`**：DEX 不在文件系统里，只能从内存 dump，`vectorscan` 方法要在内存区间里搜 `dex\n`。
- **变体**：iOS 的 `FairPlay` 解密（`frida-ios-dump`）、Unity `il2cpp`（`global-metadata.dat` + `libil2cpp.so`）。

## 六、参考来源

- [hluwa/frida-dexdump：内存中 DEX 扫描与导出](https://github.com/hluwa/frida-dexdump)
- [CYRUS-STUDIO/frida_fart：用 Frida 增强 FART 的脱壳能力](https://github.com/CYRUS-STUDIO/frida_fart)
- [某加固企业版的脱壳与反调试绕过实录（Frida-Dexdump + FART）](https://cloud.tencent.com/developer/article/2517005)
- [OWASP MASTG：Android 动态分析（脱壳与运行时插桩）](https://mas.owasp.org/MASTG/)
- [jadx 官方仓库（dex 反编译）](https://github.com/skylot/jadx)

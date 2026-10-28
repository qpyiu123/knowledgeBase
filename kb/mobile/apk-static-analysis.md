---
title: APK 静态分析（apktool / jadx 全流程）
category: mobile
tags: [APK, apktool, jadx, AndroidManifest, smali, 静态分析]
signals: [附件是 .apk, 需要看清 AndroidManifest 与权限, 需要读 Java/Kotlin 逻辑, smali 里有核心判断, 需要改包重签]
difficulty: easy
source: "CTF-Wiki Android 静态分析 / OWASP MASTG / jadx 与 apktool 文档"
tools: [apktool, jadx, dex2jar, jd-gui, apkanalyzer, aapt2, bytecode-viewer]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.apk`，题面要求「找出 flag」「分析逻辑」。
- 需要知道 `package`、`launchable-activity`、`exported` 组件。
- Java 层就能看到完整校验逻辑（没有 native 层）。
- 需要改 smali 里的条件跳转后重打包并让设备装上（绕过校验）。

## 二、原理

APK 是 zip，静态分析三个层次：

| 层次 | 产物 | 工具 |
|---|---|---|
| 资源/清单 | 二进制 AXML → 可读 XML | `apktool d`、`aapt2 dump` |
| Dalvik 字节码 | smali（可读可改） | `apktool d`（smali 目录）|
| Java 源码 | 近似原始 Java/Kotlin | `jadx`、`dex2jar` + JD-GUI |

**为什么 apktool 与 jadx 都要用**：
- `apktool` 解码资源、保留 smali，是**改包重打包**的必经路径。
- `jadx` 直接出 Java 源码，读逻辑快得多，但不保证可回编译。

`AndroidManifest.xml` 关键项：

```xml
<manifest package="com.example.chall">
  <uses-permission android:name="android.permission.INTERNET"/>
  <application android:debuggable="false" android:allowBackup="true">
    <activity android:name=".MainActivity" android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
      </intent-filter>
    </activity>
    <provider android:name=".FlagProvider" android:exported="true" .../>
  </application>
</manifest>
```

## 三、checksec 判读与利用思路

移动端「checksec」等价项：

| 检查 | 命令 | 含义 |
|---|---|---|
| 是否 debuggable | `apkanalyzer manifest print x.apk \| grep debuggable` | 可被 `am set-debug-app` 调试 |
| 签名 | `apksigner verify -v x.apk` | 是否 v2/v3 签名 |
| 加固 | `unzip -l` 看 classes.dex 大小与 `libjiagu*.so` | 是否梆梆/爱加密壳 |
| native 库 | `unzip -l \| grep "lib/"` | 核心逻辑可能在 so |
| 证书指纹 | `keytool -printcert -jarfile x.apk` | 校验是否依赖签名 |

分析流程：

```text
1. apk 基本信息（包名/入口/权限）
2. jadx 读 Java 层，grep flag/check/decrypt
3. 找不到就看 assets / res/raw / so
4. 需要改逻辑时回到 apktool 的 smali
```

## 四、可直接运行的 exp 脚本

```bash
#!/bin/bash
# APK 静态分析一键流程
set -e
APK=${1:-./chall.apk}
OUT=./apk_static
rm -rf "$OUT"; mkdir -p "$OUT"

echo "===== 1. 基本信息 ====="
aapt2 dump badging "$APK" 2>/dev/null | head -20 || echo "[!] 无 aapt2，跳过"
file "$APK"

echo "===== 2. Manifest ====="
apkanalyzer manifest print "$APK" 2>/dev/null | head -60

echo "===== 3. 签名与加固指示 ====="
apksigner verify -v "$APK" 2>/dev/null | head -10 || echo "[!] 无 apksigner"
unzip -l "$APK" | grep -Ei "lib/|\.so$|dex" | head -30

echo "===== 4. apktool 解包（保留 smali 与资源） ====="
apktool d -f -o "$OUT/apktool" "$APK" >/dev/null
ls "$OUT/apktool" | head

echo "===== 5. jadx 出 Java 源码 ====="
jadx -q -d "$OUT/java" --show-bad-code "$APK"
find "$OUT/java" -name "*.java" | wc -l

echo "===== 6. 关键字扫描 ====="
grep -rniE "flag|correct|wrong|secret|encrypt|decrypt|check" "$OUT/java" \
  --include=*.java | head -40

echo "===== 7. assets / res/raw 里的可疑文件 ====="
unzip -l "$APK" | grep -E "assets/|res/raw/" | head -30
```

```python
#!/usr/bin/env python3
# 用 androguard 做更结构化的静态分析（无需 apktool）
from androguard.core.apk import APK
from androguard.core.dex import DEX
import sys, pathlib

APK_PATH = sys.argv[1] if len(sys.argv) > 1 else "./chall.apk"

def analyze(path):
    apk = APK(path)
    print(f"[*] package = {apk.get_package()}")
    print(f"[*] main activity = {apk.get_main_activity()}")
    print(f"[*] version = {apk.get_androidversion_name()}")
    print(f"[*] debuggable = {apk.is_debuggable()}")
    print(f"[*] allow_backup = {apk.get_attribute_value('application', 'allowBackup')}")

    perms = sorted(apk.get_permissions())
    print(f"[*] permissions ({len(perms)}): {perms[:10]}")

    # 导出组件
    for tag in ("activity", "service", "receiver", "provider"):
        for name in apk.get_all_attribute_value(tag, "name"):
            if name:
                print(f"    {tag}: {name}")

    # 字符串里找可疑内容
    for dex in apk.get_all_dex():
        d = DEX(dex)
        for s in d.get_strings():
            sv = s.get()
            low = (sv or "").lower()
            if any(k in low for k in ("flag{", "ctf{", "correct", "wrong")):
                print(f"[+] string: {sv[:100]}")

if __name__ == "__main__":
    analyze(APK_PATH)
```

改 smali 重打包（绕过一个 `if` 校验）：

```bash
# 1) 修改 smali：把 if-eqz 改成 if-nez（或直接注释掉跳转）
#    文件路径：apktool_out/smali/com/example/chall/MainActivity.smali
sed -i 's/if-eqz v0, :cond_0/if-nez v0, :cond_0/' \
    apk_static/apktool/smali/com/example/chall/MainActivity.smali

# 2) 回编译
apktool b apk_static/apktool -o patched.apk

# 3) 重签名（v2 需 apksigner，否则 Android 7+ 装不上）
keytool -genkey -keystore ks.jks -keyalg RSA -alias a -storepass 123456 -keypass 123456 -dname "CN=x"
apksigner sign --ks ks.jks --ks-pass pass:123456 patched.apk
apksigner verify patched.apk

# 4) 安装
adb install -r patched.apk
```

## 五、常见坑 / 变体

- **`apktool` 回编译失败**：常见于 Kotlin 协程/新框架的 smali 指令，用 `apktool --use-aapt2` 或最新版。
- **重签后闪退**：应用有签名校验（见「签名校验绕过」篇），需同时 patch 校验逻辑。
- **加固壳**：`classes.dex` 很小、有 `libjiagu.so`/`libsecmain.so`，静态分析只能看到壳，需要动态脱壳。
- **多 dex**：`classes2.dex`、`classes3.dex` 里有逻辑，jadx 会自动合并，手工 `dex2jar` 时要逐个处理。
- **资源混淆（AndResGuard）**：`res/` 下文件名变成 `a/b/c.xml`，用 jadx 的 resource 视图或 `arsc` 解析。
- **Kotlin 协程/内联函数**：反编译出的 Java 与源码差异大，结合字节码/smali 看。
- **`exported=true` 的组件**：往往就是攻击入口（`adb shell am start -n pkg/.Activity --es key value`）。

## 六、参考来源

- [CTF-Wiki: Android 简单静态分析（Java 层例子）](https://ctf-wiki.org/android/basic_reverse/static/java-example/)
- [CTF-Wiki: Android 关键代码定位](https://ctf-wiki.org/android/basic_reverse/android_code_location/)
- [OWASP MASTG: Android 静态分析技术](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0014/)
- [jadx 官方仓库](https://github.com/skylot/jadx)
- [apktool 官方文档](https://apktool.org/docs/install)
- [dex2jar 官方仓库](https://github.com/pxb1988/dex2jar)
- [androguard（Python APK/DEX 分析库）](https://github.com/androguard/androguard)
- [HackTricks: Android App Pentesting](https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting/index.html)

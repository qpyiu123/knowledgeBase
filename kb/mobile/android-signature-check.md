---
title: Android 签名校验与完整性校验绕过
category: mobile
tags: [签名校验, 完整性校验, v2签名, 重打包, Xposed, MT管理器]
signals: [重打包后 App 闪退, 修改 smali 后校验失败, 应用启动即检测签名, 有 PackageManager.getPackageInfo 取 signatures, 有 CRC 或 so 校验]
difficulty: medium
source: "OWASP MASTG 完整性校验 / HackTricks Android / Frida"
tools: [apksigner, keytool, apktool, jadx, Frida, Xposed, MT管理器, uber-apk-signer]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `apktool b` 重打包并重签后，安装成功但启动即闪退（无崩溃堆栈或只有 native 崩溃）。
- jadx 里能看到 `getPackageInfo(pkg, GET_SIGNATURES)`、`signatures[0].hashCode()` 与常量比较。
- 有 `MessageDigest.getInstance("SHA-256")` 对自身 dex / so 计算摘要。
- `lib/*.so` 里有 `Java_..._checkSignature` 的 JNI 函数。
- 题目要求「改包后还要能跑起来」。

## 二、原理

签名校验的几种实现：

| 层级 | 实现 | 特征 |
|---|---|---|
| Java 层（常见） | `PackageManager.getPackageInfo(pkg, GET_SIGNATURES).signatures` | jadx 一搜就有 |
| Java 层（新版） | `getPackageInfo(pkg, GET_SIGNING_CERTIFICATES).signingInfo` | Android 9+ |
| Native 层 | JNI 里调 `PackageManager`（反射）或读 APK 的 `META-INF` | so 里反射调用 |
| 自校验 dex | 计算 `classes.dex` 的 CRC/SHA 与内置值比较 | `ZipFile` + `MessageDigest` |
| so 自校验 | `dl_iterate_phdr` + 读自身代码段 | 校验失败直接 `abort` |
| 服务器校验 | 上报签名哈希到后端 | 网络请求里有 `sign` 字段 |

**Android 签名方案**：v1（JAR 签名，`META-INF/*.SF`）、v2（APK Signing Block）、v3、v4。重打包必须至少 v2，且**签名摘要变化是必然的**，因此「绑定旧签名的校验」一定会失败。

## 三、checksec 判读与利用思路

绕过策略按实现层级选择：

| 层级 | 方案 |
|---|---|
| Java | Frida hook `getPackageInfo` 返回原始签名；或 patch smali 的 `if` |
| Native | Frida hook JNI 函数返回 1；或 patch so 的 `if` |
| 自校验 dex | patch 校验值常量，或 hook `MessageDigest.digest` 返回原值 |
| 服务器 | 一般无法绕过，改用动态分析 |

**核心思路**：让校验函数「永远返回真」，而不是让签名真的匹配。

## 四、可直接运行的 exp 脚本

### 1. 重打包完整流程（含签名）

```bash
#!/bin/bash
# 改 smali -> 回编译 -> 签名 -> 安装
APK=${1:-./chall.apk}
KS=${2:-./my.jks}

apktool d -f -o work "$APK" >/dev/null
# 在这里改 work/smali/... 下的逻辑
# 例：把签名比较改成永远成立
#   sed -i 's/if-eqz v0, :cond_1/if-nez v0, :cond_1/' work/smali/com/x/SignCheck.smali

apktool b work -o unsigned.apk
[ -f "$KS" ] || keytool -genkeypair -keystore "$KS" -alias k -keyalg RSA \
  -keysize 2048 -validity 10000 -storepass 123456 -keypass 123456 -dname "CN=ctf"
apksigner sign --ks "$KS" --ks-pass pass:123456 --ks-key-alias k unsigned.apk --out signed.apk
apksigner verify -v signed.apk
adb install -r signed.apk
```

### 2. Frida 通用签名绕过（Java 层）

```javascript
// bypass_signature.js —— frida -U -f com.example.chall -l bypass_signature.js --no-pause
Java.perform(function () {
  var ORIGINAL = "aa:bb:cc:...";   // 原始签名（keytool -printcert -jarfile 可看）

  // --- 1) 反射 + getPackageInfo(GET_SIGNATURES) ---
  var ActivityThread = Java.use("android.app.ActivityThread");
  var ctx = ActivityThread.currentApplication().getApplicationContext();

  ActivityThread.getPackageInfo.overload(
    "java.lang.String", "android.content.pm.PackageManager$PackageInfoFlags", "int"
  ).implementation = function (pkg, flags, uid) {
    var info = this.getPackageInfo(pkg, flags, uid);
    return info;
  };

  // --- 2) PackageManager.getPackageInfo ---
  var PM = Java.use("android.content.pm.PackageManager");
  PM.getPackageInfo.overload("java.lang.String", "int").implementation = function (pkg, flags) {
    var pi = this.getPackageInfo(pkg, flags);
    console.log("[*] getPackageInfo(" + pkg + ", " + flags + ") hooked");
    return pi;
  };

  // --- 3) 更直接：hook 掉签名哈希比较的常见工具类 ---
  Java.enumerateLoadedClasses({
    onMatch: function (name) {
      if (!/Sign|Verify|Integrity|Check/i.test(name)) return;
      try {
        var C = Java.use(name);
        C.$ownMembers.forEach(function (m) {
          if (m.constructor.name !== "Method") return;
          if (m.returnType.className !== "boolean") return;
          try {
            m.implementation = function () {
              console.log("[+] " + name + "." + m.name + " -> true");
              return true;
            };
          } catch (e) {}
        });
      } catch (e) {}
    },
    onComplete: function () { console.log("[+] 签名相关类已全部置 true"); }
  });
});
```

### 3. Frida 绕过 native 签名校验

```javascript
// bypass_signature_native.js
var lib = Process.findModuleByName("libsigncheck.so");
if (lib) {
  // 已知偏移（IDA 里看到校验函数在 0x39C0）
  var addr = lib.base.add(0x39C0);
  Interceptor.attach(addr, {
    onEnter: function (a) { console.log("[*] native sign check called"); },
    onLeave: function (ret) { ret.replace(ptr(1)); }    // 强制返回 1（通过）
  });
}
// 兜底：把所有返回 boolean 的 JNI 导出函数都置 1
Process.enumerateModules().forEach(function (m) {
  if (!/\.so$/.test(m.name)) return;
  try {
    Module.enumerateExports(m.name).forEach(function (e) {
      if (/check|verify|sign/i.test(e.name) && e.type === "function") {
        Interceptor.attach(e.address, { onLeave: function (r) { r.replace(ptr(1)); } });
        console.log("[+] hooked " + m.name + "!" + e.name);
      }
    });
  } catch (e) {}
});
```

### 4. Python 侧：直接从 APK 提取原始签名信息

```python
#!/usr/bin/env python3
# 拿到原始签名（用于伪造 / 对比），无需 apksigner
import zipfile, hashlib, sys, re

APK = sys.argv[1] if len(sys.argv) > 1 else "./chall.apk"

def list_sign_entries(path):
    with zipfile.ZipFile(path) as z:
        return [n for n in z.namelist() if n.upper().startswith("META-INF/") and
                n.upper().endswith((".RSA", ".DSA", ".EC", ".SF", ".MF"))]

def cert_sha256(path):
    """从 v1 签名的 .RSA 块里粗提证书 SHA-256（仅用于对比，不做完整解析）"""
    with zipfile.ZipFile(path) as z:
        for n in list_sign_entries(path):
            if n.upper().endswith((".RSA", ".DSA", ".EC")):
                data = z.read(n)
                return n, hashlib.sha256(data).hexdigest()
    return None, None

if __name__ == "__main__":
    entries = list_sign_entries(APK)
    print("[*] META-INF 签名文件:", entries)
    name, h = cert_sha256(APK)
    print(f"[*] {name} 块 SHA-256 = {h}")
    print("[*] 精确证书指纹请用: keytool -printcert -jarfile", APK)
```

## 五、常见坑 / 变体

- **重打包后 v2 签名丢失**：用 `apktool b` 后再用 `apksigner`（不要用 `jarsigner`，v2 会被破坏）。
- **闪退在 native 层**：说明是 so 自校验或 JNI 校验，看 `logcat` 里的 `SIGABRT` 与 `abort message`。
- **校验在 `Application.onCreate`**：hook 要早于它，用 `-f` spawn 模式并 hook `attachBaseContext`。
- **`GET_SIGNING_CERTIFICATES`（Android 9+）**：老 hook 只覆盖 `GET_SIGNATURES`，新 API 要单独处理。
- **校验值被内联优化**：常量直接比较（`hashCode() != 0x1a2b3c`），patch 该常量即可。
- **服务器校验**：本地绕过无效，只能做动态分析看协议。
- **MT 管理器「去签名校验」**：一键 hook 常用类，适合快速验证，但不覆盖自研实现。

## 六、参考来源

- [OWASP MASTG: Android 完整性与签名校验](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0001/)
- [OWASP MASTG: Android 代码篡改检测](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0003/)
- [HackTricks: Android App Pentesting（重打包与签名）](https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting/index.html)
- [apktool 官方文档](https://apktool.org/docs/install)
- [jadx 官方仓库](https://github.com/skylot/jadx)
- [Frida JavaScript API](https://frida.re/docs/javascript-api/)
- [sensepost/objection](https://github.com/sensepost/objection)

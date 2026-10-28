---
title: Android SSL Pinning 绕过
category: mobile
tags: [SSL Pinning, 证书固定, Frida, objection, mitmproxy, 抓包]
signals: [mitmproxy 抓不到 https 流量, 代理装了证书仍报 SSLHandshakeException, 应用提示网络错误但 http 正常, 有 trustmanager / certificate pinner, okhttp 的 CertificatePinner]
difficulty: medium
source: "OWASP MASTG Bypassing Certificate Pinning / Frida CodeShare / objection"
tools: [frida, objection, mitmproxy, apk-mitm, reflutter, Xposed]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 设备代理指向 mitmproxy 后，App 请求全部失败或只抓到 http。
- logcat 里出现 `javax.net.ssl.SSLHandshakeException: java.security.cert.CertPathValidatorException`。
- jadx 里看到 `CertificatePinner.Builder().add("api.x.com", "sha256/...")`。
- so 里有 `SSL_CTX_set_verify` 或 BoringSSL 的 `X509_VERIFY_PARAM_set1_host` 调用。
- 题目要求「抓包看 flag 在响应里」。

## 二、原理

正常 TLS 校验：系统信任链（CA）验证服务端证书。**Pinning** 在此之上额外固定：

| 层 | 实现 | 绕过点 |
|---|---|---|
| Java 默认 TrustManager | `X509TrustManager.checkServerTrusted` | hook 后直接 return |
| OkHttp `CertificatePinner` | `check(String, List<Certificate>)` | 覆盖为 no-op |
| Android 7+ 网络配置 | `network_security_config.xml` 的 `<pin-set>` | 改 config 或 hook 底层 |
| Native (BoringSSL) | `SSL_CTX_set_custom_verify` / `SSL_get_verify_result` | 需要 inline hook |
| 双向认证（mTLS） | `KeyManager` / 客户端证书 | 需要拿到客户端证书文件 |

关键点：**Android 7.0+ 后，用户安装的 CA 证书默认不被 App 信任**（只信任系统 CA），所以要先解决这个前提。

## 三、checksec 判读与利用思路

判读与绕过层级选择：

```text
1. 先确认能否抓到明文 http        （网络通路没问题）
2. 代理 + 系统 CA 证书 → 仍失败？  （存在 pinning）
3. jadx 搜 CertificatePinner / TrustManager / X509
4. 有就 Java 层 hook；没有就上 native（Frida + BoringSSL）
```

| 场景 | 方案 |
|---|---|
| 普通 OkHttp pinning | `objection -g pkg android sslpinning disable` |
| 自研 TrustManager | Frida 覆盖 `checkServerTrusted` |
| Native pinning | Frida hook `SSL_CTX_set_verify` / `SSL_get_verify_result` |
| 无法 attach | `apk-mitm` 重打包修改（需能重签且无签名校验）|

## 四、可直接运行的 exp 脚本

### 1. 环境（mitmproxy + 系统证书）

```bash
# 1) 启动代理
mitmproxy -p 8080                      # 或 mitmweb -p 8080

# 2) 下载 mitmproxy CA（设备浏览器访问 mitm.it，或直接 push）
adb shell "su -c 'mount -o rw,remount /'"
adb push ~/.mitmproxy/mitmproxy-ca-cert.pem /sdcard/
# 证书文件名必须是 <hash>.0，hash 用 openssl 计算
HASH=$(openssl x509 -inform PEM -subject_hash_old -in ~/.mitmproxy/mitmproxy-ca-cert.pem | head -1)
adb shell "su -c 'cp /sdcard/mitmproxy-ca-cert.pem /system/etc/security/cacerts/$HASH.0'"
adb shell "su -c 'chmod 644 /system/etc/security/cacerts/$HASH.0'"
adb reboot

# 3) 设置全局代理
adb shell "settings put global http_proxy 127.0.0.1:8080"
```

### 2. objection 一行绕过

```bash
pip install objection
objection -g com.example.chall explore -s "android sslpinning disable"
# 或在已进入的 shell 里：
#   android sslpinning disable
#   android root disable
```

### 3. Frida 全面 hook（Java + OkHttp + TrustManager）

```javascript
// ssl_bypass.js —— frida -U -f com.example.chall -l ssl_bypass.js --no-pause
Java.perform(function () {
  // --- 1) TrustManager：让所有证书都通过 ---
  var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
  var SSLContext = Java.use("javax.net.ssl.SSLContext");

  var TrustAll = Java.registerClass({
    name: "com.frida.TrustAll",
    implements: [X509TrustManager],
    methods: {
      checkClientTrusted: function (chain, authType) {},
      checkServerTrusted: function (chain, authType) {},
      getAcceptedIssuers: function () { return []; }
    }
  });

  var TrustManagers = [TrustAll.$new()];
  var sslContext = SSLContext.getInstance("TLS");
  sslContext.init(null, TrustManagers, null);
  console.log("[+] TrustManager replaced with trust-all");

  // --- 2) OkHttp CertificatePinner ---
  try {
    var Pinner = Java.use("okhttp3.CertificatePinner");
    Pinner.check.overload("java.lang.String", "java.util.List")
      .implementation = function (host, peer) {
        console.log("[+] bypass pinning for " + host);
      };
    Pinner.check$okhttp.overload("java.lang.String", "kotlin.jvm.functions.Function0")
      .implementation = function (host, f) { console.log("[+] check$okhttp " + host); };
  } catch (e) { console.log("[-] okhttp3 不存在（可能被混淆）"); }

  // --- 3) 常见自研校验类 ---
  Java.enumerateLoadedClasses({
    onMatch: function (name) {
      if (!/Trust|Pin|Cert|Seal/i.test(name)) return;
      try {
        var C = Java.use(name);
        C.$ownMembers.forEach(function (m) {
          if (m.constructor.name !== "Method") return;
          if (/check|verify|validate/i.test(m.name) &&
              m.returnType.className === "boolean") {
            try { m.implementation = function () { return true; }; } catch (e) {}
          }
        });
      } catch (e) {}
    },
    onComplete: function () { console.log("[+] 自研校验类扫描完成"); }
  });
});
```

### 4. native 层（BoringSSL）绕过

```javascript
// ssl_bypass_native.js
['libssl.so', 'libboringssl.so', 'libconscrypt_jni.so'].forEach(function (mod) {
  var m = Process.findModuleByName(mod);
  if (!m) return;
  console.log("[*] module " + mod + " @ " + m.base);

  ['SSL_CTX_set_verify',
   'SSL_CTX_set_custom_verify',
   'SSL_get_verify_result'].forEach(function (fn) {
    var p = Module.findExportByName(mod, fn);
    if (!p) return;
    Interceptor.attach(p, {
      onEnter: function (args) { console.log("[*] " + fn + " called"); },
      onLeave: function (ret) {
        if (fn === 'SSL_get_verify_result') ret.replace(ptr(0));   // X509_V_OK
      }
    });
  });

  // 关掉证书验证回调
  var setVerify = Module.findExportByName(mod, 'SSL_CTX_set_verify');
  if (setVerify) {
    Interceptor.replace(setVerify, new NativeCallback(function (ctx, mode, cb) {
      return 0;   // 什么都不设 = 不验证
    }, 'void', ['pointer', 'int', 'pointer']));
  }
});
```

## 五、常见坑 / 变体

- **Android 7+ 不信任用户 CA**：必须把 CA 装进 `/system/etc/security/cacerts`（需 root + remount），或用 Frida 绕过 TrustManager。
- **OkHttp 版本差异**：OkHttp 4.x 的 `check` 签名变 Kotlin 版（`Function0`），overload 要分开写。
- **Ktor/Retrofit + Conscrypt**：走 `ConscryptEngine`，需要 hook `Conscrypt` 的 `SSLParametersImpl`。
- **Flutter 应用**：不使用 JVM TrustManager，需 `reFlutter` 重打包或 hook `SSL_verify_peer_cert`。
- **mTLS**：还需要客户端证书，从 App 的 `raw/` 或 `assets/` 里找 `.p12`。

## 六、参考来源

- [OWASP MASTG: Bypassing Certificate Pinning](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0012/)
- [Frida CodeShare: frida-multiple-unpinning](https://codeshare.frida.re/@akabe1/frida-multiple-unpinning/)
- [Frida CodeShare: universal Android SSL pinning bypass](https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/)
- [HTTP Toolkit: frida-interception-and-unpinning](https://github.com/httptoolkit/frida-interception-and-unpinning)
- [sensepost/objection](https://github.com/sensepost/objection)
- [mitmproxy 官方](https://github.com/mitmproxy/mitmproxy)
- [apk-mitm（重打包修改网络配置）](https://github.com/shroudedcode/apk-mitm)
- [Frida JavaScript API](https://frida.re/docs/javascript-api/)
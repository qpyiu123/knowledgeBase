---
title: Android 网络流量（系统 CA 安装、SSL Pinning 各类实现）
category: mobile
tags: [burp, ca-cert, ssl-pinning, okhttp, flutter, trustmanager]
signals: [抓包工具里所有请求都显示 handshake failed 或者连接被重置, 需要把 burp 的证书装进系统目录, 应用使用了 OkHttp 的 CertificatePinner, 应用是 Flutter 或者 Unity 写的抓不到明文, 网络库是 boringssl 而不是系统自带的, 题目要求在移动端抓包拿到某个接口的返回]
difficulty: medium
source: "Android 官方 Network Security Config 文档 / OkHttp CertificatePinner 文档 / OWASP MASTG 网络拦截章节"
tools: [mitmproxy, burp, frida, objection, reqable, adb, magisk]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- Burp/mitmproxy 装上之后所有请求报 `client TLS handshake failed` 或 `Certificate verification failed`。
- 应用是 Android 7+（targetSdk ≥ 24），用户 CA 不被信任，必须装到系统证书。
- 请求地址里能看到内网域名，但返回永远是空。
- 应用体积大且带 `libflutter.so`，说明是 Flutter（不走系统 CA，BoringSSL 内置）。
- 用的是 OkHttp，且代码里出现 `CertificatePinner.Builder()`。
- 走 QUIC/HTTP3（UDP 443），普通代理抓不到。

## 二、原理

**为什么默认抓不到：**

1. **Android 7+**：`targetSdkVersion ≥ 24` 时，默认只信任系统 CA，用户手动装的证书对 app 无效。要么改 `network_security_config` 允许 user CA，要么把证书塞进 `/system/etc/security/cacerts`。
2. **SSL Pinning**：应用把证书/公钥哈希硬编码，校验时 `cert.hashCode()` 必须等于预期值，换证书直接抛校验异常。实现层：
   - `OkHttp` 的 `CertificatePinner`；
   - 自定义 `TrustManager`/`X509TrustManager`；
   - `HostnameVerifier`；
   - 原生层直接校验（BoringSSL + `SSL_CTX_set_custom_verify`）；
   - Flutter 的 `SecurityContext`（Dart 层）。
3. **TLS 指纹**：有的服务端只接受特定 ClientHello，Burp 的 Java TLS 栈会被识别，需用 `uTLS` 或 `mitmproxy` 加 BoringSSL。

## 三、操作步骤

1. **先装系统 CA**：
   - 旧版 Android（<14）直接推 `/system/etc/security/cacerts/<hash>.0`（root）。
   - Android 14 起系统 CA 在 APEX 里，需 Magisk 模块 `AlwaysTrustUserCerts` 或 `Move Certificates`。
2. **测是否能抓**：抓一个 HTTPS 请求，看是否成功。
3. **失败则判断 pinning 类型**：`jadx` 搜 `CertificatePinner`、`TrustManager`、`checkServerTrusted`；`strings libflutter.so` 判断 Flutter。
4. **逐层 hook**：
   - OkHttp：hook `CertificatePinner.check`。
   - TrustManager：hook `X509TrustManager.checkServerTrusted` 置空。
   - Flutter：hook BoringSSL 的 `ssl_verify_cert_chain` 返回 1。
5. **验证**：重新抓包，看明文是否出现。

## 四、命令 / 脚本

```bash
# 1) 生成系统 CA（从 burp 导出的 der 转 pem，计算 subject_hash_old）
openssl x509 -inform DER -in burp.der -out burp.pem
HASH=$(openssl x509 -inform PEM -subject_hash_old -in burp.pem | head -1)
cp burp.pem $HASH.0

# 2) 推到系统证书目录（需 root + /system 可写）
adb root; adb remount
adb push $HASH.0 /system/etc/security/cacerts/
adb shell "chmod 644 /system/etc/security/cacerts/$HASH.0"
adb reboot

# 3) 代理设置
adb shell settings put global http_proxy 127.0.0.1:8080
adb reverse tcp:8080 tcp:8080

# 4) 抓包
mitmproxy -p 8080 --set ssl_insecure=true
```

```javascript
// bypass-pinning.js —— 覆盖 OkHttp / TrustManager / HostnameVerifier
Java.perform(function () {
    // OkHttp 3/4
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation =
            function (host, certs) {
                console.log('[pinner] ' + host);
                return;
            };
    } catch (e) { console.log('[-] okhttp: ' + e); }

    // 通用 TrustManager
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        var TrustManager = Java.registerClass({
            name: 'com.ctf.TrustAll',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function () {},
                checkServerTrusted: function () {},
                getAcceptedIssuers: function () { return []; }
            }
        });
        var ctx = SSLContext.getInstance('TLS');
        ctx.init(null, [TrustManager.$new()], null);
        SSLContext.getInstance.overload('java.lang.String').implementation = function (p) {
            return ctx;
        };
    } catch (e) { console.log('[-] tm: ' + e); }

    // HostnameVerifier
    try {
        var HostnameVerifier = Java.use('javax.net.ssl.HostnameVerifier');
        var Verifier = Java.registerClass({
            name: 'com.ctf.Verifier',
            implements: [HostnameVerifier],
            methods: { verify: function () { return true; } }
        });
        var OkHostnameVerifier = Java.use('okhttp3.internal.tls.OkHostnameVerifier');
        OkHostnameVerifier.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession')
            .implementation = function () { return true; };
    } catch (e) { console.log('[-] hv: ' + e); }
});
```

```javascript
// Flutter（BoringSSL）绕过：在 libflutter.so 里找 ssl_cert_verify
function hookFlutter() {
    var m = Process.findModuleByName('libflutter.so');
    if (!m) { console.log('[-] no libflutter'); return; }
    var syms = m.enumerateSymbols().filter(function (s) {
        return /ssl_verify_cert_chain|ssl_crypto_x509_session_verify_cert/.test(s.name);
    });
    syms.forEach(function (s) {
        console.log('[flutter] ' + s.name + ' @ ' + s.address);
        Interceptor.replace(s.address, new NativeCallback(function () {
            return 1;                          // X509_V_OK
        }, 'int', ['pointer', 'pointer']));
    });
}
hookFlutter();
```

```bash
# objection 一条命令（简化路径）
objection -g com.ctf.demo explore -s "android sslpinning disable"
# 只看能否读取证书链
objection -g com.ctf.demo explore -s "android keystore list"
```

## 五、常见坑 / 变体

- **Android 14 的系统证书目录不可写**：证书在 APEX 里，`/system` 只读，必须用 Magisk 模块或 `adb root + remount` 的测试镜像。
- **Burp 证书过期**：Burp 自带 CA 有效期有限，过期后握手失败，重新生成即可。
- **应用走 pinned 的证书指纹**：hook 返回 true 仍可能被二次校验（比如自己算哈希再比），要 hook `MessageDigest.digest`。
- **Flutter 的绕过点随版本变化**：`ssl_verify_cert_chain` 在不同 Flutter 版本可能被内联，需按 `strings` 找符号或按字节特征定位。
- **QUIC/HTTP3**：UDP 443，代理不生效，需关掉 QUIC（`adb shell settings put global force_quic_disabled 1`）。
- **证书透明度（CT）**：极少数应用校验证书是否在 CT log 里，自签证书必然失败。
- **变体**：Unity 的 `libunity` 也有自己的 TLS、WebView 的 `onReceivedSslError`、TLS 指纹伪造用 `curl-impersonate`。

## 六、参考来源

- [Android 官方 Network Security Config（user vs system CA）](https://developer.android.com/privacy-and-security/security-config)
- [OkHttp CertificatePinner 官方文档](https://github.com/square/okhttp)
- [OWASP MASTG：Android 网络拦截与 SSLPinning 绕过](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0012/)
- [mitmproxy 官方文档（证书与透明代理）](https://docs.mitmproxy.org/stable/)
- [network_security_config 与信任用户证书的配置示例](https://developer.android.com/training/articles/security-config#TrustingAdditionalCas)

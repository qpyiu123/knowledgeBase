---
title: 移动端 CTF 真题题型汇总（分类打法与解题路径）
category: mobile
tags: [mobile-ctf, taxonomy, writeup, flutter, unity, root-detect]
signals: [比赛里 mobile 分类只有一两道题, 拿到 apk 但完全不知道从哪下手, 题目描述只有一句请分析这个应用, 附件同时给了 apk 和 pcap, 应用启动就检测 root 环境, 题目分值很高但附件很小看不出考点]
difficulty: medium
source: "历年 CTF 移动安全题型统计（ACSC/强网杯/0CTF/DASCTF）/ OWASP MASTG 测试项"
tools: [jadx, apktool, frida, jadx-gui, adb, angr, unidbg]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 一打开 apk，`classes.dex` 几百 KB，`lib/` 下有多个 so。
- 应用是 Flutter/Unity/React Native 打包（`libflutter.so`、`libil2cpp.so`、`libreactnativejni.so`）。
- 题目描述极短（"分析这个 app"），附件却包含 apk + so + pcap。
- 应用一启动就闪退（root/模拟器/反调试）。
- 有输入框 + 校验，但静态搜索不到明显逻辑。
- 题目要求"给出调用序列"或"提交一段脚本"，而不是 flag 字符串。

## 二、原理

**移动 CTF 的高频考点可以归为 5 类，识别打包形态就能快速定位：**

| 类型 | 特征 | 打法 |
| --- | --- | --- |
| **Java 逻辑题** | 代码量小、无壳、方法名清晰 | jadx 静态 + 手算/脚本 |
| **Native 题** | `.so` 大、`native` 方法、JNI 注册 | IDA/unidbg + Frida |
| **加固题** | 壳特征 so、DEX 极小 | 脱壳后再静态分析 |
| **跨框架题** | Flutter/Unity/RN | 找框架符号与自定义逻辑 |
| **环境题** | 反 root/反调试/反模拟器 | 先过检测，再做题 |

**其它常见组合**：APK + 网络抓包（考协议）、APK + 固件（IoT）、APK 里藏文件（考解密链）。

## 三、操作步骤

1. **分类**：`unzip -l` 看 so 列表 → 判断是 Java/native/Flutter/Unity/加固。这一步决定后面 80% 的工作。
2. **静态扫描**：`jadx` 全量反编译，搜 `flag`、`{`、`equals`、`Cipher`、`native`、`loadLibrary`。
3. **资源扫描**：`assets/`、`res/raw/`、`META-INF/` 里的文件（常见 `enc`、`data`、`.dat`）。
4. **动态验证**：Frida 挂上打点，看关键方法的入参出参。
5. **算/解**：算法通常很短（异或、RC4、AES 固定 key），写脚本还原。
6. **收尾**：构造输入验证 flag，或补齐题目要求的调用序列。

## 四、命令 / 脚本

```bash
# 1) 打包形态一键分类
python - <<'EOF'
import zipfile
z = zipfile.ZipFile('app.apk')
names = z.namelist()
print('dex:', [n for n in names if n.endswith('.dex')])
print('so :', [n for n in names if n.endswith('.so')][:20])
markers = {'flutter': 'libflutter.so', 'unity': 'libil2cpp.so',
           'rn': 'libreactnativejni.so', 'cordova': 'assets/www',
           'cocos': 'libcocos2djs.so'}
for k, v in markers.items():
    if any(v in n for n in names):
        print('框架:', k)
print('assets 数:', sum(1 for n in names if n.startswith('assets/')))
EOF

# 2) 常见藏点
unzip -l app.apk | grep -E 'assets/|raw/|lib/' | head -30
# 3) 静态线索
jadx -d out app.apk && grep -rn "flag\|Cipher\|MessageDigest\|native " out/sources | head -20
# 4) 动态
frida -U -f com.ctf.demo -l trace.js --no-pause
```

```javascript
// 通用打点脚本：把关键 API 的调用都打出来
Java.perform(function () {
    ['java.lang.StringBuilder', 'javax.crypto.Cipher', 'java.security.MessageDigest',
     'java.util.Base64'].forEach(function (name) {
        try {
            var C = Java.use(name);
            C.$init.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    var r = ov.apply(this, arguments);
                    console.log('[' + name + '] ' + Array.prototype.join.call(arguments, ','));
                    return r;
                };
            });
        } catch (e) {}
    });
});
```

```bash
# Flutter 题：从 libapp.so 里找 Dart 字符串
strings -n 8 lib/arm64-v8a/libapp.so | grep -iE 'flag|key|http' | head -20
# Unity 题：il2cpp 元数据
python il2cppdumper.py lib/arm64-v8a/libil2cpp.so global-metadata.dat out/
# RN 题
npx react-native-decompiler -i assets/index.android.bundle -o out/
```

```python
#!/usr/bin/env python3
# 典型"异或 + 换位"题的快速还原骨架
import sys
ct = bytes.fromhex(open('cipher.hex').read().strip())
for key in range(256):
    pt = bytes(c ^ key for c in ct)
    if b'flag' in pt or b'ctf' in pt:
        print('key=%#x' % key, pt)
```

## 五、常见坑 / 变体

- **不要一上来就跑动态**：先分类，否则会在反调试上浪费大量时间。
- **`assets/` 里的加密文件**：很多题的 flag 就藏在 `assets/flag.enc`，key 在 Java 里。
- **Flutter 的字符串是 AOT 编译的**：`strings` 能找到一部分，但 Dart 对象布局需要专门工具（`flutter-reverse`/`blutter`）。
- **Unity 的 `global-metadata.dat`** 是核心，没它 `libil2cpp.so` 基本不可读。
- **加固题先过检测**：不要试图静态搜 `flag`，壳会把字符串加密。
- **多 dex**：`classes2.dex`、`classes3.dex` 里可能才是真正逻辑，jadx 要全部加载。
- **变体**：`xapk`/`apks`（split apk，需合并）、`aab`（Play 分包格式）、iOS `.ipa`（见 `ios-macho-dyld-lldb`）。

## 六、参考来源

- [OWASP MASTG：移动应用安全测试技术索引](https://mas.owasp.org/MASTG/techniques/)
- [jadx 官方仓库（多 dex 与反混淆）](https://github.com/skylot/jadx)
- [Frida 官方文档](https://frida.re/docs/home/)
- [unidbg：native 方法模拟执行](https://github.com/zhkl0228/unidbg)
- [CTF-Wiki：Reverse / Mobile 分类总览](https://ctf-wiki.org/)

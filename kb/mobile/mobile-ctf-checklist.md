---
title: 移动端 CTF 检查清单（Android / iOS 通用流程）
category: mobile
tags: [检查清单, Android, iOS, 脱壳, 动态分析, 抓包]
signals: [拿到一个 apk/ipa 不知从哪下手, 时间紧需要固定套路, 静态分析卡住, 需要判断要不要脱壳/抓包/动态调试, 队伍分工要一个 checklist]
difficulty: easy
source: "OWASP MASTG / HackTricks Mobile / CTF-Wiki Android"
tools: [jadx, apktool, Frida, objection, MobSF, adb, mitmproxy, class-dump]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.apk` / `.ipa` / `.so` / `classes.dex`，需要一个可复用的推进顺序。
- 比赛现场时间紧，需要「先做什么后做什么」避免遗漏。
- 团队分工：一人静态、一人动态，需要信息交接模板。
- 走了弯路（先脱壳结果根本不需要，或忘了看 assets）。

## 二、原理

移动端逆向的「信息金字塔」：**越上层越便宜，先穷尽再往下**。

```text
L0  文件与结构        unzip / file / aapt2 / Info.plist          （秒级）
L1  清单与资源        AndroidManifest / assets / res/raw         （分钟级）
L2  Java/dex 源码     jadx / apktool smali                       （分钟级）
L3  native so         IDA / Ghidra / JNI 注册                    （小时级）
L4  动态 Hook         Frida / objection                          （小时级）
L5  脱壳              frida-dexdump / dump.py                    （按需）
L6  网络与后端        mitmproxy / SSL pinning 绕过               （按需）
```

**90% 的移动题在 L1~L2 就能解**，先别上脱壳和 native。

## 三、checksec 判读与利用思路

### 检查清单（逐项打勾）

**A. 基本信息**

- [ ] `file` 判断格式（apk / ipa / dex / so / 加密 blob）
- [ ] 包名、版本、`launchable-activity`、`exported` 组件
- [ ] `debuggable` 是否为 true
- [ ] 权限列表（网络 / 存储 / 定位）
- [ ] 是否加固（`libjiagu.so` / `libsecmain.so` / `classes.dex` 极小）

**B. 静态资源**

- [ ] `assets/`、`res/raw/`、`META-INF/` 里有无明文/二进制 flag
- [ ] `strings` 全局扫 `flag{`、`CTF{`、`correct`
- [ ] `network_security_config.xml` 的 pin 配置
- [ ] `.so` 里 `JNI_OnLoad` 与 `Java_` 符号

**C. 代码逻辑**

- [ ] jadx 全文搜 `flag|check|verify|decrypt|key`
- [ ] 找到输入入口（EditText / Intent extra / 命令参数）
- [ ] 找到校验出口（Toast / TextView / log）
- [ ] smali 里看关键 `if`（jadx 反编译可能失真）
- [ ] native 函数注册方式（静态 `Java_` / 动态 `RegisterNatives`）

**D. 动态验证**

- [ ] 设备/模拟器可装（架构匹配）
- [ ] 能 attach Frida（root 或 debuggable）
- [ ] 记录关键函数入参与返回值
- [ ] 断点命中后取明文

**E. 网络**

- [ ] 设置代理后能否抓到请求
- [ ] 有无 SSL pinning（见对应篇）
- [ ] 响应里是否直接含 flag
- [ ] 有无请求签名（`sign`/`token`）需要逆向算法

**F. 收尾**

- [ ] flag 格式校验（是否有 `{}`、是否大小写敏感）
- [ ] 记录所有尝试与结论，便于换人接手

## 四、可直接运行的 exp 脚本

### 一键侦察（先跑这个）

```bash
#!/bin/bash
# mobile_recon.sh —— 拿到包先跑一遍，输出 L0~L2 的全部线索
set -u
T=${1:-./chall.apk}
OUT=./recon_out
mkdir -p "$OUT"

echo "== L0 文件 =="
file "$T"; ls -lh "$T"

echo "== L0 结构 =="
unzip -l "$T" | head -40
unzip -l "$T" | grep -Ei "assets/|res/raw|\.so$|\.dex$|lib/" | head -40

echo "== L1 清单（apk） =="
aapt2 dump badging "$T" 2>/dev/null | head -5
aapt2 dump xmltree --file AndroidManifest.xml "$T" 2>/dev/null \
  | grep -E "debuggable|exported|permission" | head -20

echo "== L1 资源明文 =="
unzip -o -q "$T" -d "$OUT/raw"
grep -rInaE "flag\{|ctf\{" "$OUT/raw" 2>/dev/null | head -20
strings -a "$OUT/raw" -n 6 2>/dev/null | grep -iE "flag\{|ctf\{" | head

echo "== L2 dex/java =="
jadx -q -d "$OUT/java" --show-bad-code "$T" 2>/dev/null || true
grep -rniE "flag|check|verify|decrypt|secret" "$OUT/java" --include=*.java 2>/dev/null | head -30

echo "== L3 so 线索 =="
for so in $(find "$OUT/raw" -name "*.so" 2>/dev/null); do
  echo "--- $so"
  readelf -sW --dyn-syms "$so" 2>/dev/null | grep -E "Java_|JNI_OnLoad" | head -10
  strings -a "$so" | grep -iE "flag|check|key" | head -5
done

echo "[*] 输出目录: $OUT"
```

### 动态 hook 模板（按需改类名）

```javascript
// recon_hook.js —— frida -U -f <pkg> -l recon_hook.js --no-pause
Java.perform(function () {
  // 1) 记录所有可疑方法的入参与返回
  Java.enumerateLoadedClasses({
    onMatch: function (name) {
      if (name.indexOf("com.") !== 0 && name.indexOf("cn.") !== 0) return;
      try {
        var C = Java.use(name);
        C.$ownMembers.forEach(function (m) {
          if (m.constructor.name !== "Method") return;
          if (!/check|verify|decrypt|encode|flag/i.test(m.name)) return;
          try {
            m.implementation = function () {
              var args = Array.prototype.slice.call(arguments);
              console.log(`[*] ${name}.${m.name}(${args.map(String).join(", ")})`);
              var r = m.apply(this, arguments);
              console.log(`[*]  -> ${r}`);
              return r;
            };
          } catch (e) {}
        });
      } catch (e) {}
    },
    onComplete: function () { console.log("[+] hook 安装完毕"); }
  });
});
```

### 用 MobSF 自动出报告（省时间）

```bash
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest
# 打开 http://127.0.0.1:8000 上传 apk/ipa，自动给：
#   权限、exported 组件、硬编码密钥、证书、恶意行为、字符串
```

### 一键脱壳 + 反编译（加固题才用）

```python
#!/usr/bin/env python3
# 用 frida-dexdump 脱壳后自动 jadx，一步到位
import subprocess, sys, pathlib

PKG = sys.argv[1] if len(sys.argv) > 1 else "com.example.chall"
subprocess.run(["frida-dexdump", "-U", "-f", PKG, "-d", "5"], check=False)

dexs = list(pathlib.Path(".").rglob("classes*.dex"))
print(f"[*] dump 到 {len(dexs)} 个 dex")
for d in dexs[:5]:
    out = d.with_suffix("")
    subprocess.run(["jadx", "-q", "-d", str(out), str(d)], check=False)
    print("   ->", out)
```

## 五、常见坑 / 变体

- **一上来就脱壳**：先看 L0~L2，很多题根本没加固，脱壳纯浪费时间。
- **只看 jadx 结果**：Kotlin/混淆下反编译可能丢逻辑，关键分支一定回 smali 核对。
- **忽略 assets**：`assets/flag`、`assets/data.bin` 直接就是答案，`unzip -l` 时别跳过。
- **模拟器架构不匹配**：`x86_64` 模拟器装不上只有 `arm64-v8a` so 的应用，换 ARM 镜像或真机。
- **`debuggable=false` 又无 root**：Frida attach 失败，只能重打包（并处理签名校验）。
- **iOS 未越狱**：只能重签名注入，且 `cryptid=1` 无法静态分析，优先找越狱设备。
- **flag 在服务器**：检查响应体/日志，别死磕本地算法。

## 六、参考来源

- [OWASP MASTG 总目录（Android 平台概览）](https://mas.owasp.org/MASTG/0x05a-Platform-Overview/)
- [OWASP MASTG: Android 静态分析](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0014/)
- [HackTricks: Android App Pentesting](https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting/index.html)
- [HackTricks: iOS Pentesting](https://book.hacktricks.wiki/en/mobile-pentesting/ios-pentesting/index.html)
- [CTF-Wiki: Android 逆向基本介绍](https://ctf-wiki.org/android/basic_reverse/overview/)
- [MobSF 官方文档](https://mobsf.github.io/docs/)
- [jadx 官方仓库](https://github.com/skylot/jadx)
- [Frida 官方文档](https://frida.re/docs/home/)

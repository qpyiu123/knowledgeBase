---
title: "ByteCTF 2022 mobile 系列 - Silver Droid"
category: misc
tags: ["ByteCTF", "misc", "WebView拦截", "/local_cache/ 路径", "腾讯COS POC URL", "am broadcast SET_FLAG"]
signals: ["ByteCTF 2022", "WebView拦截", "/local_cache/ 路径", "腾讯COS POC URL", "am broadcast SET_FLAG", "FlagReceiver exported=false", "root bypass", "FileInputStream", ".myqcloud.com白名单", "misc_unknown", "ByteCTF", "Silver", "Droid", "COS"]
difficulty: hard
source: "https://www.ctfiot.com/87778.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ByteCTF 2022 mobile 系列 - Silver Droid

> 赛事：ByteCTF 2022 | 方向：misc | 难度：hard | 工具：Python

## 一句话总结

ByteCTF 2022 Silver Droid — 攻击者提供腾讯 COS POC URL + 模拟器启动 + am broadcast SET_FLAG 走 root 旁路 exported + MainActivity WebView + shouldOverrideUrlLoading 验证 .myqcloud.com + shouldInterceptRequest 拦截 /local_cache/ cacheDir 文件。

## 攻击链

1. 攻击者提供 https://...cos.ap-nanjing.myqcloud.com/.../poc.apk
2. server.py 启动 emulator pixel_xl_api_30 + adb install poc.apk
3. am broadcast -W -a com.wuhengctf.SET_FLAG -n com.bytectf.silverdroid/.FlagReceiver -e flag 'flag{...}
4. root 状态绕过 exported=false 限制
5. am start -W -n com.bytectf.silverdroid/.MainActivity -d "https://...cos...
6. MainActivity: getIntent().getData() 拿 URL
7. WebView loadUrl("https://bytectf-...myqcloud.com/jump.html?url=" + uri0)
8. shouldOverrideUrlLoading 拦截: scheme=https + host .myqcloud.com 结尾返回 false 不拦截
9. shouldInterceptRequest: 拦截 /local_cache/ 路径, 读 cacheDir 文件返回

## 关键 payload

```
cos.ap-nanjing.myqcloud.com URL / am broadcast -e flag / root bypass exported / /local_cache/ cacheDir / shouldInterceptRequest
```

## 经验教训

WebView shouldOverrideUrlLoading + shouldInterceptRequest 是 Android 经典链;root 状态下 exported=false 可被 am broadcast bypass;cos.ap-nanjing.myqcloud.com 白名单是 bypass 套路。

## 标签

WebView拦截、/local_cache/ 路径、腾讯COS POC URL、am broadcast SET_FLAG、FlagReceiver exported=false、root bypass、FileInputStream、.myqcloud.com白名单、byte_unzip、run.sh、avdmanager、emulator、WebViewClient.shouldInterceptRequest

## 参考来源

- https://www.ctfiot.com/87778.html
- 原文件：ByteCTF2022_mobile系列.full.md

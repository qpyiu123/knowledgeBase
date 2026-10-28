---
title: "Java安全基础"
category: web
tags: [licensed chinese reference]
signals: [Java安全基础, Java, PHP, Python]
difficulty: medium
source: "https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/java_basic.md"
tools: []
origin: imported
origin_id: helloctf-c1f9cdb6dfac5d
origin_sha256: 3292afd2b1d0a5697884ddb5442b5c017ac606a4785b65ac47766d6bbffa5e05
origin_event: ""
origin_kind: licensed_chinese_reference
license: "CC-BY-SA-4.0"
updated: 2026-10-23
---
# Java安全基础

> 来源：https://github.com/ProbiusOfficial/Hello-CTF/blob/8e9d6396a0d1ccc1f606810d575d1abb3dd567de/docs/hc-web/java_basic.md

---
comments: true
---

# Java安全基础

本章是 Java Web 安全的入门铺垫，定位是"够用即止"：不追求把 Java 语言学全，而是把后面 **Java 反序列化** 与 **Java 代码审计** 必需的几个核心概念讲透——运行基础、反射、类加载、动态代理、序列化机制。如果你已经会 PHP 或 Python，可以对照着读，很多概念是相通的（可以先翻翻本书的「PHP基础」和「PHP 序列化及反序列化基础」章节找找感觉）。

## Java 运行基础速览

### JVM 与字节码

Java 的口号是"一次编译，到处运行"。与 PHP 这种解释执行的脚本语言不同，Java 代码先由编译器 `javac` 编译成 **字节码**（`.class` 文件），再由 **JVM（Java 虚拟机）** 加载并执行：


对安全的意义有两点：

- 攻击载荷最终也是 `.class` 字节码。只要能想办法让目标 JVM 加载我们构造的类，就能执行任意代码。
- `.class` 文件可以被反编译（如用 `jd-gui`、`javap -c`），做 Java 代码审计时经常直接审 jar 包反编译出来的源码。

### 类与对象

Java 是纯面向对象语言，一切代码都写在 **类（class）** 里。类比 PHP：`class` 定义模板，`new` 出对象，方法、字段的概念几乎一样：


需要记住的区别：Java 是强类型语言，每个变量都要声明类型；方法的访问权限由 `public / private / protected` 控制，但如后文所述，**反射可以无视这些权限**，这正是很多漏洞利用的基础。

### 包与 classpath

类多了以后用 **包（package）** 组织，包名对应目录结构。比如 `package com.example;` 的类编译后放在 `com/example/` 目录下，全限定类名是 `com.example.User`。

JVM 找类靠 **classpath**（类路径），运行时用 `-cp` 指定：


审计 Java Web 应用时，`WEB-INF/lib/` 下的 jar 包就是应用的 classpath 组成部分——目标依赖了哪些第三方库（如 Commons Collections、Fastjson），决定了反序列化利用链能用什么"零件"。

## 反射

### 什么是反射

正常情况下，调用一个方法需要"写死"类名和方法名，编译时就确定了。而 **反射（Reflection）** 允许程序在 **运行时** 通过字符串形式的类名、方法名来加载类、创建对象、调用方法。这相当于 Java 世界里类似于 PHP 中可变函数 `$func()` 和 `eval` 的能力——只要攻击者能控制反射调用的类名和方法名，就等于控制了程序执行流。

### 核心 API 与最小示例

反射的三板斧：`Class.forName()` 拿类对象，`getMethod()` 拿方法，`invoke()` 调用：


编译运行，就能看到 `id` 命令的输出。CTF 里大量 Java 题目的最终一步，本质都是走到 `Runtime.exec()` 或 `ProcessBuilder` 执行命令，区别只在"怎么走到"。

几个补充要点：

- `clazz.getDeclaredConstructor().newInstance()` 可以通过构造方法实例化对象；
- 私有方法/字段也能用反射访问：拿到 `getDeclaredMethod` 后调用 `m.setAccessible(true)` 即可绕过 `private` 检查，Java 代码审计时看到 `setAccessible` 要格外留意；
- `Class.forName(name)` 除了返回 `Class` 对象，还会 **触发该类的初始化**（执行静态代码块 `static { ... }`），这个特性在一些利用链里被直接拿来触发代码执行。

## 类加载机制

### ClassLoader

JVM 不会一次性加载所有类，而是在类第一次被使用时，由 **类加载器（ClassLoader）** 把 `.class` 字节码读进来。类加载是分层委派的：

- `Bootstrap ClassLoader`：加载 JDK 核心类（`java.lang.*` 等）；
- `Extension / Platform ClassLoader`：加载扩展类；
- `App ClassLoader`：加载 classpath 上的应用类；
- 自定义 `ClassLoader`：开发者可以继承 `ClassLoader`，重写 `findClass()`，从 **任意来源** 读取字节码并调用 `defineClass()` 把它变成一个真正的类。

最后一点是安全关键：**类的来源不一定是本地文件**。

### URLClassLoader 加载远程类

`URLClassLoader` 是 JDK 自带的 ClassLoader，可以从指定 URL（包括 HTTP 地址）加载类。这意味着只要目标应用存在"用 `URLClassLoader` 加载用户可控地址的类"的逻辑，攻击者就能让目标加载自己服务器上的恶意类：

攻击者先编写恶意类并编译：


目标侧的加载代码（漏洞点）形如：


远程类加载是 Java 漏洞利用的常备手段：fastjson、JNDI 注入（如 Log4Shell）等著名漏洞的最终效果，很多都归结为"让目标 JVM 从攻击者控制的地址加载一个类"。它和 PHP 的远程文件包含（见「文件包含」章节）在思路上完全同构。

## 动态代理

### 什么是动态代理

代理就是"套壳"：不直接调目标对象，而是先经过一个中间层，在中间层里插入额外逻辑。Java 的 **JDK 动态代理** 可以在运行时为任意 **接口** 生成代理对象，所有对代理对象方法的调用，都会被统一转发到一个 `InvocationHandler.invoke()` 里：


可以看到：调用 `proxy.say()` 时，真正执行的是我们写的 `invoke()`。方法调用被"劫持"了。

### 它在反序列化链里的作用

为什么讲这个？因为 Java 反序列化利用链（Gadget Chain）里，动态代理是常用的"转接头"。一条链的起点往往是"反序列化时自动调用了某个对象的某个方法"，而终点是命令执行，中间需要若干类接力传递调用。动态代理可以把 **任意接口方法调用** 转发到 `InvocationHandler.invoke()`，于是链的作者会找一个"自身可序列化、且 `invoke()` 里会继续调别的危险方法"的 Handler 类（经典如 Commons Collections 链里的 `AnnotationInvocationHandler`），用代理对象把链的各环节串起来。

读链的工具（如 ysoserial）生成的 payload 里经常能看到代理类（`$Proxy0` 之类）的身影，到那时你只需记得：代理对象收到任何方法调用，都会进它 Handler 的 `invoke()`。

## 序列化机制

### Serializable 与 ObjectOutputStream

Java 原生序列化：类实现 `java.io.Serializable` 接口（空接口，仅作标记）后，对象就能被 `ObjectOutputStream.writeObject()` 转成字节流，再由 `ObjectInputStream.readObject()` 还原：


与 PHP 的 `serialize()` 产出可读字符串不同，Java 序列化产物是 **二进制字节流**，固定以魔数 `AC ED 00 05` 开头（Base64 编码后是 `rO0AB`，在流量或代码里看到这个特征基本可以断定是 Java 原生序列化数据）。

### readObject / writeObject 魔术方法

类可以自定义一对私有方法来介入序列化过程，地位相当于 PHP 的 `__wakeup()` / `__sleep()`：


**关键结论：反序列化一个对象时，如果它的类定义了 `readObject()`，这个方法会被自动执行。** 只要攻击者能控制反序列化的输入，而 classpath 上又存在某个类的 `readObject()` 里做了危险操作（或能一路调过去），就形成了反序列化漏洞。审计 Java 代码时，`readObject(` 和 `readObject()` 的调用点是第一优先级搜索目标。

### transient 关键字

被 `transient` 修饰的字段 **不参与序列化**：


反序列化还原后，`password` 是类型的默认值（对象为 `null`，数字为 `0`）。在利用链构造中这也是常客：有些字段类型本身不可序列化，作者会用 `transient` 跳过去，再在 `readObject()` 里手工重建。

## 典型例题：一道最基础的 Java 反序列化题

题目（常见于各 CTF 的 Java 入门题）：给定一个 Web 接口，接收 Base64 编码的数据后反序列化，源码如下：


完整解题过程：

**第一步：定位漏洞点。** 看到 `readObject()` 处理外部输入，且 classpath 里的 `Evil` 类在 `readObject()` 中执行 `this.cmd`——只要我们能控制 `cmd` 字段，反序列化瞬间就会触发命令执行。思路和 PHP 反序列化找 `__wakeup()` / `__destruct()` 完全一致。

**第二步：本地编写 payload 生成器。** 由于序列化数据是二进制且包含类的结构信息，最稳的办法是用 Java 自己生成，而不是手拼字节：


注意：生成 payload 的类名、包名、字段必须和题目环境一致，否则反序列化时找不到类会抛异常。

**第三步：发送并验证。** 把输出的 Base64 字符串（开头应为 `rO0AB`）发给接口：


目标反序列化 → 自动进入 `Evil.readObject()` → `exec(cmd)` 执行，拿到反弹 shell，读 flag 收工。

真实比赛中题目很少直接把 `exec` 写在 `readObject` 里，而是依赖第三方库中一串类的接力（Gadget Chain），用 ysoserial 等工具生成——但无论链多长，**入口永远是 `readObject()`，原理永远离不开本章讲的反射、类加载、动态代理这几块积木**。后续的 Java 反序列化章节会专门讲链的构造，本章打的地基到这里就够用了。

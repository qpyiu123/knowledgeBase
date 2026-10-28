---
title: "Under Construction：不同技术栈解析重复参数"
category: web
tags: [wp prose translation]
signals: [Under Construction：不同技术栈解析重复参数, PHP]
difficulty: medium
source: "https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/web-under-construction/solution/README.md"
tools: []
origin: imported
origin_id: gctf-2023-web-under-construction
origin_sha256: 156f476302b0125d89b883f3533e2b9808232f162e07c05ee2395ac6e1e191e9
origin_event: ""
origin_kind: wp_prose_translation
license: "Apache-2.0"
updated: 2026-10-23
---
# Under Construction：不同技术栈解析重复参数

> 来源：https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/web-under-construction/solution/README.md

# Under Construction 题解

这道题基于两个使用不同技术栈运行的 Web 应用。

## 注册和登录

两个应用都支持用户注册和登录。Flask 应用的注册入口任何人都可访问，但 PHP 应用的注册入口受秘密令牌保护，令牌需要放在 HTTP 头中。Flask 与 PHP 应用共享该令牌，外部无法取得。

Flask 有一种机制，会把注册请求的原始查询参数转发给 PHP，以确保 Flask 创建的所有账号也都存在于 PHP。因此，Flask 注册的账号也可以用于 PHP 登录。

## 不同用户等级，也就是权限级别

注册时可以选择等级。Flask 识别四种等级：blue、red、green、gold。前三种是低权限，gold 是高权限。目标是在 PHP 应用中创建一个凭据已知的 gold 等级账号；达到该条件便能得到 flag。

### 对 gold 等级的限制

Flask 检查账号必须创建在某个低权限等级上。PHP 虽然缺少这项检查，但注册请求需要秘密 HTTP 头令牌，因此不能直接从外部向 PHP 提交经过认证的 gold 注册请求。

## 绕过与题解

需要向 Flask 的注册入口发送请求，在 Flask 创建低权限账号以满足其检查；该请求经 Flask 转发给 PHP 后，却应在 PHP 中创建高权限账号，因为 PHP 没有对应的权限等级检查。

实现这一点利用了原始 HTTP 查询串被转发的事实，以及两端对重复参数的不同解释。

例如，`a=1&a=2` 在题目使用的 Flask 和 Apache HTTP Server 上的 PHP 中含义不同：Flask 把参数解释为第一次出现的值 1，PHP 则取最后一次出现的值 2。

因此，形如 `username=username&password=password&tier=blue&tier=gold` 的查询，会在 Flask 中创建低权限账号，在 PHP 中创建高权限账号。这种方法通常称为 HTTP 参数污染。

有许多工具可用来发送这样的 POST 请求，原文给出了一个 curl 示例：

〔原文代码块 1：请求代码未收录，也没有执行。〕

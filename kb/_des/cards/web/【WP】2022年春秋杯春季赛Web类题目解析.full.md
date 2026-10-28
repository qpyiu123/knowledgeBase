---
title: "【WP】2022年春秋杯春季赛 Web 类题目解析"
category: web
tags: ["春秋杯", "web", "Swoole", "EasySwoole", "gopher-protocol", "Redis-SERIALIZE_PHP"]
signals: ["春秋杯 2022", "Swoole", "EasySwoole", "gopher-protocol", "Redis-SERIALIZE_PHP", "UploadFile-destruct", "Prophecy-chain", "PHPUnit-MockObject-MockTrait-generate-eval", "swoole-RCE", "deserialize", "Web", "Redis", "gopher", "PHPUnit"]
difficulty: medium
source: "https://www.ctfiot.com/42191.html"
tools: ["PHP", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2022年春秋杯春季赛 Web 类题目解析

> 赛事：春秋杯 2022 | 方向：web | 难度：medium | 工具：PHP、curl

## 一句话总结

2022 春秋杯春季赛 Web 2 题 WP，EasySwoole + Redis 反序列化 + gopher 注入 + PHPUnit Mock 链 RCE。

## 攻击链

1. 1. Redis SERIALIZE_PHP 配置 + 爬虫 curl gopher 注入序列化数据 /2. UploadFile.__destruct → $this->stream->close 触发 __call/3. Prophecy ObjectProphecy 链 + LazyDouble + Doubler + PHPUnitFrameworkMockObjectMockTrait generate → eval RCE/4. Swoole 框架 system 无回显 → 抛异常回显

## 关键 payload

```
EasySwooleHttpMessageUploadFile → ProphecyProphecyObjectProphecy → ProphecyDoublerLazyDouble → PHPUnitFrameworkMockObjectMockTrait generate → eval
```

## 经验教训

EasySwoole 默认 SERIALIZE_PHP 配置可被 gopher 注入利用；Swoole framework system() 无回显需用异常方式；Prophecy + PHPUnit MockObject 是 PHP 反序列化常见 gadget 库。

## 标签

Swoole、EasySwoole、gopher-protocol、Redis-SERIALIZE_PHP、UploadFile-destruct、Prophecy-chain、PHPUnit-MockObject-MockTrait-generate-eval、swoole-RCE

## 参考来源

- https://www.ctfiot.com/42191.html
- 原文件：【WP】2022年春秋杯春季赛Web类题目解析.full.md

---
title: "2023 idekCTF WriteUp"
category: web
tags: ["idekCTF 2023", "web", "pydash原型链污染", "Jinja2全局变量劫持", "urllib拆fragment", "flask_unsign伪造session"]
signals: ["idekCTF 2023 2023", "pydash原型链污染", "Jinja2全局变量劫持", "urllib拆fragment", "flask_unsign伪造session", "Go_bufio_Race", "php_filter_chain", "nginx缓存绕过", "web_unknown", "Web", "pydash", "urllib", "fragment", "flask"]
difficulty: hard
source: "https://www.ctfiot.com/92876.html"
tools: ["Flask", "Go", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 idekCTF WriteUp

> 赛事：idekCTF 2023 2023 | 方向：web | 难度：hard | 工具：Flask、Go、Python

## 一句话总结

5 道高质量 Web：pydash 链污染+urllib fragment 拆分+flask session 伪+Go bufio 越界+php filter chain 预置 FREE。

## 攻击链

1. TaskManager: pydash.set_ 走 __init__.__globals__ 链污染 app.env / jinja_env.globals.value
2. 改 jinja_env.variable_start_string/[[:成 '']:，闭合 jinja 模板表达式
3. GET /../../usr/local/lib/python3.8/turtle.py 触发 SSTF 读 /flag-*.txt
4. Subscription: requests/urllib3 _splittag 用 %23 切 fragment 拆分 URL
5. 代理层 http://proxy/proxy/file:///flag.txt%23/../../../static/a 双层 URL 穿越
6. free_flag_news: 注册/登录/上传 zip 触发 unzip 软链读 /tmp/server.log
7. log 时间戳 + config.py SECRET_OFFSET 还原 random.seed
8. flask_unsign.sign 伪造 session.admin=True 拿 /flag
9. just-read-it: Go bufio.NewReader 在 size>=100 包裹，套娃调用 Read 移动 reader 指针 32 字节对齐
10. Order=32 + bufio 边界读 32 字节比较 password
11. idek newsPHPaper: php://filter 多重 iconv 链预置 FREE 头部绕过 strpos === 0 检测

## 关键 payload

```
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|...|convert.base64-decode/resource=flag
```

## 经验教训

pydash.set_ 走 Python 属性路径可污染 Flask jinja_env；urllib _splittag 用 %23 切 URL 绕过 SSRF 检查；flask SECRET_KEY 靠 random.seed(time+offset) 可还原；Go bufio 包装是经典套娃越界；php://filter iconv 链可前置任意字符串。

## 标签

pydash原型链污染、Jinja2全局变量劫持、urllib拆fragment、flask_unsign伪造session、Go_bufio_Race、php_filter_chain、nginx缓存绕过

## 参考来源

- https://www.ctfiot.com/92876.html
- 原文件：2023IdekCTFWriteup.full.md

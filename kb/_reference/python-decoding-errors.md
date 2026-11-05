---
title: Python 解码与正则排错：Base64、JSON、捕获组和替换字符串
category: misc
kind: tutorial
tags: [Python, Base64, JSON, 正则, 排错]
signals: [Incorrect padding, 补等号, 长度余1, JSONDecodeError位置, findall元组, bad escape, 替换字符串Windows路径]
difficulty: easy
source: kb/_reference/python39/base64.md, kb/_reference/python39/json.md, kb/_reference/python39/re.md
tools: [python]
updated: 2026-11-05
license: 原创说明与示例；依据 Python 3.9 PSF 文档，许可见 licenses/python-3.9-license.html
---

## Base64：Incorrect padding 与非法字符

先核对是标准 Base64 还是 URL-safe 字母表，保留原始输入。编码器可能省略尾部等号；若确认是这种格式，可按长度补齐。长度除以 4 余 1 的有效字符序列不完整，补等号无法修复。`validate=True` 会拒绝字母表之外的字符，默认值则会在检查填充前丢弃这些字符。

```python
import base64
import binascii

s = b'Zg'  # 已确认是省略等号的标准 Base64
assert base64.b64decode(s + b'=' * (-len(s) % 4), validate=True) == b'f'
assert base64.b64decode(b'Z!g==') == b'f'
try:
    base64.b64decode(b'Z!g==', validate=True)
except binascii.Error:
    pass
else:
    raise AssertionError('非法字符应报错')
try:
    base64.b64decode(b'A===', validate=True)
except binascii.Error:
    pass
else:
    raise AssertionError('余 1 的输入无法补齐')
assert base64.urlsafe_b64decode(b'-_8=') == b'\xfb\xff'
```

参数和异常全文：[库内 base64 文档](python39/base64.md)，小节 `base64.b64decode`。

## JSONDecodeError：用 lineno、colno、pos 定位

`json.loads` 读取 JSON 文本，`json.load` 读取文件对象。JSON 键使用双引号；单引号、尾随逗号、额外文本应回查原始数据。错误对象的行、列从 1 开始，字符索引 pos 从 0 开始。

```python
import json

assert json.loads('{"ok": true}') == {'ok': True}
try:
    json.loads('{"ok": }')
except json.JSONDecodeError as error:
    assert (error.lineno, error.colno, error.pos) == (1, 8, 7)
    assert error.doc[error.pos] == '}'
else:
    raise AssertionError('缺少值应报错')
```

错误文本可能随 Python 版本改变；定位字段与原始字符一起看。全文见 [库内 json 文档](python39/json.md) 的 `json.loads`、`JSONDecodeError`。

## re.findall：捕获组改变返回形状

没有捕获组时返回完整匹配字符串；一个组返回该组的字符串；多个组返回元组列表。只想分组、不想改变返回值时使用 `(?:...)`。

```python
import re

text = 'x=12 y=34'
assert re.findall(r'\w+=\d+', text) == ['x=12', 'y=34']
assert re.findall(r'(\w+)=\d+', text) == ['x', 'y']
assert re.findall(r'(\w+)=(\d+)', text) == [('x', '12'), ('y', '34')]
assert re.findall(r'(?:\w+)=\d+', text) == ['x=12', 'y=34']
```

## re.sub：Windows 路径触发 bad escape

原始字符串只处理 Python 字面量这一层。`re.sub` 的替换字符串还会解析反斜杠转义与组引用。要把动态字符串原样插入，用回调函数返回字符串；需要引用组时用 `\g<1>`，避免 `\20` 被读成第 20 组。

```python
import re

replacement = r'C:\Users\ctf'
assert re.sub('PATH', lambda match: replacement, 'PATH') == replacement
assert re.sub(r'(\d+)', r'\g<1>0', '12') == '120'
```

全文见 [库内 re 文档](python39/re.md) 的 `re.findall`、`re.sub`。本页示例使用标准库；基于 Python 3.9 文档整理，在当前独立 Python 与开发环境运行，具体结果记入项目 R4 记录。文档许可见项目 `licenses/python-3.9-license.html`，原文来源链接保留在三篇全文顶部。

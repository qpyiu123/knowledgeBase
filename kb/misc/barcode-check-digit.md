---
title: EAN-13 条码校验位速查
category: misc
tags: [barcode, ean13, 校验位, GS1]
signals: [只有 13 位数字的条码, EAN-13 末位校验失败, 条码数字抄错, GTIN 校验位]
difficulty: easy
source: https://gs1.org.sg/check-digit-calculator/
tools: [python]
updated: 2026-11-05
---

## 识别信号

只有 13 位数字的条码，或 EAN-13 末位校验失败时，先核对抄写结果。
校验通过后，再使用条码阅读器检查对应的图像和数据。

## 校验方法

从左到右，前 12 位数字依次乘以 1、3、1、3，重复六次。
设这些乘积的和为 s，末位应为 `(10 - s % 10) % 10`。

```python
def valid_ean13(text):
    if len(text) != 13 or any(c not in '0123456789' for c in text):
        return False
    total = sum(int(c) * (1 if i % 2 == 0 else 3)
                for i, c in enumerate(text[:12]))
    return int(text[-1]) == (10 - total % 10) % 10

assert valid_ean13('6291041500213')
assert not valid_ean13('6291041500215')
```

## 来源

[GS1 Singapore：GTIN 校验位计算示例](https://gs1.org.sg/check-digit-calculator/)。
本页整理校验方法，未收录条码图像解码器。
